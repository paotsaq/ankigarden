from logger import logger
from objects import Flashcard
from const import LANG_MAP

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
