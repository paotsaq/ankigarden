from apis.wiktionary import *
import unittest
from bs4 import (
    BeautifulSoup,
        )
from bs4.element import (
        Tag
        )

SOURCE_BO_DEFINITION = """<ol><li>to <a href="/wiki/live" title="live">live</a>, <a href="/wiki/reside" title="reside">reside</a>, <a href="/wiki/dwell" title="dwell">dwell</a>
<dl><dd><div class="h-usage-example"><i class="Latn mention e-example" lang="da">Hun <b>bor</b> i London.</i><dl><dd><span class="e-translation">She <b>lives</b> in London.</span></dd></dl></div></dd></dl></li></ol>"""


SOURCE_TALE_CONJUGATION = """<p><span class="headword-line"><strong class="Latn headword" lang="da">tale</strong> (<i>imperative</i> <b class="Latn form-of lang-da imp-form-of" lang="da"><a href="/wiki/tal#Danish" title="tal">tal</a></b>, <i>infinitive</i> <b class="Latn" lang="da">at <strong class="selflink">tale</strong></b>, <i>present tense</i> <b class="Latn form-of lang-da pres-form-of" lang="da"><a href="/wiki/taler#Danish" title="taler">taler</a></b>, <i>past tense</i> <b class="Latn form-of lang-da past-form-of" lang="da"><a href="/wiki/talte#Danish" title="talte">talte</a></b>, <i>perfect tense</i> <b class="Latn form-of lang-da past|part-form-of" lang="da">har <a href="/wiki/talt#Danish" title="talt">talt</a></b>)</span>"""


SOURCE_FRANKS_DEF = """<p>Compound of <i class="Latn mention" lang="da"><a href="/wiki/fransk#Danish" title="fransk">fransk</a></i> +‎ <i class="Latn mention" lang="da"><a href="/wiki/br%C3%B8d#Danish" title="brød">brød</a></i>, after the model of <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/German_language" title="w:German language">German</a></span> <i class="Latn mention" lang="de"><a class="new" href="/w/index.php?title=Franzbrot&amp;action=edit&amp;redlink=1" title="Franzbrot (page does not exist)">Franzbrot</a></i>.</p>"""

EXPECTED_TARGET_SECTION = """<li class="toclevel-1 tocsection-1"><a href="#Danish"><span class="tocnumber">1</span> <span class="toctext">Danish</span></a>
<ul>
<li class="toclevel-2 tocsection-2"><a href="#Etymology"><span class="tocnumber">1.1</span> <span class="toctext">Etymology</span></a></li>
<li class="toclevel-2 tocsection-3"><a href="#Pronunciation"><span class="tocnumber">1.2</span> <span class="toctext">Pronunciation</span></a></li>
<li class="toclevel-2 tocsection-4"><a href="#Noun"><span class="tocnumber">1.3</span> <span class="toctext">Noun</span></a></li>
<li class="toclevel-2 tocsection-5"><a href="#References"><span class="tocnumber">1.4</span> <span class="toctext">References</span></a></li>
</ul>
</li>"""

EXPECTED_MULTIPLE_LANGUAGES_TARGET_SECTION = """<li class="toclevel-1 tocsection-51"><a href="#Danish"><span class="tocnumber">10</span> <span class="toctext">Danish</span></a>
<ul>
<li class="toclevel-2 tocsection-52"><a href="#Pronunciation_6"><span class="tocnumber">10.1</span> <span class="toctext">Pronunciation</span></a></li>
<li class="toclevel-2 tocsection-53"><a href="#Etymology_1_3"><span class="tocnumber">10.2</span> <span class="toctext">Etymology 1</span></a>
<ul>
<li class="toclevel-3 tocsection-54"><a href="#Noun_5"><span class="tocnumber">10.2.1</span> <span class="toctext">Noun</span></a>
<ul>
<li class="toclevel-4 tocsection-55"><a href="#Inflection"><span class="tocnumber">10.2.1.1</span> <span class="toctext">Inflection</span></a></li>
</ul>
</li>
</ul>
</li>
<li class="toclevel-2 tocsection-56"><a href="#Etymology_2_3"><span class="tocnumber">10.3</span> <span class="toctext">Etymology 2</span></a>
<ul>
<li class="toclevel-3 tocsection-57"><a href="#Verb_3"><span class="tocnumber">10.3.1</span> <span class="toctext">Verb</span></a>
<ul>
<li class="toclevel-4 tocsection-58"><a href="#Conjugation"><span class="tocnumber">10.3.1.1</span> <span class="toctext">Conjugation</span></a></li>
</ul>
</li>
</ul>
</li>
</ul>
</li>"""

