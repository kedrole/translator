import datetime
from typing import List, Tuple
import requests
import re
import os
import time
import random
from bs4 import BeautifulSoup


def log(message):
    with open("log.txt", "a") as f:
        mess = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " " + message
        print(mess)
        f.write(mess + "\n")

class ParserListArticlesPage:
    def __init__(self, list_page):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
        }

        self.page_href = "https://" + list_page.site.domain_name + "/" + list_page.href
        self.preview_tag_name = list_page.site.preview_tag_name
        self.preview_tag_property_name = list_page.site.preview_tag_property_name
        self.preview_tag_property_value = list_page.site.preview_tag_property_value

        self.max_page_count = list_page.max_page_count
        if list_page.last_checked:
            self.max_page_count = 1

    def get_page(self, page):
        try:
            return self.session.get(page).text
        except Exception as e:
            log("Ошибка получения страницы " + page + " " + str(e))

    #def tag_starts_with_stopfraze(self, tag):
    #    if str(tag).startswith(self.stop_fraze):
    #        return True
    #    return False

    def get_items(self):
        if "{page}" not in self.page_href:
            return self.get_items_recoursive()
        else:
            all_items = []
            for page_num in range(1, self.max_page_count+1):
                print("Получение страницы " + str(page_num))
                items = self.get_items_recoursive(page_num)
                if len(items) > 0:
                    all_items.extend(items)
                else:
                    break
            return all_items

    def get_items_recoursive(self, page_num=False):
        page_href = self.page_href
        if page_num:
            page_href = self.page_href.replace("{page}", str(page_num))


        page = self.get_page(page_href)
        if not page:
            return []

        soup = BeautifulSoup(page, 'html.parser')
        blocks_articles = soup.find_all(self.preview_tag_name, attrs={self.preview_tag_property_name: self.preview_tag_property_value})

        print("Найдено блоков статей: " + str(len(blocks_articles)))
        return [block.find('a') for block in blocks_articles if str(type(block)) == "<class 'bs4.element.Tag'>"]

