from logger import logger
from db.objects import (
        Flashcard,
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,        
        )
from const import (
        LANG_MAP,
        DATABASE_FILE_PATH,
        AUDIOS_ANKI_DIR,
        AUDIOS_SOURCE_DIR
        )
import json
from const import ANKI_CONNECT_BASE_URL
import requests
import shutil
import csv
from io import StringIO
from typing import (
        Dict,
        List
        )
from sqlalchemy.orm import (
        sessionmaker,
        Session,
        )
from sqlalchemy.engine import Engine, create_engine


# NOTE Lute import should not be here.
### LUTE FILE IMPORT

TERMS_KEYS = ['term', 'parent', 'translation', 'language', 'tags', 'added', 'status', 'link_status', 'pronunciation']

def parse_lute_term_output(line: str) -> dict:
    reader = csv.reader(StringIO(line))
    values = next(reader)
    return dict(zip(TERMS_KEYS, values))


def create_flashcard_from_lute_entry(lute_entry: LuteEntry) -> Flashcard:
    source = lute_entry.translation
    # removes the infinitives
    if 'verb' in lute_entry.tags and source.startswith('to '):
        source = source[3:]
    return Flashcard(
        target=lute_entry.term,
        target_lang=lute_entry.language,
        source_lang="English",
        source=source,
        tags=', '.join(lute_entry.tags)
    )

### ANKI CONNECT


def send_request_to_anki(action: str, params: dict = None) -> bool | dict:
    payload = {"action": action,
               "version": 6,
               "params": params}
    try:
        res = requests.post(ANKI_CONNECT_BASE_URL,
                           json=payload,
                           )
        logger.debug(f"Made request: {res}")
        if res.status_code != 200:
            logger.error(f"Anki connect request for {action} had an error!")
            return False
        else:
            response_content = json.loads(res.content)
            return response_content['result']
    except requests.exceptions.ConnectionError:
        logger.error("Connection refused: is Anki running?")
        return False


def create_anki_dict_from_flashcard(fc: Flashcard) -> dict:
    res = {
            "deckName": fc.deck,
            "modelName": fc.notetype,
            "fields": {
                # NOTE these are contextual and depend on `fc.notetype`
                "source": fc.source,
                "target": fc.target,
                "pronunciation": "[sound:" + fc.audio_filename + "]"
                },
            "tags": fc.tags.split()
            }
    return res


def move_audio_files_to_anki_mediadir(fcs: list[Flashcard]) -> None:
    for fc in fcs:
        shutil.move(AUDIOS_SOURCE_DIR + fc.audio_filename,
                    AUDIOS_ANKI_DIR + fc.audio_filename)


def show_card_info_with_id(note_ids: List[int]) -> None:
    res = send_request_to_anki("notesInfo",
                         params={"notes": note_ids})
    return res 

##### ANKI FLASHCARD MATCHING

def find_exact_match_in_one_field(
        lute_entry: NormalizedLuteEntry,
        deck: str,
        field_name: str,
        query_on_term: bool = True
        ) -> List[Dict]:
    """checks for exact matches on _either_ source or target fields"""
    deck_query = f'"deck:{deck}"'
    to_query = lute_entry.term if query_on_term else lute_entry.translation
    query = " ".join([deck_query,
                      f'"{field_name}:{to_query}"',
                      ])
    action = "findNotes"
    params = {"query": query}
    query_result = send_request_to_anki(action, params)
    return query_result

def find_exact_match_in_both_fields(
        lute_entry: NormalizedLuteEntry,
        # TODO change these default value
        deck: str = "alex-danish",
        front_field_name: str = "source",
        back_field_name: str = "target",
        ) -> List[Dict]:
    """checks for exact matches in both source and target fields"""
    front_field_request = find_exact_match_in_one_field(
            lute_entry,
            deck=deck,
            field_name=front_field_name,
            query_on_term=False)
    print(show_card_info_with_id(front_field_request[0]))
    if len(front_field_request) == 1:
        back_field_request = find_exact_match_in_one_field(
                lute_entry,
                deck=deck,
                field_name=back_field_name,
                query_on_term=True)
        if front_field_request == back_field_request:
            return front_field_request
    return []




