
<h1>ankigarden: an Anki flashcard automation tool</h1> 

because language learning can be done *quicker* 🏃

## Why this, Alex?

Hello! I have been spending much time learning languages in the past few months and this is a tool that strives to make that process a bit easier. There's some general information about the project [here](https://sbsbsb.sbs/ankigarden).


## And what does it do?

For a better understanding of what I was trying to solve, it might be useful to check the [motivation](https://sbsbsb.sbs/old-anki-procedure) for the project. At the moment, it is a good tool to process some phrases/vocabulary, and it handles bidireccional input (so you can query in Danish and get English, and the other way around).

## Is it finished?

Not by any chance! But a few friends have asked to use it — and I could really use the feedback. So this is still a private repository, and lots of work shall still be done.


## And how can I get this thing going?

Yep! Let's go.

Ensure you have Anki running on your machine; [AnkiConnnect](https://ankiweb.net/shared/info/2055492159) should be installed and running.

You should check the `const.py` file, where some constants are defined. The following are important, as they are specific to your AnkiConnect config, and also the directories to save the audio files to:

```
ANKI_CONNECT_BASE_URL = "http://localhost:8765/"

AUDIOS_SOURCE_DIR = "./audios/"
AUDIOS_ANKI_DIR = "./anki_audios_dir/"
```

My `USE_CONFIG` for Danish, for example:

```
USE_CONFIGS = {
        "english-to-danish": {
            "deck": "alex-danish",
            "target_lang": "Danish",
            "source_lang": "English",
            "notetype": "Basic (and reversed) with pronunciation"
            }
}
```

(I now realise you should also have my notetype `Basic (and reversed) with pronunciation` on your Anki; I'll figure this out.)