EXPECTED_SINGLE_ETYMOLOGY_SUBSECTIONS = """[<div class="mw-heading mw-heading3"><h3 id="Etymology">Etymology</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=2" title="Edit section: Etymology"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p>Compound of <i class="Latn mention" lang="da"><a href="/wiki/fransk#Danish" title="fransk">fransk</a></i> +‎ <i class="Latn mention" lang="da"><a href="/wiki/br%C3%B8d#Danish" title="brød">brød</a></i>, after the model of <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/German_language" title="w:German language">German</a></span> <i class="Latn mention" lang="de"><a class="new" href="/w/index.php?title=Franzbrot&amp;action=edit&amp;redlink=1" title="Franzbrot (page does not exist)">Franzbrot</a></i>.
</p>, <div class="mw-heading mw-heading3"><h3 id="Pronunciation">Pronunciation</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=3" title="Edit section: Pronunciation"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p><a href="/wiki/Wiktionary:International_Phonetic_Alphabet" title="Wiktionary:International Phonetic Alphabet">IPA</a><sup>(<a href="/wiki/Appendix:Danish_pronunciation" title="Appendix:Danish pronunciation">key</a>)</sup>: <span class="IPA">[ˈfʁɑnsb̥ʁœðˀ]</span>
</p>, <div class="mw-heading mw-heading3"><h3 id="Noun">Noun</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=4" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p><span class="headword-line"><strong class="Latn headword" lang="da">franskbrød</strong> <span class="gender"><abbr title="neuter gender">n</abbr></span> (<i>singular definite</i> <b class="Latn form-of lang-da def|s-form-of" lang="da"><a class="new" href="/w/index.php?title=franskbr%C3%B8det&amp;action=edit&amp;redlink=1" title="franskbrødet (page does not exist)">franskbrødet</a></b>, <i>plural indefinite</i> <b class="Latn form-of lang-da indef|p-form-of" lang="da"><strong class="selflink">franskbrød</strong></b>)</span>
</p>, <ol><li><a href="/wiki/wheat" title="wheat">wheat</a> <a href="/wiki/bread" title="bread">bread</a></li></ol>, <div class="mw-heading mw-heading3"><h3 id="References">References</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=5" title="Edit section: References"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p>“<a class="external text" href="http://ordnet.dk/ddo/ordbog?query=franskbr%C3%B8d" rel="nofollow">franskbrød</a>” in <i><a class="extiw" href="https://en.wikipedia.org/wiki/da:Den_Danske_Ordbog" title="w:da:Den Danske Ordbog">Den Danske Ordbog</a></i>
</p>]"""

