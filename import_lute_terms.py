import shutil
from sqlalchemy.orm import Session
from db.objects import LuteEntry, LuteTableEntry  # Adjust import paths if needed
from apis.lute_terms_db import create_connection_to_database, close_connection_to_database
from datetime import datetime
from apis.lute_terms_db import parse_lute_export_from_file


def save_real_lute_data(lute_csv_path: str, db_path: str) -> None:
    # Create connection to the SQLite database
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

# Example usage with real data
if __name__ == "__main__":
    # Path to your SQLite database
    db_path = "/lute_terms.db"
    lute_csv_path = "./Terms.csv"

    # Save the real data to the database
    save_real_lute_data(lute_csv_path, db_path)
