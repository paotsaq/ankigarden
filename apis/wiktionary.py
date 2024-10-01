import requests_cache
import requests
from bs4 import (
    BeautifulSoup,
        )
from bs4.element import (
        Tag,
        NavigableString,
        Comment
        )
from itertools import takewhile
import re
from typing import Tuple
from logger import logger

SUBSECTIONS = [
        'Noun',
        'Adjective',
        'Preposition',
        'Adverb',
        'Verb',
        'Conjunction'
        ]


def cached_request_wrapper():
    session = requests_cache.CachedSession('demo_cache')
    return session


def fetch_wiktionary_page(page_title: str, target_lang: str = "Danish") -> BeautifulSoup | bool:
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
    try:
        response = session.get(base_url, params=params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.json()["parse"]["text"], 'lxml')
            logger.debug(f"Successfully queried Wiktionary for {page_title}")
            return soup
        else:
            logger.error(f"Failed to fetch page content. Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to Wiktionary API. Am I connected to the internet?")
        return False


def retrieve_toc_from_soup(soup) -> Tag | bool:
    toc = soup.find('div', id='toc')
    if toc:
        # print("Table of Contents found.")
        return toc
    else:
        print("Table of Contents not found.")
        return False

        
def find_target_lang_section_in_toc(toc, target_lang) -> Tag | bool:
    # NOTE this might be unnecessary; one could try to look directly
    # into the DOM.
    tl_section = (toc.find('span',
                           string=target_lang).parent.parent
                  if toc.find('span', string=target_lang) else None)
        
    if tl_section:
        # print(f"{target_lang} section exists.")
        return tl_section
    else:
        print(f"{target_lang} section not found in TOC. Definition might be missing?")
        return False


def retrieve_target_lang_subsections(target_lang: str, soup, relevant=True) -> list[Tag | NavigableString] | bool:
    target_lang_wiki_sections = soup.find('h2', id=target_lang)
    # note target section exists and every sibling between this element
    # and next h2 will belong to target
    if target_lang_wiki_sections:
        # NOTE every sibling between found element and next h2 / end of page is to be fetched
        all_content = takewhile(
            lambda elem: not (isinstance(elem, Tag) and 
                            elem.has_attr("class") and "mw-heading2" in elem["class"]),
            target_lang_wiki_sections.parent.next_siblings
            )
        all_subsections = filter(lambda elem: not(elem == '\n' or isinstance(elem, Comment)),
                                 all_content)
        return list(all_subsections)
    else:
        # NOTE should we want to do something else? ie. signal the possibility of updating Wiki further?
        logger.error(f"{target_lang} section not found in DOM. Definition might be missing?")
        return False


def retrieve_content_from_tag(html_tag: Tag):
    soup = BeautifulSoup(html_tag.get_text(), features="lxml")
    return soup.get_text().strip()


def retrieve_definition_from_tag(html_tag: Tag):
    # Wiktionary formats its definitions using <dl> tags.
    # thus, they should be supressed
    # NOTE object is directly modified!
    if html_tag.dl is not None:
        html_tag.dl.decompose()
    return retrieve_content_from_tag(html_tag)


def check_if_term_is_conjugation(subsection: Tag) -> Tuple[bool] | Tuple[bool | str]:
    target_elements = subsection.find_all("li")
    if target_elements:
        verb_link = target_elements[0].find('span', class_='form-of-definition-link')
        if verb_link and verb_link.get_text():
            return (True, verb_link.get_text().strip())
    return (False, "")


def get_verb_conjugation_from_subsection(subsection: Tag):
    # NOTE this is parsing the definition verb header, and
    # not the conjugation table: the latter might be a better option
    pattern = r'(imperative|infinitive|present tense|past tense|perfect tense)\s+(.*?)\s*(?:,|$)'
    
    raw_text = retrieve_content_from_tag(subsection)
    paren_content = raw_text[raw_text.find('(') + 1:-1]

    matches = re.findall(pattern, paren_content, flags=re.IGNORECASE)
    
    return {
        conj_type.strip().lower(): conj_value.strip()
        for conj_type, conj_value in matches
    }


def get_word_categories_from_subsections(
        subsections: list[Tag],
        categories: list[dict],
        current_entry: dict
        ) -> list[dict]:
    if subsections == []:
        return categories
    head = subsections[0]
    # print(f"categories: {categories}; current_entry: {current_entry}")
    if head.has_attr("class") and "mw-heading" in head["class"]:
        # NOTE this is how to hackily retrieve the identifier of which subsection to handle
        subsection = next(head.children)["id"].split("_")[0]
        if subsection == "Etymology":
            etymology_paragraph = subsections[1]
            new_entry = {"etymology": retrieve_content_from_tag(etymology_paragraph)}
            return get_word_categories_from_subsections(subsections[2:], categories, new_entry)
        elif subsection in SUBSECTIONS:
            # TODO some of this code is rather redundant
            # (type can certainly be got before the if/else branches)
            if subsection == "Noun":
                gender_info = retrieve_content_from_tag(subsections[1].find("span", "gender"))
                definition = retrieve_definition_from_tag(subsections[2]).split("\n")
                new_info = {
                        "type": subsection.lower(),
                        "gender": gender_info,
                        "definition": definition
                        }
            elif subsection == "Verb":
                # NOTE in case the term is itself a conjugation,
                # there's much less information to retrieve
                # print(subsections[0])
                # print(subsections[1])
                term_is_conjugation, parent = check_if_term_is_conjugation(subsections[2])
                if term_is_conjugation:
                    new_info = {
                            "type": "conjugation",
                            "parent": parent,
                            }
                else:
                    conjugation = get_verb_conjugation_from_subsection(subsections[1])
                    definition = retrieve_definition_from_tag(subsections[2]).split("\n")
                    new_info = {
                            "type": subsection.lower(),
                            "conjugation": conjugation,
                            "definition": definition
                            }
            elif subsection in ["Adverb", "Conjunction", "Adjective"]:
                definition = retrieve_definition_from_tag(subsections[2]).split("\n")
                new_info = {
                        "type": subsection.lower(),
                        "definition": definition
                        }

            # NOTE must check whether `current_entry` already has an etymology;
            # if it does — the usual case — just keep adding information to the `dict` object
            # otherwise, retrieve it from the last entry
            if ("etymology" not in current_entry.keys() and 
                len(categories) >= 1 and "etymology" in categories[-1] and
                not (subsection == "Verb" and term_is_conjugation)):
                new_info["etymology"] = categories[-1]["etymology"]
            return get_word_categories_from_subsections(subsections[3:], categories + [current_entry | new_info], {})
        else:
            return get_word_categories_from_subsections(subsections[2:], categories, current_entry)


def get_word_definition(word: str, language: str = "Danish") -> dict | bool:
    soup = fetch_wiktionary_page(word)
    if not soup:
        logger.error(f"Failed to get word definition from Wiktionary for {word}.")
        return False
    # toc = retrieve_toc_from_soup(soup)
    # target_section = find_target_lang_section_in_toc(toc, language)
    subs = retrieve_target_lang_subsections(language, soup)
    res_dict = get_word_categories_from_subsections(subs, [], {})
    return res_dict
