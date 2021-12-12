from django.contrib.auth.models import User, Group 
from .models import Site, ListPage, Article, ArticleImage, ArticleItem
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = ('created', 'domain_name', 'content_tag_name', 'content_property_name', 'content_property_value', 'preview_tag_name', 'preview_tag_property_name', 'preview_tag_property_value')

class ListPageSerializer(serializers.HyperlinkedModelSerializer):
    #articles = serializers.PrimaryKeyRelatedField(many=True, queryset=ListPage.objects.all())

    class Meta:
        model = ListPage
        fields = ('created', 'last_checked', 'site', 'href', 'in_work', 'max_page_count')

class ArticleSerializer(serializers.ModelSerializer):
    #list_page = serializers.PrimaryKeyRelatedField(many=False, queryset=ListPage.objects.all())

    class Meta:
        model = Article
        fields = ('created', 'title', 'original_page_href', 'list_page', 'original_unique_check_uid', 'original_unique_percent', 'original_unique_urls', 'original_unique_date_check', 'translation_unique_check_uid', 'translation_unique_percent', 'translation_unique_urls', 'translation_unique_date_check', 'accepted_on_parsing_stage', 'accepted_on_review_stage', 'locked_by_autotask', 'status', 'stage')

class ArticleImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ('article', 'base64_original', 'base64_translated', 'src')

class ArticleItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArticleItem
        fields = ('article', 'tag', 'original', 'translation', 'article_image', 'type')
