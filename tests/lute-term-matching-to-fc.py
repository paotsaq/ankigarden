import pytest
from datetime import datetime
from typing import List, Dict, Tuple
from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        Flashcard
        )
from apis.anki_database import (
        send_request_to_anki,
        find_exact_match_in_both_fields,
        find_exact_match_in_any_field,
        find_partial_match_in_any_field,
        show_card_info_with_id,
        find_all_matches_in_database
        # comprehensive_anki_match
        )

### TEST MATCHING OF TERMS

def test_exact_match_on_two_fields_verb():
    lute_entry = NormalizedLuteEntry(
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
    results = find_exact_match_in_both_fields(lute_entry, deck="ankigarden-test-deck")
    assert len(results) == 1
    assert results[0] == 1727246868311
    card_info = show_card_info_with_id(results)
    assert card_info[0]['fields']['source']['value'] == 'to decide'
    assert card_info[0]['fields']['target']['value'] == 'beslutte'


def test_exact_match_on_two_fields_noun():
    lute_entry = NormalizedLuteEntry(
        term="bog",
        parent="",
        translation="book",
        language="Danish",
        tags="noun",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    results = find_exact_match_in_both_fields(lute_entry, deck="ankigarden-test-deck")
    assert len(results) == 1
    assert results[0] == 1727598631014
    card_info = show_card_info_with_id(results)
    assert card_info[0]['fields']['source']['value'] == 'book'
    assert card_info[0]['fields']['target']['value'] == 'bog'


def test_exact_match_on_one_field_adverb():
    lute_entry = NormalizedLuteEntry(
        term="hurtig",
        parent="",
        translation="quickly",
        tags="adverb",
        language="Danish",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    results = find_exact_match_in_any_field(lute_entry, deck="ankigarden-test-deck")
    assert len(results) == 1
    assert results[0] == 1727599326447
    card_info = show_card_info_with_id(results)
    assert card_info[0]['fields']['source']['value'] == 'fast'
    assert card_info[0]['fields']['target']['value'] == 'hurtig'


def test_exact_match_on_one_field_verb():
    lute_entry = NormalizedLuteEntry(
        term="søge",
        parent="",
        translation="to search",
        tags="verb",
        language="Danish",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    results = find_exact_match_in_any_field(lute_entry, deck="ankigarden-test-deck")
    assert len(results) == 1
    assert results[0] == 1727598720797
    card_info = show_card_info_with_id(results)
    assert card_info[0]['fields']['source']['value'] == 'to search'
    assert card_info[0]['fields']['target']['value'] == 'at søge'


def test_partial_match_on_one_field_verb():
    lute_entry = NormalizedLuteEntry(
        term="søge",
        parent="",
        translation="to search",
        tags="verb",
        language="Danish",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    results = find_partial_match_in_any_field(lute_entry, deck="ankigarden-test-deck")
    assert results == [1727598658028, 1727598720797, 1727598701143, 1727598720797]


def test_all_matches_with_many_results():
    lute_entry = NormalizedLuteEntry(
        term="søge",
        parent="",
        translation="to search",
        tags="verb",
        language="Danish",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )
    results = find_all_matches_in_database(lute_entry, deck="ankigarden-test-deck")
    assert results == {
            'exact_matches_both_fields': [],
            'exact_match_any_field': [1727598720797],
            'partial_match_any_field': [1727598658028, 1727598701143]
            }


def test_pairing_of_term_to_flashcard():
    lute_entry = NormalizedLuteEntry(
        term="søge",
        parent="",
        translation="to search",
        tags="verb",
        language="Danish",
        added="2024-08-17 12:51:06",
        status="1",
        link_status="",
        pronunciation="",
    )


# def test_partial_match_conjunction():
    # entry = LuteEntry(term="men", translation="however", tags="conjunction")
    # results = comprehensive_anki_match(entry)
    # assert len(results["partial_term_matches"]) == 1
    # assert results["partial_term_matches"][0] == {"term": "men", "translation": "but"}

# def test_multiple_matches():
    # entry = LuteEntry(term="engang", translation="once", tags="adverb, conjunction")
    # results = comprehensive_anki_match(entry)
    # assert len(results["partial_term_matches"]) == 2
    # assert {"term": "hør engang", "translation": "listen here"} in results["partial_term_matches"]
    # assert {"term": "engang", "translation": "once upon a time"} in results["partial_term_matches"]

# def test_tag_match():
    # entry = LuteEntry(term="new_word", translation="new translation", tags="noun")
    # results = comprehensive_anki_match(entry)
    # assert len(results["tag_matches"]) > 0
    # assert all("noun" in card["tags"] for card in results["tag_matches"])

# def test_fuzzy_match():
    # entry = LuteEntry(term="lobe", translation="run", tags="verb")
    # results = comprehensive_anki_match(entry)
    # assert len(results["fuzzy_matches"]) > 0
    # assert any("løb" in card["term"] for card in results["fuzzy_matches"])

# def test_no_matches():
    # entry = LuteEntry(term="nonexistent", translation="not here", tags="none")
    # results = comprehensive_anki_match(entry)
    # assert all(len(matches) == 0 for matches in results.values())