class ParserArticlePage:
    def __init__(self):
        self.header_tags = ['h1', 'h2']
        self.paragraph_tags = ['p']
        self.inner_tags =           ['a', 'strong', 'b', 'i', 'br', 'code']
        self.inner_paragraph_tags = ['a', 'strong', 'b', 'i', 'br', 'code', 'span']
        self.stop_frazes = [
            'Like it? Share it',
            'Share',
            'Tweet',
            'Pin',
            'LinkedIn',
            'Email',
            'Previous Post',
            'Next Post',
        ]

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
        }

    def get_page(self, page):
        return self.session.get(page).text

    def tagname_mean_whole_separate_block(self, tagname):
        return str(tagname) in self.paragraph_tags or str(tagname) in self.header_tags or str(tagname) == "li"

    def add_items_recoursive(self, tag, parent_tag_name, nesting_level):
        #print("--------УВ: " + str(nesting_level))
        #if self.tag_starts_with_stopfraze(tag):
        #    return

        if str(type(tag)) == "<class 'bs4.element.Tag'>":
            if self.tagname_mean_whole_separate_block(tag.name):
                print(str(tag.name) + "------------------- в списке тегов")
                if self.block_text_is_garbage(tag.text.strip()):
                    print("__block__is_garbage__,try find images")
                    # try_find_images(tag)
                    for child in tag.children:
                        self.add_items_recoursive(child, str(tag.name), nesting_level + 1)
                else:
                    #print("# Before clearing: " + str(tag))
                    #print("# After clearing: " + str(self.get_cleared_object(tag)))
                    print("Adding...")
                    self.res_objects.append({"original": str(self.get_cleared_object(tag)).strip(), "original_text": str(tag.text).strip(), "tag": tag.name, "nesting_lvl": nesting_level, "parent_tag": parent_tag_name})
                
                #print("\n[" + self.res_objects[-1]['tag'] + "] " + str(self.res_objects[-1]['nesting_lvl']) + " " + self.res_objects[-1]['val'])

            elif self.tag_is_image(tag):
                print('ИЗОБРАЖЕНИЕ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                self.res_objects.append({"src": tag['src'], "original": "", "tag": tag.name, "nesting_lvl": nesting_level})
            else:
                print(str(tag.name) + " ------------------- НЕ в списке тегов")
                print("test1: " + str(str(tag)))
                if self.all_child_are_inner_tags_or_strings(tag) and not self.block_text_is_garbage(tag.text.strip()):
                    print("Adding...")
                    self.res_objects.append({"original": str(self.get_cleared_object(tag)).strip(), "original_text": str(tag.text).strip(), "tag": tag.name, "nesting_lvl": nesting_level})
                else:
                    for child in tag.children:
                        self.add_items_recoursive(child, str(tag.name), nesting_level + 1)

        elif str(type(tag)) == "<class 'bs4.element.NavigableString'>":
            if self.block_text_is_garbage(str(tag).strip()):
                return

            self.res_objects.append({"original_text": str(tag).strip(), "original": str(tag).strip(), "tag": tag.parent.name, "nesting_lvl": nesting_level})
            #print("[" + self.res_objects[-1]['tag'] + "] " + str(self.res_objects[-1]['nesting_lvl']) + " " + self.res_objects[-1]['val'])
        else:
            print("ТИП: " + str(type(tag)))

    def tag_is_image(self, tag):
        return str(tag.name) == 'img' and tag.has_attr('src')

    def block_text_is_garbage(self, text):
        if text == "":
            return True

        text_lower = text.lower()
        text_len = len(text)
        for fraze in self.stop_frazes:
            if (len(fraze) <= text_len <= len(fraze) + 3) and fraze.lower() in text_lower:
                return True

        return False

    def all_child_are_inner_tags_or_strings(self, tag):
        def check_if_image_in_tag(tag):
            def tag_is_image(tag):
                return str(tag.name) == 'img' and tag.has_attr('src')

            if str(type(tag)) == "<class 'bs4.element.NavigableString'>":
                return False

            if tag_is_image(tag):
                return True

            for child in tag.children:
                if check_if_image_in_tag(child):
                    return True

        for child_tag in tag.children:
            if str(type(child_tag)) == "<class 'bs4.element.NavigableString'>":
                continue

            if str(child_tag.name) not in self.inner_paragraph_tags:
                return False

        if check_if_image_in_tag(tag):
            return False

        return True

    def get_cleared_object(self, tag):
        ''' returns tag cleared from unwanted tags and attributes '''
        def get_cleared_from_unwanted_tags(self, tag):
            '''  returns bs4 tag, consists only of 'a', 'strong', 'b', 'i', 'br', 'code' '''
            def get_cleared_tag(tag):
                if tag.name not in ['a', 'strong', 'b', 'i', 'br', 'code']:
                    _tag = ''.join([str(child) for child in tag.children])
                    return BeautifulSoup(_tag, 'html.parser')
                return tag

            if tag.text == '':
                return ''

            _tag = get_cleared_tag(tag)
            #print("After cleaning: " + str(_tag))

            if len(_tag.contents) == 1:
                return _tag
            else:
                res_list = []
                for child in _tag:
                    if str(type(child)) == "<class 'bs4.element.Tag'>":
                        res_list.append(self.get_cleared_object(child))
                    else:
                        res_list.append(str(child))

                print("Res: " + str(BeautifulSoup(''.join([str(res) for res in res_list]), 'html.parser')))
                return BeautifulSoup(''.join([str(res) for res in res_list]), 'html.parser')

        def get_cleared_of_attributes(tag) -> str:
            ''' delete all attrs from tag and children '''
            def del_attrs_from_tag(tag) -> None:
                for attr in list(tag.attrs):
                    del tag.attrs[attr]
            
            if str(type(tag)) == "<class 'bs4.element.NavigableString'>":
                return tag
                
            del_attrs_from_tag(tag)

            for child in tag.children:
                child = get_cleared_of_attributes(child)

            return tag

        tag = get_cleared_from_unwanted_tags(self, tag)
        return get_cleared_of_attributes(tag)

    def get_content_from_article(self, article) -> Tuple[str, List[dict]]:
        page = self.get_page(article.original_page_href)
        if not page:
            return

        self.res_objects = []

        soup = BeautifulSoup(page, 'html.parser')

        title = soup.find('title').text
        print("Title: " + title)

        block_content = soup.find(article.list_page.site.content_tag_name, attrs={article.list_page.site.content_property_name: article.list_page.site.content_property_value})

        self.add_items_recoursive(block_content, "MAIN", 0)

        if len(self.res_objects) == 0:
            return

        for tag in self.res_objects:
            print("[" + tag['tag'] + " - " + str(tag['nesting_lvl']) + "]  " + tag['original'])

        return (title, self.res_objects)