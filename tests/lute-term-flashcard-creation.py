import pytest
from datetime import datetime
from typing import List, Dict
from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        Flashcard
        )

verb_lute_entry = LuteEntry(
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
 
adverb_lute_entry = LuteEntry(
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

conjunction_lute_entry = LuteEntry(
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

def test_flashcard_creation_from_lute_entry_verb():
    flashcard = Flashcard.from_lute_entry(verb_lute_entry)
    
    assert flashcard is not None
    assert flashcard.target == "beslutte"
    assert flashcard.source == "to decide"
    assert flashcard.context == ""
    assert flashcard.tags == "verb"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"

def test_can_generate_audio_for_verb_flashcard():
    flashcard = Flashcard.from_lute_entry(verb_lute_entry)

    assert True == False


def test_flashcard_creation_from_lute_entry_adverb():
    flashcard = Flashcard.from_lute_entry(adverb_lute_entry)

    assert flashcard is not None
    assert flashcard.target == "engang"
    assert flashcard.source == "once"
    assert flashcard.context == ""
    assert flashcard.tags == "adverb, conjunction"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"


def test_flashcard_creation_from_lute_entry_conjunction():
    flashcard = Flashcard.from_lute_entry(conjunction_lute_entry)
    
    assert flashcard is not None
    assert flashcard.target == "eller"
    assert flashcard.source == "or"
    assert flashcard.context == ""
    assert flashcard.tags == "conjunction"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"
