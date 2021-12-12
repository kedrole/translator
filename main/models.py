from django.db import models
from datetime import datetime

#class Site(models.Model)

class Site(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    domain_name = models.CharField(verbose_name='Доменное имя', default='', max_length=120)

    content_tag_name = models.CharField(default='', blank=True, max_length=120)
    content_property_name = models.CharField(default='', blank=True, max_length=120)
    content_property_value = models.CharField(default='', blank=True, max_length=120)

    preview_tag_name = models.CharField(default='', blank=True, max_length=120)
    preview_tag_property_name = models.CharField(default='', blank=True, max_length=120)
    preview_tag_property_value = models.CharField(default='', blank=True, max_length=120)

class ListPage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(blank = True, null = True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Сайт')

    href = models.CharField(verbose_name='Страница со списком контента ({page} - тег для номера страницы)', default='', blank=True, max_length=250)
    in_work = models.BooleanField(verbose_name='В работе', default=False)
    max_page_count = models.IntegerField(verbose_name='Максимальное количество страниц (pagination)', default=1)

class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(verbose_name='Название статьи', default='', max_length=120)
    original_page_href = models.CharField(verbose_name='Адрес страницы-оригинала', default='', max_length=120)
    list_page = models.ForeignKey(ListPage, on_delete=models.CASCADE, verbose_name='Страница сайта', null=True)

    original_unique_check_uid = models.CharField(verbose_name='UID проверки уникальности оригинала', default='', blank=True, max_length=120)
    original_unique_percent = models.FloatField(verbose_name='Процент уникальности оригинала', default=-100)
    original_unique_urls = models.TextField(verbose_name='JSON проверки уникальности оригинала', blank=True)
    original_unique_date_check = models.DateTimeField(verbose_name='Дата проверки уникальности оригинала', default=datetime(1, 1, 1))

    translation_unique_check_uid = models.CharField(verbose_name='UID проверки уникальности перевода', default='', blank=True, max_length=120)
    translation_unique_percent = models.FloatField(verbose_name='Процент уникальности перевода', default=-100)
    translation_unique_urls = models.TextField(verbose_name='JSON проверки уникальности перевода', blank=True)
    translation_unique_date_check = models.DateTimeField(verbose_name='Дата проверки уникальности перевода', default=datetime(1, 1, 1))

    accepted_on_parsing_stage = models.BooleanField(default=False)
    accepted_on_review_stage = models.BooleanField(default=False)

    locked_by_autotask = models.BooleanField(default=False)

    STATUS = [
        ('Rejected Auto', 'Отклонено автоматически'),
        ('Rejected Manually', 'Отклонено вручную'),
        ('Processing', 'В работе'),
        ('Published', 'Опубликовано'),
        ('Error', 'Ошибка'),
    ]

    status = models.CharField(verbose_name='Статус', max_length=30, choices=STATUS, default='Error')

    STAGE = [
        ('Parsing', 'Парсинг контента'),
        ('Checking original unique', 'Проверка на уникальность оригинала'),
        ('Auto Translating', 'Перевод автоматический'),
        ('Traslating', 'В процессе перевода'),
        ('Checking translation unique', 'Проверка на уникальность перевода'),
        ('Review', 'Финальная проверка'),
        ('Publishing', 'Опубликование'),
        ('Published', 'Опубликовано'),
    ]

    stage = models.CharField(verbose_name='Статус', max_length=30, choices=STAGE, default='Parsing')

class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    base64_original = models.TextField(default='')
    base64_translated = models.TextField(default='')
    src = models.CharField(default='', max_length=500)

class ArticleItem(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.CharField(default='', max_length=30)
    original = models.TextField(default='')
    original_text = models.TextField(default='')
    translation = models.TextField(default='')
    translation_text = models.TextField(default='')
    
    # В случае если ArticleItem - изображение
    article_image = models.ForeignKey(ArticleImage, on_delete=models.CASCADE, null=True)

    TYPE = [
        ('Абзац', 'Абзац'),
        ('Абзац-примечание', 'Абзац-примечание'),
        ('Подзаголовок', 'Подзаголовок'),
        ('Заголовок', 'Заголовок'),
        ('Элемент списка', 'Элемент списка'),
        ('Изображение', 'Изображение'),
        ('Не определен', 'Не определен'),
    ]
    type = models.CharField(verbose_name='Тип', max_length=30, choices=TYPE, default='Не определен')

class Log(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    text = models.TextField(verbose_name='Текст сообщения')