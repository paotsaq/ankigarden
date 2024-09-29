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


# def create_connection_to_database(database_path: str) -> list[Session, Engine]:
    # engine = create_engine('sqlite://' + database_path)
    # intermediate_session = sessionmaker(bind=engine)
    # session = intermediate_session()
    # return session, engine


# def close_connection_to_database(session: Session, engine: Engine):
    # session.close()
    # engine.dispose()


# def retrieve_all_flashcards_from_database(session: Session) -> list[Flashcard]:
    # fcs = session.query(Flashcard).all()
    # return fcs


# def retrieve_flashcards_without_source(session: Session) -> list[Flashcard]:
    # return session.query(Flashcard).filter(Flashcard.source.is_(None)).all()


# def retrieve_flashcards_without_audio_file_path(session: Session) -> list[Flashcard]:
    # return session.query(Flashcard).filter(Flashcard.audio_filename.is_(None)).all()


# def update_flashcards_to_added_with_given_tag(
        # session: Session,
        # target_tag: str
        # ):
    # stmt = (
        # update(Flashcard).
        # where(Flashcard.tags.contains(target_tag)).
        # values(added=1)
        # )
    # session.execute(stmt)
    # session.commit()


# def parse_line_from_prompt(line: str) -> list[str, str | None, str | None]:
    # parts = line.split('|')
    # query, tags, context = parts + [None] * (3 - len(parts))  # Unpack parts, filling missing values with None
    # return query, tags, context


# # NOTE `notetype` field must still be refactored
# def create_flashcard_from_prompt_line(prompt: str,
                                      # target_lang: str,
                                      # source_lang: str,
                                      # notetype: str = "Basic (and reversed) with pronunciation"
                                      # ) -> Flashcard:
    # target, tags, context = parse_line_from_prompt(prompt)
    # return Flashcard(target_lang = target_lang,
                     # target = target,
                     # source_lang = source_lang,
                     # context = context,
                     # notetype = notetype,
                     # tags = tags,
                     # )

# def import_prompts_from_text_file_to_database(prompts_filename: str,
                                              # session: Session,
                                              # target_lang: str,
                                              # source_lang: str,
                                              # ) -> list[Flashcard]:
    # with open(prompts_filename, "r") as prompts:
        # lines = prompts.read().strip().splitlines()
        # for line in lines:
            # session.add(create_flashcard_from_prompt_line(line, target_lang, source_lang))
    # session.commit()


# def create_anki_import_string(fcs: list[Flashcard],
                              # SEP: str,
                              # TAGS_COLUMN: int,
                              # NOTETYPE_COLUMN: int,
                              # DECK: str,
                              # TAGS = list[str],
                              # COLUMNS = list[str],
                              # NOTETYPE = str
                              # ) -> str:
    # header = "\n".join([
        # f'#separator:{SEP}',
        # f'#tags:{" ".join(TAGS)}',
        # f'#columns:{SEP.join(COLUMNS)}',
        # f'#deck: {DECK}',
        # f'#tags column: {TAGS_COLUMN}',
        # f'#notetype column: {NOTETYPE_COLUMN}',
        # ])
    # body = "\n".join(list(map(lambda fc:
                              # SEP.join([
                                  # fc.source,
                                  # fc.target,
                                  # f"[sound:{fc.audio_filename}]",
                                  # " ".join(TAGS + [fc.tags]),
                                  # NOTETYPE]) + "|",
                              # fcs)))
    # return "\n\n".join([header, body])


# def create_anki_import_file(anki_import_str: str,
                            # anki_import_filename: str):
    # with open(anki_import_filename, "w") as f:
        # f.write(anki_import_str)


# def create_anki_import_file_of_not_added_flashcards(batch_name: str):
    # ANKI_TEXTS_DIR = "anki-textfile-outputs/"
    # ANKI_IMPORT_FILENAME = f"anki-{batch_name}.txt"

    # SEP = "|"
    # TAGS_COLUMN = 4
    # NOTETYPE_COLUMN = 5
    # DECK = "alex-danish"
    # TARGET_LANG = "Danish"
    # SOURCE_LANG = "English"
    # COLUMNS = ["source", "target", "pronunciation"]
    # NOTETYPE = "Basic (and reversed) with pronunciation"

    # session, engine = create_connection_to_database(DATABASE_FILE_PATH)
    # fcs =  session.query(Flashcard).filter(Flashcard.added.is_(0)).all()
    # anki_str = create_anki_import_string(fcs,
                               # SEP,
                               # TAGS_COLUMN,
                               # NOTETYPE_COLUMN,
                               # DECK,
                               # [batch_name],
                               # COLUMNS,
                               # NOTETYPE)
    # create_anki_import_file(anki_str, ANKI_TEXTS_DIR + ANKI_IMPORT_FILENAME)
    # stmt = (
        # update(Flashcard).
        # where(Flashcard.added.is_(0)).
        # values(added=1)
        # )
    # session.execute(stmt)
    # session.commit()
    # close_connection_to_database(session, engine)

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

