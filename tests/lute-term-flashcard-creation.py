import pytest
from datetime import datetime
from typing import List, Dict
from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        Flashcard
        )
from os.path import (
        exists
        )
from os import (
        remove
        )
from const import (
        AUDIOS_SOURCE_DIR
        )

building_lute_entry = LuteEntry(
        term="besluttede sig for",
        parent="",
        translation="he decided (himself) that/for",
        language="Danish",
        tags="building",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )


def test_flashcard_creation_from_lute_entry_building():
    flashcard = Flashcard.from_lute_entry(building_lute_entry)
    
    assert flashcard is not None
    assert flashcard.target == "besluttede sig for"
    assert flashcard.source == "he decided (himself) that/for"
    assert flashcard.context == ""
    assert flashcard.tags == "building ankigarden-experimental"
    assert flashcard.source_lang == "English"
    assert flashcard.target_lang == "Danish"


def test_can_generate_audio_for_lute_entry_building():
    flashcard = Flashcard.from_lute_entry(building_lute_entry)
    flashcard.generate_target_audio_query()
    assert flashcard.target_audio_query == "besluttede sig for"
    flashcard.get_audio_file()
    file_path = AUDIOS_SOURCE_DIR + flashcard.audio_filename

    # assert file exists, and remove it
    assert exists(file_path) is True
    remove(file_path)
    assert exists(file_path) is False