EXPECTED_MULTIPLE_ETYMOLOGIES_SUBSECTIONS = """[<div class="mw-heading mw-heading3"><h3 id="Pronunciation_6">Pronunciation</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=52" title="Edit section: Pronunciation"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <ul><li><a href="/wiki/Wiktionary:International_Phonetic_Alphabet" title="Wiktionary:International Phonetic Alphabet">IPA</a><sup>(<a href="/wiki/Appendix:Danish_pronunciation" title="Appendix:Danish pronunciation">key</a>)</sup>: <span class="IPA">/boː/</span>, <span class="IPA">[b̥oːˀ]</span></li></ul>, <div class="mw-heading mw-heading3"><h3 id="Etymology_1_3">Etymology 1</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=53" title="Edit section: Etymology 1"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p>From <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Old_Norse" title="w:Old Norse">Old Norse</a></span> <i class="Latn mention" lang="non"><a href="/wiki/b%C3%BA#Old_Norse" title="bú">bú</a></i>, from <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Old_Norse" title="w:Old Norse">Old Norse</a></span> <i class="Latn mention" lang="non"><a href="/wiki/b%C3%BAa#Old_Norse" title="búa">búa</a></i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">to reside</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>.
</p>, <div class="mw-heading mw-heading4"><h4 id="Noun_5">Noun</h4><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=54" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p><span class="headword-line"><strong class="Latn headword" lang="da">bo</strong> <span class="gender"><abbr title="neuter gender">n</abbr></span> (<i>singular definite</i> <b class="Latn form-of lang-da def|s-form-of" lang="da"><a href="/wiki/boet#Danish" title="boet">boet</a></b>, <i>plural indefinite</i> <b class="Latn form-of lang-da indef|p-form-of" lang="da"><a href="/wiki/boer#Danish" title="boer">boer</a></b>)</span>
</p>, <ol><li><a href="/wiki/estate" title="estate">estate</a> <span class="gloss-brac">(</span><span class="gloss-content"><span class="Latn" lang="en">the property of a deceased person</span></span><span class="gloss-brac">)</span></li>
<li><a href="/wiki/den" title="den">den</a>, <a href="/wiki/nest" title="nest">nest</a></li>
<li><a href="/wiki/abode" title="abode">abode</a>, <a href="/wiki/home" title="home">home</a></li></ol>, <div class="mw-heading mw-heading5"><h5 id="Inflection">Inflection</h5><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=55" title="Edit section: Inflection"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="NavFrame">
<div class="NavHead">Declension of <i class="Latn mention" lang="da">bo</i></div>
<div class="NavContent">
<table class="inflection-table" style="text-align:center;width:100%;">
<tbody><tr style="background-color:#eee;">
<th rowspan="2">neuter<br/>gender
</th>
<th colspan="2"><i>Singular</i>
</th>
<th colspan="2"><i>Plural</i>
</th></tr>
<tr style="font-size:90%;background-color:#eee;">
<th style="width:25%;"><i>indefinite</i>
</th>
<th style="width:25%;"><i>definite</i>
</th>
<th style="width:25%;"><i>indefinite</i>
</th>
<th style="width:25%;"><i>definite</i>
</th></tr>
<tr>
<th style="background-color:#eee;"><i><a href="/wiki/nominative_case" title="nominative case">nominative</a></i>
</th>
<td style="background-color:#f9f9f9;"><span class="Latn" lang="da"><strong class="selflink">bo</strong></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da def|s-form-of" lang="da"><a href="/wiki/boet#Danish" title="boet">boet</a></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da indef|p-form-of" lang="da"><a href="/wiki/boer#Danish" title="boer">boer</a></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da def|p-form-of" lang="da"><a href="/wiki/boerne#Danish" title="boerne">boerne</a></span>
</td></tr>
<tr>
<th style="background-color:#eee;"><i><a href="/wiki/genitive_case" title="genitive case">genitive</a></i>
</th>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da indef|gen|s-form-of" lang="da"><a href="/wiki/bos#Danish" title="bos">bos</a></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da def|gen|s-form-of" lang="da"><a href="/wiki/boets#Danish" title="boets">boets</a></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da indef|gen|p-form-of" lang="da"><a href="/wiki/boers#Danish" title="boers">boers</a></span>
</td>
<td style="background-color:#f9f9f9;"><span class="Latn form-of lang-da def|gen|p-form-of" lang="da"><a href="/wiki/boernes#Danish" title="boernes">boernes</a></span>
</td></tr></tbody></table>
</div></div>, <div class="mw-heading mw-heading3"><h3 id="Etymology_2_3">Etymology 2</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=56" title="Edit section: Etymology 2"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p>From <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Old_Norse" title="w:Old Norse">Old Norse</a></span> <i class="Latn mention" lang="non"><a href="/wiki/b%C3%BAa#Old_Norse" title="búa">búa</a></i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">to reside</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>, from <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Proto-Germanic_language" title="w:Proto-Germanic language">Proto-Germanic</a></span> <i class="Latn mention" lang="gem-pro"><a href="/wiki/Reconstruction:Proto-Germanic/b%C5%ABan%C4%85" title="Reconstruction:Proto-Germanic/būaną">*būaną</a></i>, cognate with <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Norwegian_language" title="w:Norwegian language">Norwegian</a></span> <i class="Latn mention" lang="no"><a class="mw-selflink-fragment" href="#Norwegian">bo</a></i>, <i class="Latn mention" lang="no"><a href="/wiki/bu#Norwegian" title="bu">bu</a></i>, <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Swedish_language" title="w:Swedish language">Swedish</a></span> <i class="Latn mention" lang="sv"><a class="mw-selflink-fragment" href="#Swedish">bo</a></i>, <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/German_language" title="w:German language">German</a></span> <i class="Latn mention" lang="de"><a href="/wiki/bauen#German" title="bauen">bauen</a></i>, <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Dutch_language" title="w:Dutch language">Dutch</a></span> <i class="Latn mention" lang="nl"><a href="/wiki/bouwen#Dutch" title="bouwen">bouwen</a></i>, <span class="etyl"><a class="extiw" href="https://en.wikipedia.org/wiki/Gothic_language" title="w:Gothic language">Gothic</a></span> <i class="Goth mention" lang="got"><a href="/wiki/%F0%90%8C%B1%F0%90%8C%B0%F0%90%8C%BF%F0%90%8C%B0%F0%90%8C%BD#Gothic" title="𐌱𐌰𐌿𐌰𐌽">𐌱𐌰𐌿𐌰𐌽</a></i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-tr tr Latn" lang="got-Latn"><a href="/wiki/bauan#Gothic" title="bauan">bauan</a></span><span class="mention-gloss-paren annotation-paren">)</span>.
</p>, <div class="mw-heading mw-heading4"><h4 id="Verb_3">Verb</h4><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=57" title="Edit section: Verb"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <p><span class="headword-line"><strong class="Latn headword" lang="da">bo</strong> (<i>present tense</i> <b class="Latn" lang="da"><a href="/wiki/bor#Danish" title="bor">bor</a></b>, <i>past tense</i> <b class="Latn" lang="da"><a href="/wiki/boede#Danish" title="boede">boede</a></b>, <i>past participle</i> <b class="Latn" lang="da"><a href="/wiki/boet#Danish" title="boet">boet</a></b>)</span>
</p>, <ol><li>to <a href="/wiki/live" title="live">live</a>, <a href="/wiki/reside" title="reside">reside</a>, <a href="/wiki/dwell" title="dwell">dwell</a>
<dl><dd><div class="h-usage-example"><i class="Latn mention e-example" lang="da">Hun <b>bor</b> i London.</i><dl><dd><span class="e-translation">She <b>lives</b> in London.</span></dd></dl></div></dd></dl></li></ol>, <div class="mw-heading mw-heading5"><h5 id="Conjugation">Conjugation</h5><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=bo&amp;action=edit&amp;section=58" title="Edit section: Conjugation"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="NavFrame">
<div class="NavHead">Inflection of <i class="Latn mention" lang="da">bo</i></div>
<div class="NavContent">
<table class="inflection-table" style="border-collapse:separate; background:#F0F0F0; text-align:center; width:100%; border-spacing:2px">
<tbody><tr>
<th>
</th>
<th colspan="1">present
</th>
<th colspan="1">past
</th></tr>
<tr>
<th colspan="1" style="background:#c0cfe4">simple
</th>
<td><span class="Latn form-of lang-da pres-form-of" lang="da"><a href="/wiki/bor#Danish" title="bor">bor</a></span>
</td>
<td><span class="Latn form-of lang-da past-form-of" lang="da"><a href="/wiki/boede#Danish" title="boede">boede</a></span>
</td></tr>
<tr>
<th colspan="1" style="background:#c0cfe4">perfect
</th>
<td><span class="Latn" lang="da"><a href="/wiki/har#Danish" title="har">har</a></span> boet
</td>
<td><span class="Latn" lang="da"><a href="/wiki/havde#Danish" title="havde">havde</a></span> boet
</td></tr>
<tr>
<th colspan="1" style="background:#c0cfe4">passive
</th>
<td>—
</td>
<td>—
</td></tr>
<tr>
<th colspan="1" style="background:#c0cfe4">participle
</th>
<td><span class="Latn form-of lang-da pres|ptcp-form-of" lang="da"><a href="/wiki/boende#Danish" title="boende">boende</a></span>
</td>
<td><span class="Latn form-of lang-da past|part-form-of" lang="da"><a href="/wiki/boet#Danish" title="boet">boet</a></span>
</td></tr>
<tr>
<th colspan="1" style="background:#e2e4c0">imperative
</th>
<td><span class="Latn form-of lang-da imp-form-of" lang="da"><strong class="selflink">bo</strong></span>
</td>
<td>—
</td></tr>
<tr>
<th colspan="1" style="background:#e2e4c0">infinitive
</th>
<td><span class="Latn" lang="da"><strong class="selflink">bo</strong></span>
</td>
<td>—
</td></tr>
<tr>
<th colspan="1" style="background:#e2e4c0">auxiliary verb
</th>
<td><span class="Latn" lang="da"><a href="/wiki/have#Danish" title="have">have</a></span>
</td>
<td>—
</td></tr>
<tr>
<th colspan="1" style="background:#e2e4c0">gerund
</th>
<td><span class="Latn form-of lang-da ger-form-of" lang="da"><a href="/wiki/boen#Danish" title="boen">boen</a></span>
</td>
<td>—
</td></tr></tbody></table>
</div></div>]"""

