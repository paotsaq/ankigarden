from logger import logger
from objects import Flashcard
from const import (
        LANG_MAP,
        DATABASE_FILE_PATH
        )
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from objects import Base, Flashcard


# NOTE I think this is still untested?
def retrieve_flashcards_from_database(database_path: str) -> list[Flashcard]:
    engine = create_engine('sqlite://' + database_path)
    intermediate_session = sessionmaker(bind=engine)
    session = intermediate_session()
    fcs = session.query(Flashcard).all()
    session.close()
    engine.dispose()
    return fcs


def import_prompts_from_text_file(filename: str,
                                  database_path: str,
                                  batch_tags: list[str]
                                  ) -> list[Flashcard]:
    engine = create_engine(f'sqlite://{database_path}', echo=True)
    fcs = []

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        with open("prompts.txt", "r") as prompts:
            lines = prompts.read().strip().splitlines()
        for line in lines:
            if '|' in line:
                query, context = line.split('|')
            else:
                query = line
                context = None
            fc = Flashcard(target_lang = "Danish",
                           target = query,
                           source_lang = "English",
                           context = context,
                           deck = "alex-danish",
                           notetype = "Basic (and reversed) with pronunciation",
                           tags = " ".join(batch_tags))
            fc.get_source_from_target()
            # fc.get_audio_for_target()
            fcs.append(fc)
            session.add(fc)
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
                                  " ".join(TAGS),
                                  NOTETYPE]) + "|",
                              fcs)))
    return "\n\n".join([header, body])


def create_anki_import_file(anki_import_str: str,
                            anki_import_filename: str):
    with open(anki_import_filename, "w") as f:
        f.write(anki_import_str)
