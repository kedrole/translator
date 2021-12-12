from . import search, unique, yandex_translate
from .models import Article, ArticleItem, ArticleImage, ListPage, Log
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction

from django.db.models import Q

from PIL import Image
import base64
import requests
from io import BytesIO

from celery import shared_task


def process_stage_with_lock_and_try(f_processing, article, stage_name):
    def set_locked_by_autotask(article):
        article.locked_by_autotask = True
        article.save()

    def unset_locked_by_autotask(article):
        article.locked_by_autotask = False
        article.save()

    if article.locked_by_autotask:
        log("Обработка заблокирована процессом, process stage: " + stage_name + ": " + str(e), article)
        return

    try:
        set_locked_by_autotask(article)
        f_processing(article)
    except Exception as e:
        article.status = 'Error'
        article.save()
        log("Ошибка, " + stage_name + ": " + str(e), article)
    finally:
        print("Здесь должен быть True: " + str(article.locked_by_autotask))
        unset_locked_by_autotask(article)
        print("Здесь должен быть False: " + str(article.locked_by_autotask))

@shared_task
def STAGE_add_artices_from_articlelistpages_to_parsing_queue():
    def add_article_or_skip():
        href = elem['href']
        title = elem['title']
        if Article.objects.filter(original_page_href = href).exists():
            print("Статья " + href + " уже в БД")
        else:
            article = Article(original_page_href=href, list_page=list_page, title=title, status='Processing', stage='Parsing')
            article.save()

            log("Cтатья добавлена в очередь на пасинг: " + href, article)

    query_list_pages_in_work_not_checked = Q(last_checked__isnull=True, in_work=True)
    query_list_pages_in_work_not_checked_long_time = Q(last_checked__lte=(datetime.now() - timedelta(hours=10)), in_work=True)

    list_pages_needed_checking = ListPage.objects.filter(query_list_pages_in_work_not_checked | query_list_pages_in_work_not_checked_long_time)
    print("Всего: " + str(len(list_pages_needed_checking)))
    
    for list_page in list_pages_needed_checking:
        articles_hrefs_list = search.ParserListArticlesPage(list_page).get_items()

        for elem in articles_hrefs_list:
            add_article_or_skip()

        list_page.last_checked = datetime.now()
        list_page.save()

@shared_task
def STAGE_parse_articles_with_stage_parsing():
    def _():
        articles_with_stage_parsing = Article.objects.filter(status='Processing', stage="Parsing")
        print("Со статусом парсинг: " + str(len(articles_with_stage_parsing)))
        for article in articles_with_stage_parsing:
            if article.accepted_on_parsing_stage:
                process_stage_with_lock_and_try(f_processing=parse_article, article=article, stage_name="parsing article")

    def parse_article(article):
        def _():
            with transaction.atomic():
                article.articleitem_set.all().delete()

                print("_______________________________")
                print("Контент: " + article.original_page_href)
                (title, content_blocks) = get_translate_content_and_images_src(article)

                # Установить заголовок в отдельную переменную и в первый article_item
                article.title = title
                article_item = ArticleItem(article=article, tag='title', type='Заголовок', original=title, original_text=title, translation='')
                article_item.save()

                for item in content_blocks:
                    article_item = ArticleItem(article=article, tag=item['tag'], type=get_type_name(item['tag']), original=item['original'], original_text=item['original'], translation='')

                    # В случае если article_item - изображение
                    if 'src' in item:
                        # Если адрес изображения не начинается с http, пропускаем
                        if not item['src'].startswith('http'):
                            log("Пропуск изображения с src = " + item['src'], article)
                            continue

                        article_item.type = 'Изображение'

                        article_image = ArticleImage(article=article, src=item['src'], base64_original=get_base64_from_img_src(item['src']))
                        article_image.save()

                        article_item.article_image = article_image

                    article_item.save()

                article.stage = get_next_stage(article)
                article.save()
                log("Проведен парсинг статьи: " + article.original_page_href, article)

        def get_translate_content_and_images_src(article):
            parser = search.ParserArticlePage()

            print("start get_page")
            page = parser.get_page(article.original_page_href)

            print("start get_content")
            (title, content_blocks) = parser.get_content_from_article(article, page)

            return (title, content_blocks)

        def get_base64_from_img_src(src):
            try:
                im = Image.open(requests.get(src, stream=True).raw)

                output = BytesIO()
                im.save(output, format='JPEG')
                im_data = output.getvalue()

                image_data = base64.b64encode(im_data)
                if not isinstance(image_data, str):
                    # Python 3, decode from bytes to string
                    image_data = image_data.decode()
                data_url = 'data:image/jpg;base64,' + image_data
                return data_url
            except:
                return ""

        def get_type_name(tag_name):
            type_name = 'Не определен'
            if tag_name in ['p']:
                type_name = 'Абзац'
            if tag_name in ['li']:
                type_name = 'В списке'
            elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10']:
                type_name = 'Подзаголовок'
            elif tag_name in ['img']:
                type_name = 'Изображение'
            return type_name
        _()
    _()