def find_partial_match_in_any_field(
        lute_entry: NormalizedLuteEntry,
        # TODO change these default value
        deck: str = "alex-danish",
        front_field_name: str = "source",
        back_field_name: str = "target",
        ) -> List[Dict]:
    """checks for exact matches on _either_ source or target fields"""
    deck_query = f'"deck:{deck}"'
    back_query = " ".join([deck_query,
                      f'"{back_field_name}:*{lute_entry.term}*"',
                      ])
    front_query = " ".join([deck_query,
                      f'"{front_field_name}:*{lute_entry.translation}*"',
                      ])
    action = "findNotes"
    params = {"query": back_query}
    back_query_result = send_request_to_anki(action, params)
    params = {"query": front_query}
    front_query_result = send_request_to_anki(action, params)
    return back_query_result + front_query_result


def find_all_matches_in_database(
        lute_entry: NormalizedLuteEntry,
        deck: str,
        front_field_name: str = "source",
        back_field_name: str = "target",
        ) -> Dict[str, List[Dict]]:
    match_results = {
        "exact_matches_both_fields": [],
        "exact_match_front_field": [],
        "exact_match_back_field": [],
        "partial_match_any_field": [],
    }

    # Exact match on both fields
    exact_both = find_exact_match_in_both_fields(lute_entry, deck)
    exact_any_front = find_exact_match_in_one_field(
            lute_entry,
            deck,
            front_field_name,
            False)
    exact_any_back = find_exact_match_in_one_field(
            lute_entry,
            deck,
            back_field_name,
            True)
    partial_any = find_partial_match_in_any_field(lute_entry, deck)
    match_results["exact_matches_both_fields"] += exact_both
    new_front_matches = [match for match in exact_any_front
                       if match not in exact_both]
    match_results["exact_match_front_field"] += new_front_matches
    new_back_matches = [match for match in exact_any_back
                       if match not in exact_both]
    match_results["exact_match_back_field"] += new_back_matches
    new_partial_matches = [match for match in partial_any
                           if (match not in exact_any_front and
                               match not in exact_any_back)]
    match_results["partial_match_any_field"] = new_partial_matches

    # # Fuzzy match (for similar spellings or synonyms)
    # fuzzy_matches = find_fuzzy_matches(lute_entry)
    # match_results["fuzzy_matches"].extend(fuzzy_matches)

    return match_results


### LUTE TERMS MATCHING WITH FLASHCARD

def retrieve_matching_flashcard_id_for_lute_entry(
        session: Session,
        lute_entry: LuteTableEntry,
        deck: str
        ) -> int | None:
    results = find_all_matches_in_database(lute_entry, deck)
    if len(results["exact_matches_both_fields"]) == 1:
        anki_note_id = results["exact_matches_both_fields"][0]
        update_lute_entry_with_anki_id(session, lute_entry, anki_note_id)
        return anki_note_id
    elif len(results["exact_match_any_field"]) == 1:
        print("got exact match on one field for ", lute_entry)
        print(show_card_info_with_id(results["exact_match_any_field"]))
    elif len(results["partial_match_any_field"]) > 0:
        print("got partial match on one field for ", lute_entry)
    else:
        print("No match found for", lute_entry)
    return None


def update_lute_entry_with_anki_id(session: Session, lute_entry: LuteTableEntry, anki_note_id: int) -> None:
    try:
        db_entry = session.query(LuteTableEntry).filter_by(
            id=lute_entry.id,
        ).first()

        if db_entry:
            db_entry.anki_note_id = anki_note_id
            db_entry.last_synced = datetime.now()
            session.commit()
            print(f"Updated LuteTableEntry for term '{lute_entry.term}' with Anki note ID: {anki_note_id}")
        else:
            print(f"No matching LuteTableEntry found for term '{lute_entry.term}'")

    except Exception as e:
        print(f"Error updating LuteTableEntry: {str(e)}")
        session.rollback()


def match_lute_terms_with_anki_database(database_path: str):
    session, engine = create_connection_to_database(database_path)
    try:
        unsynced_entries = session.query(LuteTableEntry).filter(LuteTableEntry.anki_note_id.is_(None)).all()
        
        for entry in unsynced_entries:
            anki_note_id = retrieve_matching_flashcard_id_for_lute_entry(session, entry, "alex-danish")
            
            if anki_note_id:
                print(f"Matched and updated entry: {entry.term}")
            else:
                print(f"No match found for entry: {entry.term}")
        
        session.commit()
        print("Matching process completed successfully.")
    except Exception as e:
        print(f"An error occurred during the matching process: {str(e)}")
        session.rollback()
    finally:
        close_connection_to_database(session, engine)
