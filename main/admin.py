from django.contrib import admin

# Register your models here.

from .models import Page, Article, ArticleUniqueUrls, ArticleItem


@admin.register(Page)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['created', 'domain_name', 'content_page', 'content_tag_name', 'content_property_name', 'content_property_value']

@admin.register(Article)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['created', 'title', 'page', 'status', 'original_unique_proc']

@admin.register(ArticleItem)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['article', 'tag', 'original', 'translation', 'type']

@admin.register(ArticleUniqueUrls)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['article', 'url', 'plagiat_proc']