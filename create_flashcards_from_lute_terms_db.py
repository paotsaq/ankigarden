from db.objects import (
        # LuteEntry,
        # NormalizedLuteEntry,
        LuteTableEntry,
        Flashcard
        )
from const import (
        AUDIOS_SOURCE_DIR
        )
from logger import logger
from apis.anki_database import (
        move_audio_files_to_anki_mediadir,
        send_request_to_anki,
        create_anki_dict_from_flashcard
        )
from apis.lute_terms_db import (
        create_connection_to_database,
        close_connection_to_database
        )


ELIGIBLE_TAGS = ['building']
DATABASE = "/lute_terms.db"
session, engine = create_connection_to_database(DATABASE)
eligible_terms_for_flashcard = (session.query(LuteTableEntry).filter(
    LuteTableEntry.anki_note_id.is_(None) & LuteTableEntry.tags.contains('building')).all())
for lute_entry in eligible_terms_for_flashcard:
    flashcard = Flashcard.from_lute_entry(lute_entry)
    flashcard.generate_target_audio_query()
    flashcard.get_audio_file()
    flashcard.notetype = "Basic (and reversed) with pronunciation"
    flashcard.deck = "alex-danish"
    file_path = AUDIOS_SOURCE_DIR + flashcard.audio_filename

    anki_payload = create_anki_dict_from_flashcard(flashcard)
    fc_dict = create_anki_dict_from_flashcard(flashcard)
    params = {"notes": [fc_dict]}
    test_can_add = send_request_to_anki("canAddNotesWithErrorDetail",
                                        params)
    if test_can_add:
        send_request_to_anki("addNotes", params)
        move_audio_files_to_anki_mediadir([flashcard])
        logger.info(f"Created Anki card for {flashcard.target}")
    else:
        logger.error(test_can_add)
close_connection_to_database(session, engine)
