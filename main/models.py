from django.db import models

#class Site(models.Model)

class Page(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    domain_name = models.CharField(verbose_name='Доменное имя', default='', max_length=120)
    content_page = models.CharField(verbose_name='Страница со списком контента', default='', max_length=250)

    content_tag_name = models.CharField(default='', blank=True, max_length=120)
    content_property_name = models.CharField(default='', blank=True, max_length=120)
    content_property_value = models.CharField(default='', blank=True, max_length=120)

#class HrefContentPage(models.Model):
#    href = models.CharField(default='', max_length=120)
#    page = models.ForeignKey(Page, on_delete=models.CASCADE)

class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(verbose_name='Название статьи', default='', max_length=120)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name='Страница сайта')

    STATUS = [
        ('Rejected Auto', 'Rejected Auto'),
        ('Rejected Manually', 'Rejected Manually'),
        ('Cheking', 'Cheking'),
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Published', 'Published'),
        ('Error', 'Error'),
    ]

    status = models.CharField(verbose_name='Статус', max_length=30, choices=STATUS, default='Error')

    original_unique_proc = models.FloatField(verbose_name='Процент уникальности оригинала', default=-1.0)
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

class ArticleUniqueUrls(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    plagiat_proc = models.FloatField(verbose_name='Процент плагиата', default=-1.0)
    url = models.CharField(verbose_name='URL', default='', max_length=500)

