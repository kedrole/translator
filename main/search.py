import datetime
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


    def get_page(self, page):
        return self.session.get(page).text

    #def tag_starts_with_stopfraze(self, tag):
    #    if str(tag).startswith(self.stop_fraze):
    #        return True
    #    return False

    def get_items_recoursive(self):
        print("start get_page")
        page = self.get_page(self.page_href)
        print("end get_page")

        with open('page_list_articles.html', 'w', encoding='utf-8') as f:
            f.write(page)

        soup = BeautifulSoup(page, 'html.parser')
        blocks_articles = soup.find_all(self.preview_tag_name, attrs={self.preview_tag_property_name: self.preview_tag_property_value})

        print("Найдено блоков статей: " + str(len(blocks_articles)))

        return [block.find('a')['href'] for block in blocks_articles if str(type(block)) == "<class 'bs4.element.Tag'>"]



class ParserArticlePage:
    def __init__(self):
        self.restricted_tags = ['iframe', 'script', 'a']
        self.header_tags = ['h2']
        self.paragraph_tags = ['p']
        self.inner_tags = ['strong', 'i']
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

    #def tag_starts_with_stopfraze(self, tag):
    #    if str(tag).startswith(self.stop_fraze):
    #        return True
    #    return False

    def add_items_recoursive(self, tag, parent_tag_name, nesting_level):
        #print("")
        #print("--------УВ: " + str(nesting_level))
        #if self.tag_starts_with_stopfraze(tag):
        #    return

        if str(type(tag)) == "<class 'bs4.element.Tag'>":
            if str(tag.name) in self.paragraph_tags or str(tag.name) in self.header_tags or str(tag.name) == "li":
                #print(str(tag.name) + "------------------- в списке тегов, добавление текста")
                if self.block_text_is_garbage(tag.text.strip()):
                    return

                self.res_objects.append({"original": str(tag.text).strip(), "tag": tag.name, "nesting_lvl": nesting_level})
                
                #print("\n[" + self.res_objects[-1]['tag'] + "] " + str(self.res_objects[-1]['nesting_lvl']) + " " + self.res_objects[-1]['val'])
            else:
                #print(str(tag.name) + "------------------- НЕ в списке тегов")

                for desc in tag.children:
                    self.add_items_recoursive(desc, str(tag.name), nesting_level + 1)

        elif str(type(tag)) == "<class 'bs4.element.NavigableString'>":
            if self.block_text_is_garbage(str(tag).strip()):
                return
                
            self.res_objects.append({"original": str(tag).strip(), "tag": tag.parent.name, "nesting_lvl": nesting_level})
            #print("[" + self.res_objects[-1]['tag'] + "] " + str(self.res_objects[-1]['nesting_lvl']) + " " + self.res_objects[-1]['val'])
        #else:
            #print("ТИП: " + str(type(tag)))

    def block_text_is_garbage(self, text):
        if text == "":
            return True

        text_lower = text.lower()
        text_len = len(text)
        for fraze in self.stop_frazes:
            if (len(fraze) <= text_len <= len(fraze) + 3) and fraze.lower() in text_lower:
                return True

        return False

    def get_content_from_article(self, article, page):
        self.res_objects = []

        soup = BeautifulSoup(page, 'html.parser')

        title = soup.find('title').text
        print("Title: " + title)

        #block_content = soup.find('div', attrs={'class': 'entry-content'})
        #block_content = soup.find('div', attrs={'id': 'k2Container'})
        block_content = soup.find(article.list_page.site.content_tag_name, attrs={article.list_page.site.content_property_name: article.list_page.site.content_property_value})

        self.add_items_recoursive(block_content, "MAIN", 0)

        for tag in self.res_objects:
            print("[" + tag['tag'] + " - " + str(tag['nesting_lvl']) + "]  " + tag['original'])

        return (title, self.res_objects)
        #print(title.text)

# НЕ ИСПОЛЬЗУЕТСЯ
class Tastessence(ParserArticlePage):
    def get_items_from_page1(self, page, max_count):
        soup = BeautifulSoup(page, 'html.parser')

        item_regex = re.compile(r'item-wrapper\(([0-9]{6,12})\)')
        items = soup.find_all(attrs={"data-marker": item_regex})[:max_count]

        if len(items) == 0:
            if "Мы обнаружили, что запросы, поступающие с вашего IP-адреса, похожи на автоматические" in page:
                print("Заблокирован IP")
                #print(page)
            else:
                print("Ошибка. Нет объявлений на странице")

        res = []
        for item in items:
            id = re.findall(item_regex, item["data-marker"])[0]

            href = ''
            title = ''

            link = item.find(attrs={"data-marker": "item/link"})
            if link:
                if link.has_attr('href'):
                    href = link["href"]
                title = link.text
            else:
                print("NO HREF AND TITLE")

            price = item.find(attrs={"data-marker": "item/price"})
            if price:
            	price = price.text

            datetime = item.find(attrs={"data-marker": "item/datetime"})
            if datetime:
            	datetime = datetime.text

            shop = item.find(attrs={"data-marker": "item/shop"})
            if shop:
            	shop = shop.text
            else:
                shop = ""

            #geo = item.find(attrs={'class': re.compile(r'geo-root')})
            #geo_addr = geo.find(attrs={'class': re.compile(r'geo-address')})
            #if geo_addr:

            geo = ''
            geo_addr = item.find(attrs={"data-marker": "item/georeferences"})
            if geo_addr:
            	spans = geo_addr.find_all('span')
            	for span in spans:
                    if len(span.attrs) == 0:
                    	geo += span.text

            res.append({"id": id,
                        "href": href,
                        "title": title,
                        "price": price,
                        "georeferences": geo,
                        "datetime": datetime,
                        "shop": shop})
                        
        return res

    def set_full_info(self, items):
        time.sleep(random.randint(5, 8))

        for item in items:
            page = self.session.get("https://avito.ru" + item["href"]).text
            #print(page)
            regexp = r'<meta name=\"description\" content=\"[\s\S]*?на[\s\S]{1}Авито\. ([\s\S]*?)\" \/><meta'
            result = re.findall(regexp, page)
            item["descr"] = ""
            if len(result) > 0:
                item["descr"] = result[0].replace("\xa0", " ")

            print("https://avito.ru" + item["href"])
            time.sleep(random.randint(2, 8))

