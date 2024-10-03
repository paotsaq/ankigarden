from logger import logger
from apis.anki_database import send_request_to_anki
from db.objects import (
        Flashcard,
        LuteEntry,
        LuteTableEntry,
        NormalizedLuteEntry,
        convert_to_normalized_lute_entry,
        PARENT_TAGS,
        CHILD_TAGS,
        TAGS_TO_SUPPRESS,
        ANKIGARDEN_WORKING_TAG,
        ANKIGARDEN_FINAL_TAG
        )
import json
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import (
        sessionmaker,
        Session,
        )
from sqlalchemy.engine import Engine, create_engine
import shutil
from datetime import datetime
import sqlite3
from functools import reduce
from apis.anki_database import retrieve_matching_flashcard_id_for_lute_entry




## DATABASE HANDLING
def create_connection_to_database(database_path: str) -> Tuple[Session, Engine]:
    engine: Engine = create_engine('sqlite://' + database_path)
    intermediate_session = sessionmaker(bind=engine)
    session: Session = intermediate_session()
    return session, engine

def close_connection_to_database(session: Session, engine: Engine) -> None:
    session.close()
    engine.dispose()


### LUTE TERMS FILE IMPORT

# NOTE contains the definition of the lute CSV header
# will also split the commas on export if needed
def parse_lute_term_output(line: list) -> Dict[str, str]:
    TERMS_KEYS: List[str] = ['term', 'parent', 'translation', 'language', 'tags', 'added', 'status', 'link_status', 'pronunciation']
    res = dict(zip(TERMS_KEYS, line))
    res["tags"] = " ".join(res["tags"].split(", "))
    return res


def parse_lute_export(lute_export: csv.reader) -> List[Dict[str, str]]:
    """Parse the Lute export string into a list of dictionaries."""
    return [parse_lute_term_output(line)
            for line in lute_export]


def parse_lute_export_from_file(csv_file_path: str) -> List[Dict[str, str]]:
    """Parse the Lute export CSV file into a list of dictionaries."""
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        return parse_lute_export(reader)


def save_lute_entries_to_db(lute_entries: List[LuteEntry], db_session: Session) -> None:
    for entry in lute_entries:
        existing_entry = db_session.query(LuteEntry).filter_by(added=entry.added).first()
        if existing_entry:
            for key, value in entry.__dict__.items():
                if key != 'id':  # Assuming 'id' is the primary key
                    setattr(existing_entry, key, value)
        else:
            # Add new entry
            db_session.add(entry)
    db_session.commit()


def save_real_lute_data(lute_csv_path: str, db_path: str) -> None:
    session, engine = create_connection_to_database(db_path)
    try:
        parsed_entries = parse_lute_export_from_file(lute_csv_path)
        lute_entries = [LuteEntry.from_dict(entry)
                        for entry in parsed_entries]
        # NOTE what happens below is its own routine and should be refactored
        new_entry_count = 0
        for lute_entry in lute_entries:
            # NOTE this tag is applied when term has undergone full
            # normalisation process, including fixing problems if any arise.
            if ANKIGARDEN_FINAL_TAG in lute_entry.tags:
                logger.info(f"term {normalized_entry.term} has already been imported!")
                continue

            # NOTE 10/01/24: the normalisation happens upon object creation;
            # this might not be good practice
            normalized_entry = NormalizedLuteEntry.from_lute_entry(lute_entry)

            # query the database for duplicate/redundant entry
            same_term_query = (session.query(LuteTableEntry).filter(
                LuteTableEntry.term == normalized_entry.term)).all()
            same_timestamp_query = (session.query(LuteTableEntry).filter(
                LuteTableEntry.added == normalized_entry.added)).all()

            # TODO as it is, if there is a bunch of terms with the same timestamp;
            # it saves one of those and rejects the others; this is not the ideal situation
            # maybe they should all share a tag?
            # there's a big family of terms here; ouch!
            if len(same_term_query) > 1:
                logger.error("duplicate terms {normalized_entry.term} in database?!")
            elif len(same_term_query) == 1:
                logger.info(f"term {normalized_entry.term} matches another term in database!")
            elif len(same_timestamp_query) > 1:
                logger.warning("multiple timestamp query results is not yet handled!")
                logger.debug(len(same_timestamp_query), lute_entry.term)
            elif len(same_timestamp_query) == 1:
                logger.warning("exact timestamp query result: is this an unhandled parent/child term?")
            else:
                # TODO this should be under the normalisation process, not here.
                # checks whether to apply ANKIGARDEN_WORKING_TAG:
                # NOTE there was no work done; just small normalisations
                # Wiktionary queries, for example, will trigger a flag.
                if not normalized_entry.check_eligibility_for_final_tag():
                    if normalized_entry.tags != '':
                        new_tags = " ".join(normalized_entry.tags.split() + [ANKIGARDEN_WORKING_TAG])
                    else:
                        new_tags = ANKIGARDEN_WORKING_TAG
                else:
                    new_tags = " ".join(normalized_entry.tags.split() + [ANKIGARDEN_FINAL_TAG])
                normalized_entry.tags = new_tags
                new_table_entry = LuteTableEntry.from_lute_entry(normalized_entry)
                session.add(new_table_entry)
                logger.info(f"new term {new_table_entry} added to database")
                new_entry_count += 1
        session.commit()
        print(f"Successfully saved {new_entry_count} entries to the database.")
    
    # except Exception as e:
        # print(f"An error occurred: {e}")
    
    finally:
        close_connection_to_database(session, engine)


### LUTE TERMS MATCHING WITH FLASHCARD

def match_lute_terms_with_anki_database(database_path: str):
    session, engine = create_connection_to_database(database_path)
    anki_is_up = send_request_to_anki("getNumCardsReviewedToday") is not False
    if anki_is_up:
        try:
            unsynced_entries = session.query(LuteTableEntry).filter(LuteTableEntry.anki_note_id.is_(None)).all()
            # NOTE first, it tries matching entries
            for entry in unsynced_entries:
                anki_note_id = retrieve_matching_flashcard_id_for_lute_entry(session, entry, "alex-danish")
                if anki_note_id:
                    logger.info(f"Matched and updated entry: {entry.term}")
                else:
                    logger.info(f"No match found for entry: {entry.term}")
            # NOTE then, it can create _some_ entries that would not likely be matched
            # case in point: terms tagged with `building` represent idiomatic expressions,
            # or small sentence excerpts
            unmatched_building_entries = (session.query(LuteTableEntry).filter(
                LuteTableEntry.anki_note_id.is_(None) & LuteTableEntry.tags.contains('building')).all())
            logger.info(f"Found {len(unmatched_building_entries)} unmatched `building` entries.")
            for entry in unmatched_building_entries:
                # TODO create flashcard object
                pass
            session.commit()
        # except Exception as e:
            # print(dir(e))
            # print(help(e.with_traceback))
            # logger.error(f"An error occurred during the matching process: {str(e)}")
            # session.rollback()
        finally:
            close_connection_to_database(session, engine)
    else:
        logger.error("Cannot connect to Anki. Is it running?")
