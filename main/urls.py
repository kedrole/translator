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
    path('', views.articles_list_view, name='articles_list'),
    path('articles/add/', views.article_add_view, name='article_add'),
    path('article/<int:pk>/', views.article_processing_view, name='article_processing'),
    path('articles/<int:id>/edit/', views.article_edit_view, name='article_edit'),
    path('article/<int:id>/save/', views.article_save_view, name='article_save'),
    path('article/<int:pk>/del/', views.ArticleDeleteView.as_view(), name='article_del'),
    
    path('article/<int:id>/get_translation_unique/', views.article_get_translation_unique, name='get_translation_unique'),

    
    path('log/', views.log_page_view, name='log'),
]