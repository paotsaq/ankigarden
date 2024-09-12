import requests_cache
import requests
from bs4 import (
    BeautifulSoup,
        )
from bs4.element import (
        Tag
        )

SUBSECTIONS = [
        'Noun',
        'Adjective'
        ]


def cached_request_wrapper():
    session = requests_cache.CachedSession('demo_cache')
    return session


def fetch_wiktionary_page(page_title: str) -> BeautifulSoup | bool:
    target_lang = "Danish"
    base_url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text",
        "utf8": 1,
        "formatversion": 2,
    }
    session = cached_request_wrapper()
    # NOTE quick caching
    # response = requests.get(base_url, params=params)
    response = session.get(base_url, params=params)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.json()["parse"]["text"], 'lxml')
        return soup
    else:
        print(f"Failed to fetch page content. Status code: {response.status_code}")
        return False


def retrieve_toc_from_soup(soup) -> Tag | bool:
    toc = soup.find('div', id='toc')
    if toc:
        print("Table of Contents found.")
        return toc
    else:
        print("Table of Contents not found.")
        return False

        
def find_target_lang_section_in_toc(toc, target_lang) -> Tag | bool:
    tl_section = (toc.find('span',
                           string=target_lang).parent.parent
                  if toc.find('span', string=target_lang) else None)
        
    if tl_section:
        print(f"{target_lang} section exists.")
        return tl_section
    else:
        print(f"{target_lang} section not found in TOC. Definition might be missing?")
        return False


def retrieve_target_lang_subsections(target_lang: str, soup, relevant=True) -> list[Tag] | bool:
    target_lang_wiki_sections = soup.find('h2', id=target_lang)
    # NOTE target section exists and every sibling between this element
    # and next h2 will belong to target
    if target_lang_wiki_sections:
        subsections = target_lang_wiki_sections.parent.find_next_siblings("div", "mw-heading mw-heading3")
        if relevant: 
            relevant = list(filter(lambda sub: next(sub.children).string in SUBSECTIONS,
                              subsections))
            return relevant
        else:
            return list(subsections)
    else:
        return False


def get_noun_gender_from_subsection(subsections: list[Tag]) -> str:
    # NOTE this is hardcoded! a any/filter combo would be safer
    noun_info = list(subsections)[0].next_sibling.next_sibling
    gender_divs = noun_info.find("span", "gender")
    return list(gender_divs.descendants)[1]


def get_danish_noun_gender(word: str):
    target_lang = "Danish"
    soup = fetch_wiktionary_page(word)
    toc = retrieve_toc_from_soup(soup)
    target_lang_exists = find_target_lang_section_in_toc(toc, target_lang)
    if target_lang_exists:
        subsections = retrieve_target_lang_subsections(target_lang, soup, True)
        # TODO parse subsections to check category of word
        # NOTE what if a word is a noun + something else?
        gender = get_noun_gender_from_subsection(subsections)
        return gender
