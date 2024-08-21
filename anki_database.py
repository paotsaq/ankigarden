from logger import logger
from objects import Flashcard
from const import (
        LANG_MAP,
        DATABASE_FILE_PATH
        )
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker
from objects import Base, Flashcard
from sqlalchemy.engine.base import Engine


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
