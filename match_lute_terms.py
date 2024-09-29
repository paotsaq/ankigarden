from apis.lute_terms_db import (
    match_lute_terms_with_anki_database,
    )

if __name__ == "__main__":
    db_path = "/lute_terms.db"
    match_lute_terms_with_anki_database('/lute_terms.db')
