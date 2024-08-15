import requests
from const import (
        TRANSLATE_ENDPOINT
        )
from typing import Tuple
from logger import logger
from json import (
        loads,
        dumps
        )
from time import (
        sleep
        )
from dotenv import load_dotenv
import os
import deepl


def request_translation_from_api(target_lang: str, query: str, source_lang: str = None) -> Tuple[bool, str]:
    """produces a request to the API to generate a translation

    returns a bool indicating success of query
    and a str with the resulting translation"""

    # NOTE this should be elsewere, surely?
    load_dotenv()
    api_key = os.getenv('DEEPL_API_KEY')

    translator = deepl.Translator(api_key)

    try: 
        res = translator.translate_text(query, target_lang=target_lang, source_lang=source_lang)
        logger.info(f"Made request: {res}")
    except deepl.exceptions.DeepLException as e:
        logger.error(f"There was a problem!")
        logger.error(e)
        return False, None
    else:
        translation = res.text
        logger.info(f"Request was successful! translation is {translation}")
        return True, translation


def retrieve_sound_from_api(audio_id: str, retries: int) -> Tuple[bool, str]:
    """produces a request to the API

    returns a bool indicating success of query
    and a str with the resulting audio_stream_url

    if the audio is not ready ("Pending" response)
    will retry for a max of 5 tries. """
    MAX_TRIES = 5
    if retries == MAX_TRIES:
        logger.error(f"Request failed! Maximum retries of {MAX_TRIES} achieved.")
        return False, None
    res = requests.get(SOUNDS_ENDPOINT + audio_id)
    logger.info(f"Made request: {res}")
    if res.status_code == 200:
        loaded_content =  loads(res.content)
        if loaded_content["status"] == "Pending":
            logger.debug(f"Audio creation was pending!\nWill retry in 5 seconds.")
            sleep(5)
            return request_sound_from_api(audio_id, retries + 1)
        else:
            audio_url = loads(res.content)['location']
            logger.info(f"Request was successful!\naudio_url is {audio_url}")
            return True, audio_url
    elif res.status_code == 400:
        logger.error(f"Response code was {res.status_code}!")
        logger.error(f"{res.reason}")
        content_str = dumps(loads(res.content), indent=2)
        logger.error(f"Error message: {content_str}")
        return False, None


def saves_audio_file(web_audio_path: str, file_path: str) -> bool:
    response = requests.get(web_audio_path, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.info(f'Successfully downloaded {file_path}')
        return True
    else:
        logger.error(f'Failed to download the file.\nStatus code: {response.status_code}')
        return False


def download_foreign_audio(language: str, query: str, file_path: str = None) -> bool:
    sound_request_successful, audio_id = request_sound_from_api(language, query)
    if not sound_request_successful:
        logger.error(f"Request for {query} was not successful!")
        return False
    retrieve_request_successful, audio_url = retrieve_sound_from_api(audio_id, 0)
    if not retrieve_request_successful:
        logger.error(f"URL retrieval for {query} | audio_id: {audio_id} was not successful!")
        return False
    if not file_path:
        file_path = query.replace(" ", "_").lower() + '.mp3'
    if not saves_audio_file(audio_url, file_path):
        logger.error(f"Saving of {query} | audio_id: {audio_id} | audio_url: {audio_url} was not successful!")
        return False
    return True
