DEEPL_API_BASE_URL = "https://api-free.deepl.com/v2/"
TRANSLATE_ENDPOINT = DEEPL_API_BASE_URL + "translate/"

SOUND_API_BASE_URL = "https://api.soundoftext.com/"
SOUNDS_ENDPOINT = SOUND_API_BASE_URL + "sounds/"

DATABASE_FILE_PATH = "/ankigarden.db"
ANKI_CONNECT_BASE_URL = "http://localhost:8765/"

AUDIOS_SOURCE_DIR = "./audios/"
AUDIOS_ANKI_DIR = "./anki_audios_dir/"

USE_CONFIGS = {
        "english-to-danish": {
            "deck": "alex-danish",
            "target_lang": "Danish",
            "source_lang": "English",
            "notetype": "Basic (and reversed) with pronunciation"
            },
        "english-to-greek": {
            "deck": "alex-greek",
            "target_lang": "Greek",
            "source_lang": "English",
            "notetype": "Basic (and reversed) with pronunciation"
            }

        }

EMOJI_FLAG = {
        "Danish": "🇩🇰",
        "English": "🇬🇧",
        "Greek": "🇬🇷",
        }

LANG_MAP = {
        "Greek": {
            "deepl_code": "EL",
            "sot_code": "el-GK"
            },
        "Danish": {
            "deepl_code": "DA",
            "sot_code": "da-DK"
            },
        "English": {
            "deepl_code": "EN-US",
            "sot_code": ""
        }
    }

# SUPPORTED_DEEPL_TARGET = {
        # "AR": "Arabic",
        # "BG": "Bulgarian",
        # "CS": "Czech",
        # "DA": "Danish",
        # "DE": "German",
        # "EL": "Greek",
        # "EN-GB": "English (British)",
        # "EN-US": "English (American)",
        # "ES": "Spanish",
        # "ET": "Estonian",
        # "FI": "Finnish",
        # "FR": "French",
        # "HU": "Hungarian",
        # "ID": "Indonesian",
        # "IT": "Italian",
        # "JA": "Japanese",
        # "KO": "Korean",
        # "LT": "Lithuanian",
        # "LV": "Latvian",
        # "NB": "Norwegian Bokmål",
        # "NL": "Dutch",
        # "PL": "Polish",
        # "PT-BR": "Portuguese (Brazilian)",
        # "PT-PT": "Portuguese (all Portuguese variants excluding Brazilian Portuguese)",
        # "RO": "Romanian",
        # "RU": "Russian",
        # "SK": "Slovak",
        # "SL": "Slovenian",
        # "SV": "Swedish",
        # "TR": "Turkish",
        # "UK": "Ukrainian",
        # "ZH-HANS": "Chinese (simplified)",
        # "ZH-HANT": "Chinese (traditional)"
    # }
