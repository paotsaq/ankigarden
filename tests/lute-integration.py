import pytest
from datetime import datetime
from db.objects import Flashcard, LuteEntry
from apis.anki_database import (
        create_flashcard_from_lute_entry,
        parse_lute_term_output
        )

@pytest.fixture
def sample_lute_lines():
    return [
        "høj,,high / tall,Danish,adjective,2024-08-21 23:00:13,1,,",
        "lugte,,to smell,Danish,verb,2024-08-21 23:00:43,1,,",
        "tynd,,thin,Danish,adjective,2024-08-21 22:59:48,1,,",
        "kone,,wife / woman,Danish,\"common-noun, noun\",2024-08-17 16:48:46,1,,",
    ]

def test_parse_single_line_of_prompt():
    line = "høj,,high / tall,Danish,adjective,2024-08-21 23:00:13,1,,"
    expected = {
        'term': 'høj',
        'parent': '',
        'translation': 'high / tall',
        'language': 'Danish',
        'tags': 'adjective',
        'added': '2024-08-21 23:00:13',
        'status': '1',
        'link_status': '',
        'pronunciation': ''
    }
    assert parse_lute_term_output(line) == expected

def test_create_lute_entry_from_parsed_line():
    parsed_line = {
        'term': 'høj',
        'parent': '',
        'translation': 'high / tall',
        'language': 'Danish',
        'tags': 'adjective',
        'added': '2024-08-21 23:00:13',
        'status': '1',
        'link_status': '',
        'pronunciation': ''
    }
    lute_entry = LuteEntry.from_dict(parsed_line)
    assert isinstance(lute_entry, LuteEntry)
    assert lute_entry.term == 'høj'
    assert lute_entry.translation == 'high / tall'
    assert lute_entry.tags == ['adjective']
    assert lute_entry.added == datetime(2024, 8, 21, 23, 0, 13)
    assert lute_entry.status == 1

@pytest.mark.parametrize("line, expected", [
    (
        "lugte,,to smell,Danish,verb,2024-08-21 23:00:43,1,,",
        LuteEntry(
            term='lugte',
            parent='',
            translation='to smell',
            language='Danish',
            tags=['verb'],
            added=datetime(2024, 8, 21, 23, 0, 43),
            status=1,
            link_status='',
            pronunciation=''
        )
    ),
    (
        "kone,,wife / woman,Danish,\"common-noun, noun\",2024-08-17 16:48:46,1,,",
        LuteEntry(
            term='kone',
            parent='',
            translation='wife / woman',
            language='Danish',
            tags=['common-noun', 'noun'],
            added=datetime(2024, 8, 17, 16, 48, 46),
            status=1,
            link_status='',
            pronunciation=''
        )
    )
])

def test_create_lute_entries_from_various_lines(line, expected):
    parsed_line = parse_lute_term_output(line)
    lute_entry = LuteEntry.from_dict(parsed_line)
    assert lute_entry == expected

def test_lute_entry_knowledge_level():
    new_word = LuteEntry(term='new', parent='', translation='new', language='Danish', 
                         tags=['noun'], added=datetime.now(), status='W', link_status='', pronunciation='')
    assert new_word.knowledge_level() == "Known"

    learning_word = LuteEntry(term='learning', parent='', translation='learning', language='Danish', 
                              tags=['verb'], added=datetime.now(), status=3, link_status='', pronunciation='')
    assert learning_word.knowledge_level() == "Learning"

    known_word = LuteEntry(term='known', parent='', translation='known', language='Danish', 
                           tags=['adjective'], added=datetime.now(), status=5, link_status='', pronunciation='')
    assert known_word.knowledge_level() == "Learning"

def test_create_flashcard_from_lute_entry():
    lute_entry = LuteEntry(
        term='lugte',
        parent='',
        translation='to smell',
        language='Danish',
        tags=['verb'],
        added=datetime(2024, 8, 21, 23, 0, 43),
        status=1,
        link_status='',
        pronunciation=''
    )
    flashcard = create_flashcard_from_lute_entry(lute_entry)
    assert isinstance(flashcard, Flashcard)
    assert flashcard.target == 'lugte'
    assert flashcard.target_lang == 'Danish'
    assert flashcard.source_lang == 'English'
    assert flashcard.source == 'smell'  # 'to' should be removed
    assert flashcard.tags == 'verb'

def test_flashcard_has_danish_target_and_english_source():
    lute_entry = LuteEntry(
        term='tynd',
        parent='',
        translation='thin',
        language='Danish',
        tags=['adjective'],
        added=datetime(2024, 8, 21, 22, 59, 48),
        status=1,
        link_status='',
        pronunciation=''
    )
    flashcard = create_flashcard_from_lute_entry(lute_entry)
    assert flashcard.target_lang == "Danish"
    assert flashcard.source_lang == "English"