@shared_task
def STAGE_get_uniquedata_articles_with_stage_ChekingOriginalUnique_and_autoreject_if_needed():
    def _():
        articles_with_status_checking = Article.objects.filter(status='Processing', stage="Checking original unique")
        print("Со статусом Checking original unique: " + str(len(articles_with_status_checking)))

        for article in articles_with_status_checking:
            process_stage_with_lock_and_try(f_processing=check_article_original_unique_or_send_to_checking, article=article, stage_name="checking original unique")

    def check_article_original_unique_or_send_to_checking(article):
        def _():
            if settings.SKIP_CHEKING_ORIGINAL_UNIQUE:
                log("SKIP_CHEKING_ORIGINAL_UNIQUE", article)
                article.stage = get_next_stage(article)
            else:
                if article.original_unique_check_uid == "":
                    send_article_to_unuque_checking_original(article)
                else:
                    if get_unuque_result_original(article):
                        if rejecting_article_needed_by_original(article) and settings.AUTOREJECTING_ENABLED:
                            log("Статья имеет уникальность ниже предельного значения. Установка статуса Rejected Auto", article)
                            article.status = 'Rejected Auto'
                        else:
                            article.stage = get_next_stage(article)
            article.save()

        def send_article_to_unuque_checking_original(article):
            text = "\n".join([item.original for item in article.articleitem_set.all()])

            # Divide by spaces or commas
            exceptdomain = article.list_page.site.domain_name
                    
            result = unique.UniqueCheck().send_text_and_get_uid(text, exceptdomain)
            if result["status"] == "error":
                article.status = 'Error'
                log("Ошибка при отправке текста на проверку уникальности: " + str(result["message"]), article)
            else:
                article.original_unique_check_uid = result["uid"]
                log("Текст отправлен в очередь на проверку уникальности: " + str(result["uid"]), article)

        def get_unuque_result_original(article):
            print("Сбор результатов проверки уникальности")
            result = unique.UniqueCheck().check_result(article.original_unique_check_uid)
            if result["status"] == "error":
                article.status = 'Error'
                log("Ошибка при проверке текста на уникальность: " + str(result["message"]), article)
            elif result["status"] == "not-checked":
                log("Попытка получения данных уникальности. Текст еще не проверен: " + str(result["message"]), article)
            else:
                article.original_unique_percent = result["result"]["unique"]
                article.original_unique_urls = result["result"]["urls"]
                article.original_unique_date_check = datetime.strptime(result["result"]["date_check"], "%d.%m.%Y %H:%M:%S")

                log("Данные по уникальности текста получены: " + str(result["result"]), article)
                return True

        def rejecting_article_needed_by_original(article):
            if article.original_unique_percent < 10:
                return True
            return False

        _()
    _()