EXPECTED_ALL_SUBSECTIONS = """[<div class="mw-heading mw-heading3"><h3 id="Etymology">Etymology</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=2" title="Edit section: Etymology"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="Pronunciation">Pronunciation</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=3" title="Edit section: Pronunciation"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="Noun">Noun</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=4" title="Edit section: Noun"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>, <div class="mw-heading mw-heading3"><h3 id="References">References</h3><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=franskbr%C3%B8d&amp;action=edit&amp;section=5" title="Edit section: References"><span>edit</span></a><span class="mw-editsection-bracket">]</span></span></div>]"""

SOURCE_BEGYNDTE = """<ol><li><span class="form-of-definition use-with-mention"><a href="/wiki/Appendix:Glossary#past_tense" title="Appendix:Glossary">past</a> of <span class="form-of-definition-link"><i class="Latn mention" lang="da"><a href="/wiki/begynde#Danish" title="begynde">begynde</a></i></span></span></li></ol>"""

class TestWiktionaryStepRequests(unittest.TestCase):

    def test_can_fetch_wikipedia_page(self):
        word = "franskbrød"
        soup = fetch_wiktionary_page(word)
        self.assertTrue(soup is not False)

    def test_can_retrieve_toc_from_wiktionary_page(self):
        word = "franskbrød"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        self.assertTrue(isinstance(toc, Tag))

    def test_can_find_Danish_section_in_single_language_soup(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        self.assertEqual(target_section.__repr__(), EXPECTED_TARGET_SECTION)

    def test_can_find_Danish_section_in_multiple_languages_soup(self):
        word = "bo"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        self.assertEqual(target_section.__repr__(), EXPECTED_MULTIPLE_LANGUAGES_TARGET_SECTION)


    def test_can_retrieve_target_lang_subsections_single_etymology_result(self):
        self.maxDiff = None
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        self.assertEqual(subs.__repr__(),EXPECTED_SINGLE_ETYMOLOGY_SUBSECTIONS)
        self.assertTrue(isinstance(subs, list), EXPECTED_SINGLE_ETYMOLOGY_SUBSECTIONS)


    def test_can_retrieve_target_lang_subsections_multiple_etymologies_results(self):
        self.maxDiff = None
        word = "bo"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        self.assertEqual(subs.__repr__(),EXPECTED_MULTIPLE_ETYMOLOGIES_SUBSECTIONS)


    def test_number_of_definitions_for_single_definition(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)

    def test_can_identify_verb_conjugation(self):
        EXPECTED = (True, "begynde")
        soup = BeautifulSoup(SOURCE_BEGYNDTE, features="lxml")
        self.assertEqual(EXPECTED, check_if_term_is_conjugation(soup))

    def test_can_parse_html_from_text_content(self):
        EXPECTED = "Compound of fransk +\u200e brød, after the model of German Franzbrot."
        self.assertEqual(EXPECTED, retrieve_content_from_tag(BeautifulSoup(SOURCE_FRANKS_DEF, features="lxml")))

    def test_can_remove_usage_example_from_definition(self):
        EXPECTED = "to live, reside, dwell"
        self.assertEqual(EXPECTED, retrieve_definition_from_tag(BeautifulSoup(SOURCE_BO_DEFINITION,features="lxml")))

    def test_can_retrieve_danish_verb_conjugation(self):
        EXPECTED = {
                "imperative": "tal",
                "infinitive": "at tale",
                "present tense": "taler",
                "past tense": "talte",
                "perfect tense": "har talt"
                }
        self.assertEqual(get_verb_conjugation_from_subsection(BeautifulSoup(SOURCE_TALE_CONJUGATION, features="lxml")), EXPECTED)

    def test_can_retrieve_target_lang_noun_single_definition(self):
        word = "franskbrød"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        res_dict = get_word_categories_from_subsections(subs, [], {})
        self.assertEqual(res_dict, [{"etymology": "Compound of fransk +\u200e brød, after the model of German Franzbrot.",
                                    "type": "noun",
                                    "gender": "n",
                                    "definition": ["wheat bread"]
                         }])

    def test_can_retrieve_target_lang_noun_multiple_definition(self):
        word = "trivsel"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        res_dict = get_word_categories_from_subsections(subs, [], {})
        self.assertEqual(res_dict, [{"etymology": "Verbal noun to trives (“to thrive”).",
                                    "type": "noun",
                                    "gender": "c",
                                    "definition": ["well-being", "growth, prosperity"]
                         }])

    def test_can_retrieve_target_lang_multiple_word_role(self):
        self.maxDiff = None
        word = "tale"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        res_dict = get_word_categories_from_subsections(subs, [], {})
        self.assertEqual(res_dict, [{"etymology": "From Old Norse tala.",
                                     "type": "noun",
                                     "gender": "c",
                                     "definition": ["speech, talk, address, discourse"]},
                                    {"etymology": "From Old Norse tala.",
                                     "type": "verb",
                                     "conjugation": {
                                         "imperative": "tal",
                                         "infinitive": "at tale",
                                         "present tense": "taler",
                                         "past tense": "talte",
                                         "perfect tense": "har talt"
                                         },
                                     "definition": ['to make a speech', 'to speak, talk']
                         }])

    def test_can_retrieve_target_lang_multiple_etymologies(self):
        word = "bo"
        language = "Danish"
        soup = fetch_wiktionary_page(word)
        toc = retrieve_toc_from_soup(soup)
        target_section = find_target_lang_section_in_toc(toc, language)
        subs = retrieve_target_lang_subsections(language, soup)
        res_dict = get_word_categories_from_subsections(subs, [], {})
        self.assertEqual(res_dict, [{'etymology': 'From Old Norse bú, from Old Norse búa (“to reside”).',
                                     'type': 'noun',
                                     'gender': 'n',
                                     'definition': [
                                         'estate (the property of a deceased person)',
                                         'den, nest',
                                         'abode, home']},
                                    {'etymology': 'From Old Norse búa (“to reside”), from Proto-Germanic *būaną, cognate with Norwegian bo, bu, Swedish bo, German bauen, Dutch bouwen, Gothic 𐌱𐌰𐌿𐌰𐌽 (bauan).',
                                     'type': 'verb',
                                     'conjugation': {
                                         'present tense': 'bor',
                                         'past tense': 'boede'
                                         },
                                     'definition': [
                                         'to live, reside, dwell']
                                     }])

    def test_can_get_definition_from_word(self):
        word = "tale"
        language = "Danish"
        res_dict = get_word_definition(word, language)
        self.assertEqual(res_dict, [{"etymology": "From Old Norse tala.",
                                     "type": "noun",
                                     "gender": "c",
                                     "definition": ["speech, talk, address, discourse"]},
                                    {"etymology": "From Old Norse tala.",
                                     "type": "verb",
                                     "conjugation": {
                                         "imperative": "tal",
                                         "infinitive": "at tale",
                                         "present tense": "taler",
                                         "past tense": "talte",
                                         "perfect tense": "har talt"
                                         },
                                     "definition": ['to make a speech', 'to speak, talk']
                         }])

    def test_can_identify_verb_conjugation_in_full_query(self):
        word = "begyndte"
        language = "Danish"
        res_dict = get_word_definition(word, language)
        self.assertEqual(res_dict, [{'parent': 'begynde', 'type': 'conjugation'}])

    def test_can_identify_adjective_in_full_query(self):
        word = "kræsen"
        language = "Danish"
        res_dict = get_word_definition(word, language)
        self.assertEqual(res_dict, [{'etymology': 'From kræse +\u200e -en. Compare Swedish kräsen.',
                                     'type': 'adjective',
                                     'definition': ['particular (about food), choosy, picky']}])

    def test_can_identify_many_categories_in_full_query(self):
        word = "engang"
        language = "Danish"
        res_dict = get_word_definition(word, language)
        self.assertEqual(res_dict, [{'definition': ['once, one day, at one time',
                                                    'sometime, some day, one day',
                                                    '(negative) even'],
                                     'type': 'adverb'},
                                    {'definition': ['at some unspecified time in the past when...'],
                                     'type': 'conjunction'}])

    def test_can_parse_name_without_gender_information(self):
        word = "drikke"
        language = "Danish"
        res_dict = get_word_definition(word, language)
        self.assertEqual(res_dict,
                         [{'etymology': 'From Old Danish drikkæ, (Western) Old Norse drekka, from Proto-Germanic *drinkaną, cognate with Swedish dricka, English drink, German trinken.', 'type': 'verb', 'conjugation': {'imperative': 'drik'}, 'definition': ['drink', 'have (to partake of a drink)']},
                          {'etymology': 'From Old Danish drickæ, from the verb.', 'type': 'noun', 'gender': None, 'definition': ['(rare) drink']},
                          {'etymology': 'See the etymology of the corresponding lemma form.', 'type': 'noun', 'gender': 'c', 'definition': ['indefinite plural of drik']}])
                         

    # NOTE still not sure whether it is necessary to check the declension table
    # (and often there is none); at least for nouns, the declension rules are clear,
    # and words like 'cykel/cyklen' are just an exception.
    def test_can_retrieve_target_lang_declension_subsections(self):
        pass

    # def test_can_retrieve_target_lang_noun_many_definitions(self):
        # word = "bo"
        # language = "Danish"
        # soup = fetch_wiktionary_page(word)
        # toc = retrieve_toc_from_soup(soup)
        # target_section = find_target_lang_section_in_toc(toc, language)
        # subs = retrieve_target_lang_subsections(language, soup, relevant=True)
        # get_noun_definition_from_subsection(subs)

    # def test_can_retrieve_danish_word_gender(self):
        # word = "franskbrød"
        # language = "Danish"
        # soup = fetch_wiktionary_page(word)
        # toc = retrieve_toc_from_soup(soup)
        # target_section = find_target_lang_section_in_toc(toc, language)
        # subs = retrieve_target_lang_subsections(language, soup, relevant=True)
        # gender = get_noun_gender_from_subsection(subs)
        # self.assertEqual(gender, 'n')



# class TestWiktionarRoutineRequests(unittest.TestCase):

    # def test_routine_danish_gender_neuter_noun(self):
        # self.assertEqual(get_danish_noun_gender("franskbrød"), 'n')

    # def test_routine_danish_gender_common_noun(self):
        # self.assertEqual(get_danish_noun_gender("bil"), 'c')


if __name__ == "__main__":
    unittest.main(failfast=True)
