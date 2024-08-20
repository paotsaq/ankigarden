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


def request_translation_from_api(target_lang: str, query: str, source_lang: str = None, context: str = None) -> Tuple[bool, str, str]:
    """produces a request to the API to generate a translation

    returns 
    - a bool indicating success of query
    - a str with the resulting translation
    - a str with the detected_source_lang"""

    # NOTE this should be elsewere, surely?
    load_dotenv()
    api_key = os.getenv('DEEPL_API_KEY')

    translator = deepl.Translator(api_key)

    try: 
        logger.debug(f"Made request: query: {query} | target_lang: {target_lang} | source_lang: {source_lang} | context: {context}")
        res = translator.translate_text(query,
                                        target_lang=target_lang,
                                        source_lang=source_lang,
                                        context=context)
        logger.debug(f"Received response: translation: {res} | target_lang: {target_lang} | source_lang: {source_lang}")
    except deepl.exceptions.DeepLException as e:
        logger.error(f"There was a problem!")
        logger.error(e)
        return False, None, None
    else:
        translation = res.text
        detected_source = None if target_lang is None else res.detected_source_lang
        logger.debug(f"Request was successful! translation is {translation}")
        return True, translation, detected_source
