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
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Сайт')

    href = models.CharField(verbose_name='Страница со списком контента', default='', blank=True, max_length=250)

#class HrefContentPage(models.Model):
#    href = models.CharField(default='', max_length=120)
#    page = models.ForeignKey(Page, on_delete=models.CASCADE)

class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(verbose_name='Название статьи', default='', max_length=120)
    original_page_href = models.CharField(verbose_name='Адрес страницы-оригинала', default='', max_length=120)
    list_page = models.ForeignKey(ListPage, on_delete=models.CASCADE, verbose_name='Страница сайта', null=True)

    original_unique_check_uid = models.CharField(verbose_name='UID проверки уникальности оригинала', default='', blank=True, max_length=120)
    original_unique_percent = models.FloatField(verbose_name='Процент уникальности оригинала', default=-100)
    original_unique_urls = models.TextField(verbose_name='JSON url', blank=True)
    original_unique_date_check = models.DateTimeField(verbose_name='JSON url', default=datetime(1, 1, 1))

    translation_unique_check_uid = models.CharField(verbose_name='UID проверки уникальности оригинала', default='', blank=True, max_length=120)
    translation_unique_percent = models.FloatField(verbose_name='Процент уникальности оригинала', default=-100)
    translation_unique_urls = models.TextField(verbose_name='JSON url', blank=True)
    translation_unique_date_check = models.DateTimeField(verbose_name='JSON url', default=datetime(1, 1, 1))

    STATUS = [
        ('Rejected Auto', 'Отклонено автоматически'),
        ('Rejected Manually', 'Отклонено вручную'),
        ('Parsing', 'Парсинг контента'),
        ('Cheking', 'Проверка на уникальность'),
        ('Auto Translating', 'Перевод автоматический'),
        ('Selection', 'Отбор'),
        ('Processing', 'В процессе перевода'),
        ('Published', 'Опубликовано'),
        ('Error', 'Ошибка'),
    ]

    status = models.CharField(verbose_name='Статус', max_length=30, choices=STATUS, default='Error')

    #urls_json = models.TextField(verbose_name='JSON url')

class ArticleItem(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.CharField(default='', max_length=30)
    original = models.TextField()
    translation = models.TextField()

    TYPE = [
        ('Абзац', 'Абзац'),
        ('Абзац-примечание', 'Абзац-примечание'),
        ('Подзаголовок', 'Подзаголовок'),
        ('Заголовок', 'Заголовок'),
        ('Элемент списка', 'Элемент списка'),
        ('Не определен', 'Не определен'),
    ]
    type = models.CharField(verbose_name='Тип', max_length=30, choices=TYPE, default='Не определен')

#class ArticleUniqueUrls(models.Model):
#    article = models.ForeignKey(Article, on_delete=models.CASCADE)
#    plagiat_proc = models.FloatField(verbose_name='Процент плагиата', default=-1.0)
#    url = models.CharField(verbose_name='URL', default='', max_length=500)

class Log(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    #module_name = models.CharField(verbose_name='Имя модуля', default='', max_length=500)
    text = models.TextField(verbose_name='Текст сообщения')