@shared_task
def STAGE_get_uniquedata_articles_with_stage_CheckingTranslationUnique_and_autoreject_if_needed():
    def _():
        articles_with_status_CheckingTranslationUnique = Article.objects.filter(status='Processing', stage="Checking translation unique")
        print("Со статусом Checking Translation Unique: " + str(len(articles_with_status_CheckingTranslationUnique)))

        for article in articles_with_status_CheckingTranslationUnique:
            process_stage_with_lock_and_try(f_processing=check_article_translation_unique_or_send_to_checking, article=article, stage_name="checking translation unique")

    def check_article_translation_unique_or_send_to_checking(article):
        def _():
            if settings.SKIP_CHEKING_TRANSLATION_UNIQUE:
                log("SKIP_CHEKING_TRANSLATION_UNIQUE", article)
                article.stage = get_next_stage(article)
            else:
                if article.translation_unique_check_uid == "":
                    send_article_to_unuque_checking_translation(article)
                else:
                    if get_unuque_result_translation(article):
                        if rejecting_article_needed_by_translation(article) and settings.AUTOREJECTING_ENABLED:
                            log("Статья имеет уникальность ниже предельного значения. Установка статуса Rejected Auto", article)
                            article.status = 'Rejected Auto'
                        else:
                            article.stage = get_next_stage(article)

            article.save()

        def send_article_to_unuque_checking_translation(article):
            text = "\n".join([item.translation for item in article.articleitem_set.all()])

            # Divide by spaces or commas
            exceptdomain = article.list_page.site.domain_name
            
            result = unique.UniqueCheck().send_text_and_get_uid(text, exceptdomain)
            if result["status"] == "error":
                article.status = 'Error'
                log("Ошибка при отправке текста на проверку уникальности: " + str(result["message"]), article)
            else:
                article.translation_unique_check_uid = result["uid"]
                log("Текст отправлен в очередь на проверку уникальности: " + str(result["uid"]), article)

        def get_unuque_result_translation(article):
            print("Сбор результатов проверки уникальности")
            result = unique.UniqueCheck().check_result(article.translation_unique_check_uid)
            if result["status"] == "error":
                article.status = 'Error'
                log("Ошибка при проверке текста на уникальность: " + str(result["message"]), article)
            elif result["status"] == "not-checked":
                log("Попытка получения данных уникальности. Текст еще не проверен: " + str(result["message"]), article)
            else:
                article.translation_unique_percent = result["result"]["unique"]
                article.translation_unique_urls = result["result"]["urls"]
                article.translation_unique_date_check = datetime.strptime(result["result"]["date_check"], "%d.%m.%Y %H:%M:%S")

                log("Данные по уникальности текста получены: " + str(result["result"]), article)
                return True
                
        def rejecting_article_needed_by_translation(article):
            if article.original_unique_percent < 10:
                return True
            return False

        _()

@shared_task
def STAGE_get_translation_articles_with_stage_autotranslating():
    def _():
        articles_with_status_autotranslating = Article.objects.filter(status='Processing', stage="Auto Translating")
        print("Со статусом Auto Translating: " + str(len(articles_with_status_autotranslating)))

        for article in articles_with_status_autotranslating:
            process_stage_with_lock_and_try(f_processing=get_article_translation_or_skip, article=article, stage_name="checking translation unique")

    def get_article_translation_or_skip(article):
        def get_article_translation(article):
            articleitem_set = article.articleitem_set.all()

            original_list = [item.original for item in articleitem_set]

            (status, result) = yandex_translate.YandexTranslate().get_translation_list(original_list)
            if status == "error":
                article.status = 'Error'
                log("Ошибка при получении перевода текста: " + str(result), article)
            elif status == "success":
                if len(articleitem_set) != len(result):
                    log("Длина массива оригинальных фрагментов не равна длине массива переведенных фрагментов. " + str(len(articleitem_set)) + " != " + str(len(translated_items)), article)
                    article.status = 'Error'
                else:
                    with transaction.atomic():
                        for idx, articleitem in enumerate(articleitem_set):
                            articleitem.translation = result[idx]
                            articleitem.save()
                    log("Перевод статьи загружен", article)
                    article.stage = get_next_stage(article)

        if settings.DO_NOT_TRANSLATE_ARTICLES:
            log("SKIP_TRANSLATING_ARTICLE", article)
            article.stage = get_next_stage(article)
        else:
            get_article_translation(article)
        article.save()

def log(text, article):
    print(str(article.id) + ": " + text)
    Log(article=article, text=text).save()

def get_next_stage(article):
    stages_list = [stage for (stage, descr) in Article._meta.get_field('stage').choices]
    if article.stage == stages_list[-1]:
        return article.stage

    next_stage = stages_list[stages_list.index(article.stage) + 1]
    return next_stage