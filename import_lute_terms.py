from apis.lute_terms_db import (
        save_real_lute_data
        )

if __name__ == "__main__":
    db_path = "/lute_terms.db"
    lute_csv_path = "./Terms.csv"

    # Save the real data to the database
    save_real_lute_data(lute_csv_path, db_path)
