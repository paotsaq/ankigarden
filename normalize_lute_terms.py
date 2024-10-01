from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        convert_to_normalized_lute_entry
        )
from apis.lute_terms_db import (
        create_connection_to_database,
        close_connection_to_database
        )

def normalize_lute_terms_in_database(database_path: str):
    session, engine = create_connection_to_database(database_path)
    try:
        entries = session.query(LuteTableEntry).all()
        for entry in entries:
            normalized_entry = convert_to_normalized_lute_entry(entry)
            normalized_entry.normalize()
            normalized_entry.fix_logged_problems()
        session.commit()
        print("Normalising process completed successfully.")
    # except Exception as e:
        # print(f"An error occurred during the matching process: {str(e)}")
        # session.rollback()
    finally:
        close_connection_to_database(session, engine)

if __name__ == "__main__":
    db_path = "/lute_terms.db"
    normalize_lute_terms_in_database('/lute_terms.db')
