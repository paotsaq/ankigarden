import requests
from const import (
        SOUNDS_ENDPOINT
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
import os

# NOTE this function is not necessarily of this scope;
# maybe more fit for a `utils.py`?
def get_normalised_file_path(query: str) -> str:
    return query.replace(" ", "_").lower().strip('.') + '.mp3'


def request_sound_from_api(language: str, query: str) -> Tuple[bool, str]:
    """produces a request to the API to generate a sound

    returns a bool indicating success of query
    and a str with the resulting audio_id"""
    payload = {"data": {"text": query + "   ", "voice": language}}
    res = requests.post(SOUNDS_ENDPOINT,
                       json=payload,
                       )
    logger.debug(f"Made request: {res}")
    if res.status_code != 200:
        logger.error(f"Response code was {res.status_code}!")
        logger.error(f"{res.reason}")
        content_str = dumps(loads(res.content), indent=2)
        logger.error(f"Error message: {content_str}")
        return False, None
    else:
        audio_id = loads(res.content)['id']
        logger.debug(f"Request was successful! audio_id is {audio_id}")
        return True, audio_id


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
    logger.debug(f"Made request: {res}")
    if res.status_code == 200:
        loaded_content =  loads(res.content)
        if loaded_content["status"] == "Pending":
            logger.debug(f"Audio creation was pending!\nWill retry in 5 seconds.")
            sleep(5)
            return request_sound_from_api(audio_id, retries + 1)
        else:
            audio_url = loads(res.content)['location']
            logger.debug(f"Request was successful!\naudio_url is {audio_url}")
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
        logger.debug(f'Successfully downloaded {file_path}')
        return True
    else:
        logger.error(f'Failed to download the file.\nStatus code: {response.status_code}')
        return False


def download_foreign_audio(language: str, query: str, audio_path: str) -> Tuple[bool, str]:
    sound_request_successful, audio_id = request_sound_from_api(language, query)
    if not sound_request_successful:
        logger.error(f"Request for {query} was not successful!")
        return False, None
    retrieve_request_successful, audio_url = retrieve_sound_from_api(audio_id, 0)
    if not retrieve_request_successful:
        logger.error(f"URL retrieval for {query} | audio_id: {audio_id} was not successful!")
        return False, None
    file_name = get_normalised_file_path(query)
    file_path = (audio_path +
                 ('/' if audio_path[0] != '/' else
                  '') +
                 file_name)
    if not saves_audio_file(audio_url, file_path):
        logger.error(f"Saving of {query} | audio_id: {audio_id} | audio_url: {audio_url} was not successful!")
        return False, None
    return True, file_name


# NOTE untested!
def get_bulk_audio_from_textfile(target: str, source_file_path: str, dest_file_path: str):
    with open(source_file_path, "r") as bulk_content:
        lines = map(lambda line: line.strip(),
                    bulk_content.readlines())
        for query in lines:
            logger.info(f"Handling query for {query}...")
            download_foreign_audio(target, query, dest_file_path)
    logger.info("All done!")
