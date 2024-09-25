import pytest
from datetime import datetime
from typing import List, Dict
from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        Flashcard
        )


def test_flashcard_creation_from_lute_entry_verb():
    lute_entry = LuteEntry(
        term="beslutte",
        parent="",
        translation="to decide",
        language="Danish",
        tags="verb",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    
    flashcard = Flashcard.from_lute_entry(lute_entry)
    
    assert flashcard is not None
    assert flashcard.source == "beslutte"
    assert flashcard.target == "to decide"
    assert flashcard.context == ""
    assert flashcard.tags == "verb"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"
    assert flashcard.added_lute_timestamp == 1723891866  # This is the timestamp for "2024-08-17 12:51:06"
    assert flashcard.added_to_anki == False


def test_flashcard_creation_from_lute_entry_adverb():
    lute_entry = LuteEntry(
        term="engang",
        parent="",
        translation="once",
        language="Danish",
        tags="adverb, conjunction",
        added="2024-08-16 12:34:45",
        status="3",
        link_status="",
        pronunciation="",
    )
    
    flashcard = Flashcard.from_lute_entry(lute_entry)

    assert flashcard is not None
    assert flashcard.source == "engang"
    assert flashcard.target == "once"
    assert flashcard.context == ""
    assert flashcard.tags == "adverb, conjunction"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"
    assert flashcard.added_lute_timestamp == 1723804485
    assert flashcard.added_to_anki == False


def test_flashcard_creation_from_lute_entry_conjunction():
    lute_entry = LuteEntry(
        term="eller",
        parent="",
        translation="or",
        language="Danish",
        tags="conjunction",
        added="2024-08-21 22:57:35",
        status="W",
        link_status="",
        pronunciation="",
    )
    
    flashcard = Flashcard.from_lute_entry(lute_entry)
    
    assert flashcard is not None
    assert flashcard.source == "eller"
    assert flashcard.target == "or"
    assert flashcard.context == ""
    assert flashcard.tags == "conjunction"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"
    assert flashcard.added_lute_timestamp == 1724273855  
    assert flashcard.added_to_anki == False
