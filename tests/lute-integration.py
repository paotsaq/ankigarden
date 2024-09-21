import shutil
import pytest
from datetime import datetime
from db.objects import Flashcard, LuteEntry, LuteTableEntry
from apis.lute_terms_db import (
        create_connection_to_database,
        close_connection_to_database,
        parse_lute_term_output,
        parse_lute_export,
        save_lute_entries_to_db,
        Session, Engine,
        parse_lute_export_from_file
        )
import os
import csv
from io import StringIO 

@pytest.fixture
def sample_lute_lines():
    return [
        "høj,,high / tall,Danish,adjective,2024-08-21 23:00:13,1,,",
        "lugte,,to smell,Danish,verb,2024-08-21 23:00:43,1,,",
        "tynd,,thin,Danish,adjective,2024-08-21 22:59:48,1,,",
        "kone,,wife / woman,Danish,\"common-noun, noun\",2024-08-17 16:48:46,1,,",
    ]

def test_parse_single_line_of_prompt():
    line = "høj,,high / tall,Danish,adjective,2024-08-21 23:00:13,1,,".split(',')
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
    assert lute_entry.tags == 'adjective'
    assert lute_entry.added == datetime(2024, 8, 21, 23, 0, 13)
    assert lute_entry.status == '1'

def test_lute_entry_knowledge_level():
    new_word = LuteEntry(term='new', parent='', translation='new', language='Danish', 
                         tags=['noun'], added=datetime.now(), status='W', link_status='', pronunciation='')
    assert new_word.knowledge_level() == "Known"

    learning_word = LuteEntry(term='learning', parent='', translation='learning', language='Danish', 
                              tags=['verb'], added=datetime.now(), status='3', link_status='', pronunciation='')
    assert learning_word.knowledge_level() == "Learning"

    known_word = LuteEntry(term='known', parent='', translation='known', language='Danish', 
                           tags=['adjective'], added=datetime.now(), status='5', link_status='', pronunciation='')
    assert known_word.knowledge_level() == "Learning"

    line = "svær,,difficult,Danish,adjective,2024-09-21 14:30:00,,,".split(",")
    parsed_entry: Dict[str, str] = parse_lute_term_output(line)
    lute_entry: LuteEntry = LuteEntry.from_dict(parsed_entry)

    assert lute_entry.term == 'svær'
    assert lute_entry.translation == 'difficult'
    assert lute_entry.status == ''  # Non-numerical status
    assert lute_entry.knowledge_level() == "NoInfo" 


@pytest.mark.parametrize("line, expected", [
    (
        "lugte,,to smell,Danish,verb,2024-08-21 23:00:43,1,,".split(","),
        LuteEntry(
            term='lugte',
            parent='',
            translation='to smell',
            language='Danish',
            tags='verb',
            added=datetime(2024, 8, 21, 23, 0, 43),
            status='1',
            link_status='',
            pronunciation=''
        )
    ),
    # TODO this should be unit tested properly. it can be a source of distress.
    # (
        # "kone,,wife / woman,Danish,\"common-noun, noun\",2024-08-17 16:48:46,W,,",
        # LuteEntry(
            # term='kone',
            # parent='',
            # translation='wife / woman',
            # language='Danish',
            # tags='common-noun, noun',
            # added=datetime(2024, 8, 17, 16, 48, 46),
            # status="W",
            # link_status='',
            # pronunciation=''
        # )
    # )
])


def test_create_lute_entries_from_various_lines(line, expected):
    parsed_line = parse_lute_term_output(line)
    lute_entry = LuteEntry.from_dict(parsed_line)
    assert lute_entry == expected


def test_parse_multiple_lute_lines():

    lute_export = """term,parent,translation,language,tags,added,status,link_status,pronunciation
høj,,high / tall,Danish,adjective,2024-08-21 23:00:13,1,,
lugte,,to smell,Danish,verb,2024-08-21 23:00:43,1,,
tynd,,thin,Danish,adjective,2024-08-21 22:59:48,1,,
kone,,wife / woman,Danish,"common-noun, noun",2024-08-17 16:48:46,1,,"""

    csv_file_like = StringIO(lute_export)
    # Create a CSV reader from the file-like object
    reader = csv.reader(csv_file_like)
    next(reader)

    parsed_entries = parse_lute_export(reader)

    assert len(parsed_entries) == 4
    assert parsed_entries[0]['term'] == 'høj'
    assert parsed_entries[1]['term'] == 'lugte'
    assert parsed_entries[2]['term'] == 'tynd'
    assert parsed_entries[3]['term'] == 'kone'

    # Convert parsed entries to LuteEntry objects
    lute_entries = [LuteEntry.from_dict(entry) for entry in parsed_entries]

    assert isinstance(lute_entries[0], LuteEntry)
    assert lute_entries[1].translation == 'to smell'
    assert lute_entries[2].language == 'Danish'
    assert lute_entries[3].tags == 'common-noun, noun'

def test_create_lute_table_entry_from_lute_entry():
    # Mock LuteEntry
    lute_entry = LuteEntry(
        term="høj",
        parent=None,
        translation="high / tall",
        language="Danish",
        tags="adjective",
        added=datetime(2024, 8, 21, 23, 0, 13),
        status=1,
        link_status=None,
        pronunciation=""
    )
    
    # Convert LuteEntry to LuteTableEntry
    lute_table_entry = LuteTableEntry.from_lute_entry(lute_entry)

    # Check that fields are properly converted
    assert lute_table_entry.term == lute_entry.term
    assert lute_table_entry.translation == lute_entry.translation
    assert lute_table_entry.language == lute_entry.language
    assert lute_table_entry.tags == 'adjective'  # Converted list to string
    assert lute_table_entry.added == lute_entry.added
    assert lute_table_entry.status == "1" 
    assert lute_table_entry.link_status == lute_entry.link_status
    assert lute_table_entry.pronunciation == lute_entry.pronunciation

def test_routine_to_add_lute_entries_to_db() -> None:
    # Copy the database file for testing
    original_db = "./tests/test-files/test-lute-terms.db"
    test_db = "./tests/test-files/test-lute-terms_copy.db"
    FEW_CSV_TERMS = "./tests/test-files/few-lute-terms.csv"
    test_db_sqlite_path = test_db[1:]
    shutil.copy(original_db, test_db)
    session, engine = create_connection_to_database(test_db_sqlite_path)
    
    try:
        # Create connection to the copied test database
        assert isinstance(session, Session)
        assert isinstance(engine, Engine)

        # Mock Lute export data

        parsed_entries = parse_lute_export_from_file(FEW_CSV_TERMS)
        lute_entries: List[LuteEntry] = [LuteEntry.from_dict(entry) for entry in parsed_entries]
        lute_table_entries = [LuteTableEntry.from_lute_entry(entry) for entry in lute_entries]
        session.add_all(lute_table_entries)
        session.commit()
        saved_entries = session.query(LuteTableEntry).all()
        assert len(saved_entries) == 4
        assert saved_entries[0].term == "høj"
        assert saved_entries[0].tags == "adjective"
        assert saved_entries[1].term == "lugte"
    finally:
        # Close the connection and delete the copied database file
        close_connection_to_database(session, engine)
        os.remove(test_db)
