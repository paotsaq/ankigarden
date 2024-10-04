from db.objects import (
        LuteEntry,
        NormalizedLuteEntry,
        LuteTableEntry,
        convert_to_normalized_lute_entry,
        ANKIGARDEN_WORKING_TAG,
        ANKIGARDEN_FINAL_TAG
        )
from apis.lute_terms_db import (
        create_connection_to_database,
        save_real_lute_data,
        normalize_lute_terms_in_database,
        match_lute_terms_with_anki_database,
        close_connection_to_database
        )
from logger import logger

db_path = "/lute_terms.db"
lute_csv_path = "./Terms.csv"

if __name__ == "__main__":
    # save_real_lute_data(lute_csv_path, db_path)
    # normalize_lute_terms_in_database(db_path)
    match_lute_terms_with_anki_database(db_path)
