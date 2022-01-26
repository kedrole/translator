from typing import List, Tuple
import urllib.parse
from bs4 import BeautifulSoup
import undetected_chromedriver.v2 as uc
import time

def get_fragments_translations(fragments_list: List[str]) -> List[str]:
    ''' Get translations of fragments of code strings 
        Input: ["Text <a>href</a>", "<b>Sun</b>"] 
        Output: ["Текст <a>ссылка</a>, "<b>Солнце</b>"] '''
    
    def get_translated_with_code_tags(translated_text, full_tags_list, tag_placeholder):
        for tag in full_tags_list:
            translated_text = translated_text.replace(tag_placeholder, tag, 1)
        return translated_text

    def prepare_fragments(fragments_list, tag_placeholder):
        def get_splitted_fragment_value(fragment: str, placeholder: str, tags_to_replace_list: List[str]) -> Tuple[str, List[str]]:
            ''' Input: "Text <a><b>bold</b> href</a>", "@"
                Output: ("Text @@bold@ href@", ["<a>", "<b>", "</b>", "</a>"] '''
            
            def find_all(a_str, sub):
                start = 0
                while True:
                    start = a_str.find(sub, start)
                    if start == -1: return
                    yield start
                    start += len(sub)

            # list of tag occurences: ('tag: str, index: int)
            all_occurences_tuples_list = []
            for tag in tags_to_replace_list:
                match_indexes = find_all(fragment, tag)
                for match_idx in match_indexes:
                    all_occurences_tuples_list.append((tag, match_idx))

            all_occurences_tuples_list = sorted(all_occurences_tuples_list, key=lambda tag_index: tag_index[1], reverse=False)
            for (tag, index) in all_occurences_tuples_list:
                fragment = fragment.replace(tag, placeholder, 1)

            tags_list = [tag for (tag, _) in all_occurences_tuples_list]
            return (fragment, tags_list)

        prepared_fragments_list = []
        full_tags_list = []

        tags_to_replace_list = ["<br>", "<b>", "</b>", "<a>", "</a>", "<i>", "</i>", "<strong>", "</strong>", "<code>", "</code>", "<span>", "</span>"]

        for fragment in fragments_list:
            (fragment_str, tags_list) = get_splitted_fragment_value(fragment, tag_placeholder, tags_to_replace_list)
            full_tags_list.extend(tags_list)
            prepared_fragments_list.append(fragment_str)
        return (prepared_fragments_list, full_tags_list)

    tag_placeholder = "@@"
    (prepared_fragments_list, full_tags_list) = prepare_fragments(fragments_list, tag_placeholder)

    fragment_separator = "$$$"
    prepared_text = fragment_separator.join(prepared_fragments_list)

    translated_text = get_translation(prepared_text)
    translated_with_code_tags = get_translated_with_code_tags(translated_text, full_tags_list, tag_placeholder)
    translated_fragments = translated_with_code_tags.split(fragment_separator)

    assert len(fragments_list) == len(translated_fragments)

    return translated_fragments

def get_translation(text):
    driver = uc.Chrome()

    text = urllib.parse.quote(text)
    #return "http://translate.yandex.ru/?lang=en-ru&text=" + text

    try:
        driver.get("https://translate.yandex.ru/?lang=en-ru&text=" + text)
    
        html = driver.page_source
        with open("html.html", "w") as f:
            f.write(html)

        if "Нам очень жаль, но запросы с вашего устройства похожи на автоматические" in html:
            raise Exception("Автоматические запросы")

        assert "fullTextTranslation" in html
        assert "data-complaint-type" in html

        time.sleep(2)
        translation = BeautifulSoup(html, 'html.parser').find('span', attrs={"data-complaint-type": "fullTextTranslation"}).text
    
        return translation
    except Exception as e:
        raise e
    finally:
        driver.quit()


if __name__ == "__main__":
    texts_list = ["Text <a>href</a>", "Text <a><b>bold</b> href</a>"]

    t = get_fragments_translations(texts_list)

    print(t)
