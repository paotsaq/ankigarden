import pytest
from datetime import datetime
from typing import List, Dict
from db.objects import LuteEntry, NormalizedLuteEntry, LuteTableEntry


def test_normalize_uppercase_term():
    original = LuteEntry(
        term="Der",
        parent="",
        translation="there / that / who",
        language="Danish",
        tags="adverb, pronoun",
        added=datetime.fromisoformat("2024-08-16T12:33:56"),
        status="W",
        link_status="",
        pronunciation=""
    )
    normalized = NormalizedLuteEntry.from_lute_entry(original)
    
    assert normalized.term == "der"
    
    # Check normalization log
    assert len(normalized.normalization_log) == 1
    assert normalized.normalization_log[0]["method"] == "lowercased term"
    assert normalized.normalization_log[0]["field"] == "term"
    assert normalized.normalization_log[0]["original"] == 'Der'
    assert normalized.normalization_log[0]["normalized"] == 'der'

def test_set_untagged_word_as_root_verb():
    original = LuteEntry(
        term="begyndte",
        parent="",
        translation="",
        language="Danish",
        tags="",
        added=datetime.fromisoformat("2024-09-11T09:32:16"),
        status="W",
        link_status="",
        pronunciation=""
    )
    normalized = NormalizedLuteEntry.from_lute_entry(original)
    
    assert normalized.must_get_part_of_speech == True
    # Check normalization log
    assert len(normalized.normalization_log) == 1
    assert normalized.normalization_log[0]["method"] == "set must_get_part_of_speech"
    assert normalized.normalization_log[0]["field"] == "must_get_part_of_speech"
    assert normalized.normalization_log[0]["original"] == False
    assert normalized.normalization_log[0]["normalized"] == True
    assert normalized.normalization_log[0]["fixed"] == False

    normalized.fix_logged_problems()

    assert normalized.normalization_log[0]["fixed"] == True
    assert normalized.parent == "begynde"
    assert normalized.tags == "conjugation"


def test_set_untagged_word_as_something():
    original = LuteEntry(
        term="engang",
        parent="",
        translation="once",
        language="Danish",
        tags="",
        added=datetime.fromisoformat("2024-08-16T12:34:45"),
        status="3",
        link_status="",
        pronunciation=""
    )
    normalized = NormalizedLuteEntry.from_lute_entry(original)
    
    assert normalized.term == "engang"
    
    # Check normalization log
    assert len(normalized.normalization_log) == 1
    assert normalized.normalization_log[0]["method"] == "set must_get_part_of_speech"
    assert normalized.normalization_log[0]["field"] == "must_get_part_of_speech"
    assert normalized.normalization_log[0]["original"] == False
    assert normalized.normalization_log[0]["normalized"] == True
    assert normalized.normalization_log[0]["fixed"] == False

    normalized.fix_logged_problems()

    assert normalized.normalization_log[0]["fixed"] == True
    assert normalized.parent == ""
    assert normalized.tags == "adverb, conjunction"


def test_set_word_with_parent_and_verb_tag_as_conjugation():
    original = LuteEntry(
        term="besluttede",
        parent="beslutte",
        translation="decided",
        language="Danish",
        tags="verb",
        added=datetime.fromisoformat("2024-08-17T12:51:06"),
        status="1",
        link_status="y",
        pronunciation=""
    )
    normalized = NormalizedLuteEntry.from_lute_entry(original)
    
    assert normalized.term == "besluttede"
    
    # Check normalization log
    assert len(normalized.normalization_log) == 0


def test_removes_unnecessary_tags():
    original = LuteEntry(
        term="eller",
        parent="",
        translation="or",
        language="Danish",
        tags="conjunction, vocabulary",
        added=datetime.fromisoformat("2024-08-21T22:57:35"),
        status="W",
        link_status="",
        pronunciation=""
    )
    normalized = NormalizedLuteEntry.from_lute_entry(original)
    
    assert normalized.term == "eller"
    
    # Check normalization log
    assert len(normalized.normalization_log) == 1
    
    assert normalized.normalization_log[0]["method"] == "removed tags"
    assert normalized.normalization_log[0]["field"] == "tags"
    assert normalized.normalization_log[0]["original"] == 'conjunction, vocabulary'
    assert normalized.normalization_log[0]["normalized"] == 'conjunction'
