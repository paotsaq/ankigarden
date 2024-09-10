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

def fetch_and_parse_wiktionary_toc(page_title):
    base_url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text",
        "utf8": 1,
        "formatversion": 2,
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        content_html = data["parse"]["text"]
        
        # Parse the HTML content with Beautiful Soup
        soup = BeautifulSoup(content_html, 'lxml')
        
        # Find the Table of Contents
        toc = soup.find('div', id='toc')
        
        if toc:
            print("Table of Contents found.")
            
            # Look for the Danish section in the TOC;
            danish_section = toc.find('span',
                                      string='Danish').parent.parent if toc.find('span', string='Danish') else None
            
            if danish_section:
                print("Danish section exists.")
                target_lang_wiki_sections = soup.find('h2', id="Danish")
                # NOTE target section exists and every sibling between this element
                # and next h2 will belong to target
                if target_lang_wiki_sections:
                    subsections = target_lang_wiki_sections.parent.find_next_siblings("div", "mw-heading mw-heading3")
                    relevant = list(filter(lambda sub: next(sub.children).string in SUBSECTIONS,
                                      subsections))
                    noun_info = relevant[0].next_sibling.next_sibling
                    gender_divs = noun_info.find("span", "gender")
                    print(dir(gender_divs))
                    print(list(gender_divs.descendants)[1])

            else:
                print("Danish section not found in TOC.")
        else:
            print("Table of Contents not found.")
    else:
        print(f"Failed to fetch page content. Status code: {response.status_code}")

# Example usage
fetch_and_parse_wiktionary_toc("franskbrød")

