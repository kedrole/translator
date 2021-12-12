from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('sites/', views.sites_list_view, name='site_list'),
    path('sites/add/', views.site_add_view, name='site_add'),
    path('sites/<int:id>/edit/', views.site_edit_view, name='site_edit'),
    path('sites/<int:pk>/del/', views.SiteDeleteView.as_view(), name='site_del'),
    #path('sites/<int:id>/articles/', views.sites_articles, name='page_articles'),

    path('pages/', views.list_pages_list_view, name='list_page_list'),
    path('pages/add/', views.list_page_add_view, name='list_page_add'),
    path('pages/<int:id>/', views.list_page_process_view, name='list_page_process'),
    path('pages/<int:id>/edit/', views.list_page_edit_view, name='list_page_edit'),
    path('pages/<int:pk>/del/', views.ListPageDeleteView.as_view(), name='list_page_del'),
    path('pages/<int:id>/articles/', views.list_page_articles_view, name='list_page_articles'),
    
    path('articles/', views.articles_list_view, name='articles_list'),
    path('articles/work/', views.articles_work_list_view, name='articles_work_list'),
    path('articles/notwork', views.articles_not_work_list_view, name='articles_not_work_list'),
    path('articles/add/', views.article_add_view, name='article_add'),
    path('article/<int:pk>/', views.article_processing_view, name='article_processing'),
    path('articles/<int:id>/edit/', views.article_edit_view, name='article_edit'),
    path('article/<int:id>/save/', views.article_save_view, name='article_save'),
    path('article/<int:pk>/send_to_review/', views.send_to_review_view, name='article_send_to_review'),
    path('article/<int:pk>/del/', views.ArticleDeleteView.as_view(), name='article_del'),
    path('article/<int:pk>/publish/', views.article_publish_view, name='article_publish'),
    path('article/<int:pk>/log/', views.article_log_view, name='article_log'),
    path('article/<int:pk>/reject/', views.article_reject_view, name='article_reject'),
    path('article/<int:pk>/accept_on_parsing_stage/', views.article_accept_on_parsing_stage_view, name='article_accept_on_parsing_stage'),
    path('article/<int:pk>/accept_on_review_stage/', views.article_accept_on_review_stage_view, name='article_accept_on_review_stage'),
    
    path('article/<int:id>/get_translation_unique/', views.article_get_translation_unique, name='get_translation_unique'),

    path('image/<int:pk>/', views.image_processing_view, name='image_processing'),
    path('image/<int:pk>/save', views.image_save_view, name='image_save'),

    path('log/', views.log_page_view, name='log'),
    path('settings/', views.settings_view, name='settings'),

    path('', views.articles_work_list_view, name='articles_work_list'),
]