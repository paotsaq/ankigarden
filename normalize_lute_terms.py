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
        close_connection_to_database
        )
from logger import logger


def normalize_lute_terms_in_database(database_path: str):
    session, engine = create_connection_to_database(database_path)
    try:
        unmatched_unnormalized_entries = (session.query(LuteTableEntry).filter(
            LuteTableEntry.anki_note_id.is_(None) & LuteTableEntry.tags.contains('ankigarden-needs-work')).all())
        updated = 0
        for entry in unmatched_unnormalized_entries:
            try:
                normalized_entry = convert_to_normalized_lute_entry(entry)
                # NOTE this is being done earlier in the process,
                # upon object creation; might not be a good idea
                # normalized_entry.normalize()
                normalized_entry.fix_logged_problems()
                if normalized_entry.check_eligibility_for_final_tag():
                    new_tags = ", ".join(list(filter(lambda tag: tag != ANKIGARDEN_WORKING_TAG,
                                                     normalized_entry.tags.split(", "))) + [ANKIGARDEN_FINAL_TAG])

                    normalized_entry.tags = new_tags
                    updated_entry = LuteTableEntry.from_lute_entry(normalized_entry)
                    
                    # preserve the original ID
                    updated_entry.id = entry.id
                    
                    # update the entry in the database
                    session.merge(updated_entry)
                    logger.info(f"Database updated with ANKIGARDEN_FINAL_TAG for term {entry}")
                    updated += 1
            except Exception as e:
                logger.error(f"An error occurred during the normalization process: {str(e)}")
        session.commit()
        logger.info(f"Finished normalisation process. Updated {updated} entries.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during the matching process: {str(e)}")
        session.rollback()
    finally:
        close_connection_to_database(session, engine)


if __name__ == "__main__":
    db_path = "/lute_terms.db"
    normalize_lute_terms_in_database('/lute_terms.db')
