from objects import Flashcard
from anki_database import (
    create_connection_to_database,
    close_connection_to_database,
    retrieve_all_flashcards_from_database,
    retrieve_flashcards_without_source,
    retrieve_flashcards_without_audio_file_path,
    import_prompts_from_text_file_to_database,
    create_anki_import_string,
    create_anki_import_file,
    update_flashcards_to_added_with_given_tag
        )
from const import DATABASE_FILE_PATH
from logger import logger

ANKI_TEXTS_DIR = "anki-textfile-outputs"

UNIQUE_BATCH_NAME = "pimsleur-28"
NEW_PROMPTS_FILENAME = "prompts.txt"
ANKI_IMPORT_FILENAME = f"anki-{UNIQUE_BATCH_NAME}.txt"

SEP = "|"
TAGS_COLUMN = 4
NOTETYPE_COLUMN = 5
DECK = "alex-danish"
TARGET_LANG = "Danish"
SOURCE_LANG = "English"
COLUMNS = ["source", "target", "pronunciation"]
NOTETYPE = "Basic (and reversed) with pronunciation"

# creates connection to database
session, engine = create_connection_to_database(DATABASE_FILE_PATH)
# imports the prompts from the textfile
import_prompts_from_text_file_to_database(
        NEW_PROMPTS_FILENAME,
        session,
        TARGET_LANG,
        SOURCE_LANG,
        )
# NOTE there should be a better way to target these,
# maybe just get the imported prompts? 
fcs = retrieve_flashcards_without_source(session)
for fc in fcs:
    fc.get_source_from_target()
session.commit()

# update audio filename for each flaschard
fcs = retrieve_flashcards_without_audio_file_path(session)
for fc in fcs:
    fc.get_audio_file_path()
    fc.get_audio_file()
session.commit()

# select flashcards to export
fcs =  session.query(Flashcard).filter(Flashcard.added.is_(0)).all()
TAGS = [UNIQUE_BATCH_NAME]
anki_str = create_anki_import_string(fcs,
                           SEP,
                           TAGS_COLUMN,
                           NOTETYPE_COLUMN,
                           DECK,
                           TAGS,
                           COLUMNS,
                           NOTETYPE)
create_anki_import_file(anki_str, ANKI_IMPORT_FILENAME)
update_flashcards_to_added_with_given_tag(session, UNIQUE_BATCH_NAME)

# closes connection
close_connection_to_database(session, engine)
