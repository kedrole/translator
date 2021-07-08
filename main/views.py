from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

from . import search
from .models import Page, Article, ArticleItem
from .forms import PageEditForm, ArticleEditForm

import json

def articles_list(request):
    articles = Article.objects.filter()    

    return render(request, r'main/articles_list.html', {"articles": articles})

def article_processing(request, pk):
    article = Article.objects.get(id=pk)
    article_items = ArticleItem.objects.filter(article=article)

    #translate_content = get_translate_content()
    options_type_list = [
        'Абзац',
        'Абзац-примечание',
        'Подзаголовок',
        'Заголовок',
        'Элемент списка',
        'Не определен',
    ]

    return render(request, r'main/article_processing.html', {'article_items': article_items, 'options_type_list': options_type_list})


def article_save(request, id):
    try:
        if request.method != 'POST':
            raise Exception("Invalid method")

        new_items = request.POST["json"]
        print("0")
        new_items = json.loads(new_items)
        
        print(new_items)
        if len(new_items) == 0:
            raise Exception("Items length = 0")
        
        article = Article.objects.get(id=id)
        article_items = ArticleItem.objects.filter(article=article)
        article_items.delete()

        for item in new_items:
            article_item = ArticleItem(article=article, tag=item['tag'], original=item['original'], translation=item['original'], type=item['type'])
            article_item.save()

        return HttpResponse("Успешно сохранено", status=200)
    except Exception as e:
        return HttpResponse(str(e), status=400)


def pages_list(request):
    pages = Page.objects.filter()    

    return render(request, r'main/pages_list.html', {"pages": pages})

def page_add(request):
    if request.method == 'POST':
        add_href_form = PageEditForm(request.POST)
        if add_href_form.is_valid():
            new_href = add_href_form.save()
            messages.success(request, 'Сайт добавлен успешно')

            return render(request, 'main/page_save.html')
    
    return render(request, 'main/page_save.html', {'form': PageEditForm()})

def article_add(request):
    tpl_name = 'main/article_save.html'
    if request.method == 'POST':
        add_form = ArticleEditForm(request.POST)
        if add_form.is_valid():
            new_item = add_form.save()
            messages.success(request, 'Статья добавлена успешно')

            return render(request, tpl_name)
    return render(request, tpl_name, {'form': ArticleEditForm()})

def article_edit(request, id):
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

def page_edit(request, id):
    if request.method == 'POST':
        page_obj = Page.objects.get(id=id)
        page_edit_form = PageEditForm(instance=page_obj, data=request.POST)

        if page_edit_form.is_valid():
            page_edit_form.save()
            messages.success(request, 'Сайт изменен успешно')
        else:
            messages.error(request, 'Ошибка изменения')
    else:
        page_obj = Page.objects.get(id=id)
        page_edit_form = PageEditForm(instance=page_obj)
    return render(request,'main/page_save.html', {'form': page_edit_form, 'edit': True})

def page_articles(request, pk):
    page = Page.get(id=pk)
    articles = Article.objects.filter(page = page)    

    return render(request, r'main/page_articles.html', {"articles": articles})


def get_type_name(tag_name):
    type_name = 'Не определен'
    if tag_name in ['p']:
        type_name = 'Абзац'
    if tag_name in ['li']:
        type_name = 'В списке'
    elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10']:
        type_name = 'Подзаголовок'
    return type_name

def get_translate_content():
    href = "https://tastessence.com/sweet-chili-sauce-substitute"
    href = "http://topmira.com/tehnika/item/549-best-smartfons-2020-do-15000"

    parser = search.Tastessence()

    print("start get_page")
    page = parser.get_page(href)

    print("end get_page")
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(page)

    print("start get_content")
    content = parser.get_content_from_article(page)

    for part in content:
        part['translation'] = part['original']
        part['type_name'] = get_type_name(part['tag_name'])

    return content