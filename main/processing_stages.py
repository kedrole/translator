from . import search, unique, yandex_translate
from .models import Article, ArticleItem, Log
from datetime import datetime

def add_artices_from_articlelistpage_to_parsing_queue(list_page):
    parser = search.ParserListArticlesPage(list_page)
    articles_hrefs_list = parser.get_items_recoursive()

    for href in articles_hrefs_list:
        if Article.objects.filter(original_page_href = href).exists():
            print("Статья " + href + " уже в БД")
        else:
            article = Article(original_page_href=href, list_page=list_page, status='Parsing')
            article.save()

            log("Добавлена статья в очередь на пасинг: " + href, article)

def parse_articles_with_status_parsing():
    articles_with_status_parsing = Article.objects.filter(status="Parsing")
    print("Со статусом парсинг: " + str(len(articles_with_status_parsing)))
    for article in articles_with_status_parsing:
        try:
            print("_______________________________")
            print("Контент: " + article.original_page_href)
            (title, content_blocks) = get_translate_content(article)
            article.title = title
            article_item = ArticleItem(article=article, tag='title', type='Заголовок', original=title, translation='')
            article_item.save()

            for item in content_blocks:
                article_item = ArticleItem(article=article, tag=item['tag'], type=get_type_name(item['tag']), original=item['original'], translation='')
                article_item.save()

            article.status = 'Cheking'
            article.save()
            log("Проведен парсинг статьи: " + article.original_page_href, article)
        except Exception as e:
            article.status = 'Error'
            article.save()
            log("Ошибка парсинга статьи " + article.original_page_href + ": " + str(e), article)

def get_uniquedata_articles_with_status_checking_and_autoreject_if_needed():
    articles_with_status_checking = Article.objects.filter(status="Cheking")
    print("Со статусом Cheking: " + str(len(articles_with_status_checking)))

    check = unique.UniqueCheck()
    for article in articles_with_status_checking:
        if article.original_unique_check_uid == "":
            text = get_text_from_article(article)

            # Divide by spaces or commas
            exceptdomain = article.list_page.site.domain_name
            
            (status, result) = check.send_text_and_get_uid(text, exceptdomain)
            if status == "error":
                article.status = 'Error'
                log("Ошибка при отправке текста на проверку уникальности: " + str(result), article)
            else:
                article.original_unique_check_uid = result
                log("Текст отправлен в очередь на проверку уникальности: " + str(result), article)
        else:
            print("Сбор результатов проверки уникальности")
            (status, result) = check.check_result(article.original_unique_check_uid)
            if status == "error":
                article.status = 'Error'
                log("Ошибка при проверке текста на уникальность: " + str(result), article)
            elif status == "not-checked":
                log("Попытка получения данных уникальности. Текст еще не проверен: " + str(result), article)
            else:
                article.original_unique_percent = result["unique"]
                article.original_unique_urls = result["urls"]
                article.original_unique_date_check = datetime.strptime(result["date_check"], "%d.%m.%Y %H:%M:%S")

                log("Данные по уникальности текста получены: " + str(result), article)
                if rejecting_article_needed(article):
                    log("Статья имеет уникальность ниже предельного значения. Установка статуса Rejected Auto", article)
                    article.status = 'Rejected Auto'
                else:
                    log("Установка статуса Auto Translating: " + str(result), article)
                    article.status = 'Auto Translating'

        article.save()

def get_text_from_article(article):
    text_items = [item.original for item in article.articleitem_set.all()]
    text = "\n".join(text_items)
    return text

def rejecting_article_needed(article):
    if article.original_unique_percent < 10:
        return True
    return False

def get_translation_articles_with_status_autotranslating():
    articles_with_status_autotranslating = Article.objects.filter(status="Auto Translating")
    print("Со статусом Auto Translating: " + str(len(articles_with_status_autotranslating)))

    if len(articles_with_status_autotranslating) == 0:
        return

    yandexTranslate = yandex_translate.YandexTranslate()
    for article in articles_with_status_autotranslating:
        articleitem_set = article.articleitem_set.all()

        original_list = [item.original for item in articleitem_set]

        (status, result) = yandexTranslate.get_translation_list(original_list)
        if status == "error":
            article.status = 'Error'
            log("Ошибка при получении перевода текста: " + str(result), article)
        elif status == "success":
            if len(articleitem_set) != len(result):
                log("Длина массива оригинальных фрагментов не равна длине массива переведенных фрагментов. " + str(len(articleitem_set)) + " != " + str(len(translated_items)), article)
                article.status = 'Error'
            else:
                for idx, articleitem in enumerate(articleitem_set):
                    articleitem.translation = result[idx]
                    articleitem.save()
                log("Перевод статьи загружен", article)
                article.status = 'Selection'

        article.save()


def get_type_name(tag_name):
    type_name = 'Не определен'
    if tag_name in ['p']:
        type_name = 'Абзац'
    if tag_name in ['li']:
        type_name = 'В списке'
    elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10']:
        type_name = 'Подзаголовок'
    return type_name


def get_translate_content(article):
    #href = "https://tastessence.com/sweet-chili-sauce-substitute"
    #href = "http://topmira.com/tehnika/item/549-best-smartfons-2020-do-15000"

    parser = search.ParserArticlePage()

    print("start get_page")
    page = parser.get_page(article.original_page_href)

    print("end get_page")
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(page)

    print("start get_content")
    (title, content_blocks) = parser.get_content_from_article(article, page)

    return (title, content_blocks)

def log(text, article):
    print(str(article.id) + ": " + text)
    Log(article=article, text=text).save()
