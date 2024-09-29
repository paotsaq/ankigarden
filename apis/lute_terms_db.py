from logger import logger
from db.objects import (
        Flashcard,
        LuteEntry,
        LuteTableEntry
        )
import json
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
import shutil
from datetime import datetime
import sqlite3


## DATABASE HANDLING
def create_connection_to_database(database_path: str) -> Tuple[Session, Engine]:
    engine: Engine = create_engine('sqlite://' + database_path)
    intermediate_session = sessionmaker(bind=engine)
    session: Session = intermediate_session()
    return session, engine

def close_connection_to_database(session: Session, engine: Engine) -> None:
    session.close()
    engine.dispose()


### LUTE FILE IMPORT

def parse_lute_term_output(line: list) -> Dict[str, str]:
    TERMS_KEYS: List[str] = ['term', 'parent', 'translation', 'language', 'tags', 'added', 'status', 'link_status', 'pronunciation']
    return dict(zip(TERMS_KEYS, line))


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

        # Convert parsed entries to LuteEntry objects
        lute_entries = [LuteEntry.from_dict(entry) for entry in parsed_entries]

        # Convert to LuteTableEntry objects
        lute_table_entries = [LuteTableEntry.from_lute_entry(entry) for entry in lute_entries]

        # Add and commit the LuteTableEntries to the database
        session.add_all(lute_table_entries)
        session.commit()

        print(f"Successfully saved {len(lute_table_entries)} entries to the database.")
    
    # except Exception as e:
        # print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        close_connection_to_database(session, engine)


