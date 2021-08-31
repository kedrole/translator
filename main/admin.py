from django.contrib import admin

# Register your models here.

from .models import Site, ListPage, Article, ArticleItem#, ArticleUniqueUrls 


@admin.register(Site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['created', 'domain_name', 'content_tag_name', 'content_property_name', 'content_property_value']

@admin.register(ListPage)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['created', 'site', 'href']

@admin.register(Article)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['created', 'title', 'list_page', 'status', 'original_unique_percent']

@admin.register(ArticleItem)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['article', 'tag', 'original', 'translation', 'type']

#@admin.register(ArticleUniqueUrls)
#class ProfileAdmin(admin.ModelAdmin):
#    list_display = ['article', 'url', 'plagiat_proc']