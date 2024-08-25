from logger import logger
from objects import Flashcard
from const import (
        LANG_MAP,
        DATABASE_FILE_PATH,
        AUDIOS_ANKI_DIR,
        AUDIOS_SOURCE_DIR
        )
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker
from objects import Base, Flashcard
from sqlalchemy.engine.base import Engine
import json
from const import ANKI_CONNECT_BASE_URL
import requests
import shutil


def create_connection_to_database(database_path: str) -> list[Session, Engine]:
    engine = create_engine('sqlite://' + database_path)
    intermediate_session = sessionmaker(bind=engine)
    session = intermediate_session()
    return session, engine


def close_connection_to_database(session: Session, engine: Engine):
    session.close()
    engine.dispose()


def retrieve_all_flashcards_from_database(session: Session) -> list[Flashcard]:
    fcs = session.query(Flashcard).all()
    return fcs


def retrieve_flashcards_without_source(session: Session) -> list[Flashcard]:
    return session.query(Flashcard).filter(Flashcard.source.is_(None)).all()


def retrieve_flashcards_without_audio_file_path(session: Session) -> list[Flashcard]:
    return session.query(Flashcard).filter(Flashcard.audio_filename.is_(None)).all()


def update_flashcards_to_added_with_given_tag(
        session: Session,
        target_tag: str
        ):
    stmt = (
        update(Flashcard).
        where(Flashcard.tags.contains(target_tag)).
        values(added=1)
        )
    session.execute(stmt)
    session.commit()


def parse_line_from_prompt(line: str) -> list[str, str | None, str | None]:
    parts = line.split('|')
    query, tags, context = parts + [None] * (3 - len(parts))  # Unpack parts, filling missing values with None
    return query, tags, context


# NOTE `notetype` field must still be refactored
def create_flashcard_from_prompt_line(prompt: str,
                                      target_lang: str,
                                      source_lang: str,
                                      notetype: str = "Basic (and reversed) with pronunciation"
                                      ) -> Flashcard:
    target, tags, context = parse_line_from_prompt(prompt)
    return Flashcard(target_lang = target_lang,
                     target = target,
                     source_lang = source_lang,
                     context = context,
                     notetype = notetype,
                     tags = tags,
                     )

def import_prompts_from_text_file_to_database(prompts_filename: str,
                                              session: Session,
                                              target_lang: str,
                                              source_lang: str,
                                              ) -> list[Flashcard]:
    with open(prompts_filename, "r") as prompts:
        lines = prompts.read().strip().splitlines()
        for line in lines:
            session.add(create_flashcard_from_prompt_line(line, target_lang, source_lang))
    session.commit()


def create_anki_import_string(fcs: list[Flashcard],
                              SEP: str,
                              TAGS_COLUMN: int,
                              NOTETYPE_COLUMN: int,
                              DECK: str,
                              TAGS = list[str],
                              COLUMNS = list[str],
                              NOTETYPE = str
                              ) -> str:
    header = "\n".join([
        f'#separator:{SEP}',
        f'#tags:{" ".join(TAGS)}',
        f'#columns:{SEP.join(COLUMNS)}',
        f'#deck: {DECK}',
        f'#tags column: {TAGS_COLUMN}',
        f'#notetype column: {NOTETYPE_COLUMN}',
        ])
    body = "\n".join(list(map(lambda fc:
                              SEP.join([
                                  fc.source,
                                  fc.target,
                                  f"[sound:{fc.audio_filename}]",
                                  " ".join(TAGS + [fc.tags]),
                                  NOTETYPE]) + "|",
                              fcs)))
    return "\n\n".join([header, body])


def create_anki_import_file(anki_import_str: str,
                            anki_import_filename: str):
    with open(anki_import_filename, "w") as f:
        f.write(anki_import_str)


def create_anki_import_file_of_not_added_flashcards(batch_name: str):
    ANKI_TEXTS_DIR = "anki-textfile-outputs/"
    ANKI_IMPORT_FILENAME = f"anki-{batch_name}.txt"

    SEP = "|"
    TAGS_COLUMN = 4
    NOTETYPE_COLUMN = 5
    DECK = "alex-danish"
    TARGET_LANG = "Danish"
    SOURCE_LANG = "English"
    COLUMNS = ["source", "target", "pronunciation"]
    NOTETYPE = "Basic (and reversed) with pronunciation"

    session, engine = create_connection_to_database(DATABASE_FILE_PATH)
    fcs =  session.query(Flashcard).filter(Flashcard.added.is_(0)).all()
    anki_str = create_anki_import_string(fcs,
                               SEP,
                               TAGS_COLUMN,
                               NOTETYPE_COLUMN,
                               DECK,
                               [batch_name],
                               COLUMNS,
                               NOTETYPE)
    create_anki_import_file(anki_str, ANKI_TEXTS_DIR + ANKI_IMPORT_FILENAME)
    stmt = (
        update(Flashcard).
        where(Flashcard.added.is_(0)).
        values(added=1)
        )
    session.execute(stmt)
    session.commit()
    close_connection_to_database(session, engine)


### ANKI CONNECT


def send_request_to_anki(action: str, params: dict = None) -> bool | dict:
    payload = {"action": action,
               "version": 6,
               "params": params}
    try:
        res = requests.post(ANKI_CONNECT_BASE_URL,
                           json=payload,
                           )
        logger.debug(f"Made request: {res}")
        if res.status_code != 200:
            logger.error(f"Anki connect request for {action} had an error!")
            return False
        else:
            response_content = json.loads(res.content)
            return response_content['result']
    except requests.exceptions.ConnectionError:
        logger.error("Connection refused: is Anki running?")
        return False


def create_anki_dict_from_flashcard(fc: Flashcard) -> dict:
    res = {
            "deckName": fc.deck,
            "modelName": fc.notetype,
            "fields": {
                # NOTE these are contextual and depend on `fc.notetype`
                "source": fc.source,
                "target": fc.target,
                "pronunciation": "[sound:" + fc.audio_filename + "]"
                },
            "tags": fc.tags.split()
            }
    return res


def move_audio_files_to_anki_mediadir(fcs: list[Flashcard]) -> None:
    for fc in fcs:
        shutil.move(AUDIOS_SOURCE_DIR + fc.audio_filename,
                    AUDIOS_ANKI_DIR + fc.audio_filename)