def find_exact_match_in_both_fields(
        lute_entry: NormalizedLuteEntry,
        # TODO change these default value
        deck: str = "alex-danish",
        front_field_name: str = "source",
        back_field_name: str = "target",
        ) -> List[Dict]:
    """checks for exact matches in both source and target fields"""
    query = " ".join([f'"deck:{deck}"',
                      f'"{front_field_name}:{lute_entry.translation}"',
                      f'"{back_field_name}:{lute_entry.term}"',
                      ])
    action = "findNotes"
    params = {"query": query}
    result = send_request_to_anki(action, params)
    return result


def find_exact_match_in_any_field(
        lute_entry: NormalizedLuteEntry,
        # TODO change these default value
        deck: str = "alex-danish",
        front_field_name: str = "source",
        back_field_name: str = "target",
        ) -> List[Dict]:
    """checks for exact matches on _either_ source or target fields"""
    deck_query = f'"deck:{deck}"'
    back_query = " ".join([deck_query,
                      f'"{back_field_name}:{lute_entry.term}"',
                      ])
    front_query = " ".join([deck_query,
                      f'"{front_field_name}:{lute_entry.translation}"',
                      ])
    action = "findNotes"
    params = {"query": back_query}
    back_query_result = send_request_to_anki(action, params)
    params = {"query": front_query}
    front_query_result = send_request_to_anki(action, params)
    return back_query_result + front_query_result


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


def find_all_matches_in_database(lute_entry: NormalizedLuteEntry, deck: str) -> Dict[str, List[Dict]]:
    match_results = {
        "exact_matches_both_fields": [],
        "exact_match_any_field": [],
        "partial_match_any_field": [],
    }

    # Exact match on both fields
    exact_both = find_exact_match_in_both_fields(lute_entry, deck)
    if len(exact_both) != 0: 
        match_results["exact_matches_both_fields"] = exact_both

    # Exact match on any field (and doesn't consider the previous)
    exact_any = find_exact_match_in_any_field(lute_entry, deck)
    if len(exact_any) != 0: 
        new_any_matches = [match for match in exact_any
                           if match not in exact_both]
        match_results["exact_match_any_field"] = new_any_matches

    # Partial match on any field (and doesn't consider the previous)
    partial_any = find_partial_match_in_any_field(lute_entry, deck)
    if len(partial_any) != 0: 
        new_partial_matches = [match for match in partial_any
                               if match not in exact_any]
        match_results["partial_match_any_field"] = new_partial_matches

    # # Fuzzy match (for similar spellings or synonyms)
    # fuzzy_matches = find_fuzzy_matches(lute_entry)
    # match_results["fuzzy_matches"].extend(fuzzy_matches)

    return match_results


def pair_lute_table_entry_with_flashcard(lute_entry: LuteTableEntry) -> None:
    pass


# def find_partial_translation_matches(lute_entry: LuteEntry) -> List[Dict]:
    # query = f'"Back:*{lute_entry.translation}*"'
    # return execute_anki_query(query)


# def find_tag_matches(lute_entry: LuteEntry) -> List[Dict]:
    # tags = lute_entry.tags.split(", ")
    # matches = []
    # for tag in tags:
        # query = f'tag:{tag}'
        # matches.extend(execute_anki_query(query))
    # return matches


# def find_fuzzy_matches(lute_entry: LuteEntry) -> List[Dict]:
    # # This is a placeholder for a more sophisticated fuzzy matching algorithm
    # # You might want to use libraries like fuzzywuzzy or implement your own logic
    # query = f'"Front:{lute_entry.term[:3]}*" OR "Back:{lute_entry.translation[:3]}*"'
    # return execute_anki_query(query)


# def execute_anki_query(query: str) -> List[Dict]:
    # action = "findCards"
    # params = {"query": query}
    # card_ids = send_request_to_anki(action, params)
    
    # if not isinstance(card_ids, list) or len(card_ids) == 0:
        # return []

    # # Fetch card info for the found cards
    # action = "cardsInfo"
    # params = {"cards": card_ids}
    # cards_info = send_request_to_anki(action, params)

    # return [{"term": card["fields"]["Front"]["value"], 
             # "translation": card["fields"]["Back"]["value"]} 
            # for card in cards_info]
