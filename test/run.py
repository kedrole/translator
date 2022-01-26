from typing import List, Tuple
from bs4 import BeautifulSoup
import requests
import os

def get_splitted_fragment_value(fragment: str, placeholder: str, tags_to_replace_list: List[str]) -> Tuple[str, List[str]]:
    ''' Input: "Text <a><b>bold</b> href</a>", "@@"
        Output: ("Text @@@@ bold @@ href @@", ["<a>", "<b>", "</b>", "</a>"] '''
    
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


def main():
    files = os.listdir("input")

    for file in files:
        input = ''
        output = ''

        with open("input/" + file, "r") as f:
            input = f.read().strip()

        with open("output/" + file, "r") as f:
            output = f.read().strip()

        print("INPUT: " + input)
        print("OUPUT: " + output)
        
        tag = BeautifulSoup(input, 'html.parser') 

fragment = "Text <a><b>bold</b> href</a>"
placeholder = "@@"
tags_to_replace_list = ["<br>", "<b>", "</b>", "<a>", "</a>", "<i>", "</i>", "<strong>", "</strong>", "<code>", "</code>", "<span>", "</span>"]

r = get_splitted_fragment_value(fragment, placeholder, tags_to_replace_list)
print(r)