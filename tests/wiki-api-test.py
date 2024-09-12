from apis.wiktionary import *
import unittest
from bs4 import (
    BeautifulSoup,
        )
from bs4.element import (
        Tag
        )


EXPECTED_TARGET_SECTION = """<li class="toclevel-1 tocsection-1"><a href="#Danish"><span class="tocnumber">1</span> <span class="toctext">Danish</span></a>
<ul>
<li class="toclevel-2 tocsection-2"><a href="#Etymology"><span class="tocnumber">1.1</span> <span class="toctext">Etymology</span></a></li>
<li class="toclevel-2 tocsection-3"><a href="#Pronunciation"><span class="tocnumber">1.2</span> <span class="toctext">Pronunciation</span></a></li>
<li class="toclevel-2 tocsection-4"><a href="#Noun"><span class="tocnumber">1.3</span> <span class="toctext">Noun</span></a></li>
<li class="toclevel-2 tocsection-5"><a href="#References"><span class="tocnumber">1.4</span> <span class="toctext">References</span></a></li>
</ul>
</li>"""

EXPECTED_RELEVANT_SUBSECTIONS = """[<div class="mw-heading mw-heading3"><h3 id="Noun">Noun</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=4" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>]"""

EXPECTED_ALL_SUBSECTIONS = """[<div class="mw-heading mw-heading3"><h3 id="Etymology">Etymology</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=2" title="Edit section: Etymology"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="Pronunciation">Pronunciation</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=3" title="Edit section: Pronunciation"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="Noun">Noun</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=4" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="References">References</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=5" title="Edit section: References"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>]"""



class TestWiktionaryRequests(unittest.TestCase):

    def test_can_fetch_wikipedia_page(self):
        word = "franskbrød"
        soup = fetch_wiktionary_page(word)
        self.assertTrue(soup is not False)

    def test_can_retrieve_toc_from_wiktionary_page(self):
        word = "franskbrød"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        self.assertTrue(isinstance(toc, Tag))

    def test_can_find_Danish_section_in_soup(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        self.assertEqual(target_section.__repr__(), EXPECTED_TARGET_SECTION)

    def test_can_retrieve_target_lang_subsections(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        # NOTE relevant bool will filter some sections out
        subs = retrieve_target_lang_subsections(language, soup, relevant=True)
        self.assertEqual(subs.__repr__(),EXPECTED_RELEVANT_SUBSECTIONS)
        self.assertTrue(isinstance(subs, list), EXPECTED_RELEVANT_SUBSECTIONS)

        all_subs = retrieve_target_lang_subsections(language, soup, relevant=False)
        self.assertEqual(all_subs.__repr__(),EXPECTED_ALL_SUBSECTIONS)
        self.assertTrue(isinstance(all_subs, list), EXPECTED_ALL_SUBSECTIONS)

    def test_can_retrieve_danish_word_gender(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup, relevant=True)
        gender = get_noun_gender_from_subsection(subs)
        self.assertEqual(gender, 'n')

    def test_routine_danish_gender_noun(self):
        self.assertEqual(get_danish_noun_gender("franskbrød"), 'n')

if __name__ == "__main__":
    unittest.main(failfast=True)
