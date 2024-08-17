from logger import logger
from sound_api import (
        download_foreign_audio
        )
from deepl_api import (
        request_translation_from_api
        )


def get_audio_from_source_query(target: str, query: str, dest_file_path: str):
    success, translation, detected_source = request_translation_from_api(target, query)
    if not success:
        return False, None, None
    if target == "DA":
        sound_target = "da-DK"
    res = download_foreign_audio(sound_target, translation, dest_file_path)
    if not res:
        return False, None, None
    return True, translation, "oops"


def get_bulk_translation_and_audio_from_textfile(target: str, source_file_path: str, dest_file_path: str):
    with open(source_file_path, "r") as bulk_content:
        lines = map(lambda line: line.strip(),
                    bulk_content.readlines())
        for query in lines:
            logger.info(f"Handling query {query}...")
            get_audio_from_source_query(target, query, dest_file_path)
