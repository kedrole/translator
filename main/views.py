from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from . import processing_stages, publish
from .models import Site, ListPage, Article, ArticleItem, ArticleImage, Log
from .forms import SiteEditForm, ListPageEditForm, ArticleEditForm

from django.db import transaction

import json


def settings_view(request):
    logs = Log.objects.filter()    
    return render(request, r'main/settings.html', {"logs": logs})
    
def log_page_view(request):
    logs = Log.objects.filter()    
    return render(request, r'main/log.html', {"logs": logs})

def article_log_view(request, pk):
    article = Article.objects.get(id=pk)
    logs = Log.objects.filter(article=article)
    return render(request, r'main/log.html', {"logs": logs, "article": article})

def sites_list_view(request):
    sites = Site.objects.filter()    
    return render(request, r'main/sites_list.html', {"sites": sites})

def list_pages_list_view(request):
    list_pages = ListPage.objects.filter()    
    return render(request, r'main/list_pages_list.html', {"list_pages": list_pages})

def articles_list_view(request):
    articles = Article.objects.filter()
    return render(request, r'main/articles_list.html', {"articles": articles})

def articles_work_list_view(request):
    articles = Article.objects.filter(status__in=['Processing'])
    
    return render(request, r'main/articles_list.html', {"articles": articles})

def articles_not_work_list_view(request):
    articles = Article.objects.filter(status__in=['Rejected Auto', 'Rejected Manually', 'Published', 'Error'])
    return render(request, r'main/articles_list.html', {"articles": articles})

def article_reject_view(request, pk):
    article = Article.objects.get(id=pk)
    article.status = 'Rejected Manually'
    article.save()
    log("Статья отклонена вручную", article)
    return HttpResponse({"success": True})

def article_accept_on_parsing_stage_view(request, pk):
    article = Article.objects.get(id=pk)
    article.accepted_on_parsing_stage = True
    article.save()
    return HttpResponse("OK", status=200)

def article_accept_on_review_stage_view(request, pk):
    article = Article.objects.get(id=pk)
    article.accepted_on_review_stage = True
    article.save()
    return HttpResponse("OK", status=200)

def article_processing_view(request, pk):
    article = Article.objects.get(id=pk)
    article_items = ArticleItem.objects.filter(article=article)

    options_type_list = [opt_type for (opt_type, descr) in ArticleItem._meta.get_field('type').choices]
    #options_type_list = [
    #    'Абзац',
    #    'Абзац-примечание',
    #    'Подзаголовок',
    #    'Заголовок',
    #    'Элемент списка',
    #    'Не определен',
    #]

    return render(request, r'main/article_processing.html', {'article_items': article_items, 'options_type_list': options_type_list})

def image_processing_view(request, pk):
    article_image = ArticleImage.objects.get(id=pk)
    return render(request, r'main/image_processing.html', {'article_image': article_image})

def image_save_view(request, pk):
    if request.method != 'POST':
        raise Exception("Invalid method")

    base64 = request.POST['json']

    if not base64 or len(base64) == 0:
        return HttpResponse("Ошибка base64", status=500)

    article_image = ArticleImage.objects.get(id=pk)
    article_image.base64_translated = base64
    article_image.save()

    return HttpResponse("Успешно сохранено", status=200)


@transaction.atomic
def article_save_view(request, id):
    if request.method != 'POST':
        raise Exception("Invalid method")

    new_items = request.POST["json"]
    new_items = json.loads(new_items)

    article = Article.objects.get(id=id)
    article_items = ArticleItem.objects.filter(article=article)
    article_items.delete()

    for item in new_items:
        if item["type"] == 'Изображение':
            article_image = ArticleImage.objects.get(id=item["image_id"])
            ArticleItem(article=article, tag=item['tag'], type=item['type'], article_image=article_image, original='', translation='').save()
        else:
            ArticleItem(article=article, tag=item['tag'], original=item['original'], translation=item['translation'], type=item['type']).save()

    return HttpResponse("Успешно сохранено", status=200)


def send_to_review_view(request, pk):
    article = Article.objects.get(id=pk)
    article.stage = processing_stages.get_next_stage(article)
    article.save()
    return HttpResponse("OK", status=200)


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
    # ЭТАП 1
    
    processing_stages.STAGE_add_artices_from_articlelistpages_to_parsing_queue()

    # ЭТАП 2
    processing_stages.STAGE_parse_articles_with_stage_parsing()

    # ЭТАП 3
    processing_stages.STAGE_get_uniquedata_articles_with_stage_ChekingOriginalUnique_and_autoreject_if_needed()

    # ЭТАП 4
    processing_stages.STAGE_get_translation_articles_with_stage_autotranslating()

    # ЭТАП 5
    processing_stages.STAGE_get_uniquedata_articles_with_stage_CheckingTranslationUnique_and_autoreject_if_needed()

    # ЭТАП Х
    #processing_stages.publish

    return render(request, r'main/list_page_process.html', {"articles_hrefs_list": []})



def article_get_translation_unique(request, id):
    article = Article.objects.get(id=id)

    processing_stages.get_uniquedata_translated_article(article)

    return HttpResponse({"success": True})


def article_publish_view(request, pk):
    article = Article.objects.get(id=pk)

    site = 'makegen.ru'
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvbWFrZWdlbi5ydSIsImlhdCI6MTYzMDc2ODMwNywibmJmIjoxNjMwNzY4MzA3LCJleHAiOjE2MzEzNzMxMDcsImRhdGEiOnsidXNlciI6eyJpZCI6IjEifX19.VY31O7m7DFqGLmzr5tWjpJ_yoDaO08yDjfXkiaSJsbc'


    articleitem_set = article.articleitem_set.all()
    title = articleitem_set[0].translation

    article_items = [get_html_from_item(item) for item in articleitem_set[1:]]
    content = '\n\n'.join(article_items)

    print(title)
    print(article_items)


    pub = publish.Publish()
    result = pub.post_article_to_site(site, token, title, content)
    #print(result)

    return HttpResponse(str(result))

def get_html_from_item(item):
    val_opentag_closetag_dict = {
        'Абзац':            ['<!-- wp:paragraph -->\n<p>', '</p>\n<!-- /wp:paragraph -->'],
        'Абзац-примечание': ['', ''],
        'Подзаголовок':     ['<!-- wp:heading -->\n<h2>', '</h2>\n<!-- /wp:heading -->'],
        'Заголовок':        ['', ''],
        'Элемент списка':   ['', ''],
        'Не определен':     ['', ''],
    }

    open_tag = val_opentag_closetag_dict[item.type][0]
    close_tag = val_opentag_closetag_dict[item.type][1]

    return open_tag + item.translation + close_tag

def log(text, article):
    print(str(article.id) + ": " + text)
    Log(article=article, text=text).save()