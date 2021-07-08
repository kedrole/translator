from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('pages/', views.pages_list, name='page_list'),
    path('pages/add/', views.page_add, name='page_add'),
    path('pages/<int:id>/edit/', views.page_edit, name='page_edit'),
    path('pages/<int:id>/articles/', views.page_articles, name='page_articles'),
    
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/add/', views.article_add, name='article_add'),
    path('articles/<int:id>/edit/', views.article_edit, name='article_edit'),
    path('article/<int:pk>/', views.article_processing, name='article_processing'),
    path('article/<int:id>/save/', views.article_save, name='article_save'),

]