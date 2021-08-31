from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from . import processing_stages
from .models import Site, ListPage, Article, ArticleItem, Log
from .forms import SiteEditForm, ListPageEditForm, ArticleEditForm

import json


def log_page_view(request):
    logs = Log.objects.filter()    
    return render(request, r'main/log.html', {"logs": logs})

def sites_list_view(request):
    sites = Site.objects.filter()    
    return render(request, r'main/sites_list.html', {"sites": sites})

def list_pages_list_view(request):
    list_pages = ListPage.objects.filter()    
    return render(request, r'main/list_pages_list.html', {"list_pages": list_pages})

def articles_list_view(request):
    articles = Article.objects.filter()
    return render(request, r'main/articles_list.html', {"articles": articles})

def article_processing_view(request, pk):
    article = Article.objects.get(id=pk)
    article_items = ArticleItem.objects.filter(article=article)

    options_type_list = [
        'Абзац',
        'Абзац-примечание',
        'Подзаголовок',
        'Заголовок',
        'Элемент списка',
        'Не определен',
    ]

    return render(request, r'main/article_processing.html', {'article_items': article_items, 'options_type_list': options_type_list})


def article_save_view(request, id):
    try:
        if request.method != 'POST':
            raise Exception("Invalid method")

        new_items = request.POST["json"]
        new_items = json.loads(new_items)
        
        print(new_items)

        article = Article.objects.get(id=id)
        article_items = ArticleItem.objects.filter(article=article)
        article_items.delete()

        for item in new_items:
            article_item = ArticleItem(article=article, tag=item['tag'], original=item['original'], translation=item['translation'], type=item['type'])
            article_item.save()

        return HttpResponse("Успешно сохранено", status=200)
    except Exception as e:
        return HttpResponse(str(e), status=400)

################
##### ADD ######
################

def site_add_view(request):
    if request.method == 'POST':
        add_href_form = SiteEditForm(request.POST)
        if add_href_form.is_valid():
            new_href = add_href_form.save()
            messages.success(request, 'Сайт добавлен успешно')

            return render(request, 'main/site_save.html')
    
    return render(request, 'main/site_save.html', {'form': SiteEditForm()})


def list_page_add_view(request):
    if request.method == 'POST':
        add_href_form = ListPageEditForm(request.POST)
        if add_href_form.is_valid():
            new_href = add_href_form.save()
            messages.success(request, 'Страница добавлена успешно')

            return render(request, 'main/list_page_save.html')
    
    return render(request, 'main/list_page_save.html', {'form': ListPageEditForm()})

def article_add_view(request):
    tpl_name = 'main/article_save.html'
    if request.method == 'POST':
        add_form = ArticleEditForm(request.POST)
        if add_form.is_valid():
            new_item = add_form.save()
            messages.success(request, 'Статья добавлена успешно')

            return render(request, tpl_name)
    return render(request, tpl_name, {'form': ArticleEditForm()})

################
##### EDIT #####
################

def site_edit_view(request, id):
    if request.method == 'POST':
        obj = Site.objects.get(id=id)
        edit_form = SiteEditForm(instance=obj, data=request.POST)

        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, 'Сайт изменен успешно')
        else:
            messages.error(request, 'Ошибка изменения')
    else:
        obj = Site.objects.get(id=id)
        edit_form = SiteEditForm(instance=obj)
    return render(request,'main/site_save.html', {'form': edit_form, 'edit': True})

def list_page_edit_view(request, id):
    if request.method == 'POST':
        obj = ListPage.objects.get(id=id)
        edit_form = ListPageEditForm(instance=obj, data=request.POST)

        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, 'Страница со статьями изменена успешно')
        else:
            messages.error(request, 'Ошибка изменения')
    else:
        obj = ListPage.objects.get(id=id)
        edit_form = ListPageEditForm(instance=obj)
    return render(request,'main/list_page_save.html', {'form': edit_form, 'edit': True})

def article_edit_view(request, id):
    if request.method == 'POST':
        obj = Article.objects.get(id=id)
        edit_form = ArticleEditForm(instance=obj, data=request.POST)

        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, 'Статья изменена успешно')
        else:
            messages.error(request, 'Ошибка изменения')
    else:
        obj = Article.objects.get(id=id)
        edit_form = ArticleEditForm(instance=obj)
    return render(request,'main/article_save.html', {'form': edit_form, 'edit': True})

class SiteDeleteView(DeleteView):#, LoginRequiredMixin):
    model = Site
    success_url = reverse_lazy('main:site_list')

class ArticleDeleteView(DeleteView):#, LoginRequiredMixin):
    model = Article
    success_url = reverse_lazy('main:articles_list')

class ListPageDeleteView(DeleteView):#, LoginRequiredMixin):
    model = ListPage
    success_url = reverse_lazy('main:list_page_list')

def list_page_articles_view(request, pk):
    list_page = ListPage.get(id=pk)
    articles = Article.objects.filter(list_page = list_page)    

    return render(request, r'main/page_articles.html', {"articles": articles})

def list_page_process_view(request, id):
    list_page = ListPage.objects.get(id=id)
    
    # ЭТАП 1
    processing_stages.add_artices_from_articlelistpage_to_parsing_queue(list_page)

    # ЭТАП 2
    processing_stages.parse_articles_with_status_parsing()

    # ЭТАП 3
    processing_stages.get_uniquedata_articles_with_status_checking_and_autoreject_if_needed()

    # ЭТАП 4
    processing_stages.get_translation_articles_with_status_autotranslating()

    return render(request, r'main/list_page_process.html', {"articles_hrefs_list": []})

def article_get_translation_unique():
    pass