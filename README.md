<h1>ankigarden: an Anki flashcard automation tool</h1> 

because language learning can be done *quicker* 🏃

## Why this, Alex?

Hello! I have been spending much time learning languages in the past few months and this is a tool that strives to make that process a bit easier. There's some general information about the project [here](https://sbsbsb.sbs/ankigarden).

My language learning studies usually imply long dialogues with online dictionaries/translation tools, and lots of manual input. This tool aims to automate most of that, creating Anki flashcards in a quicker fashion.

For a better understanding of what I was trying to solve, it might be useful to check the [motivation](https://sbsbsb.sbs/old-anki-procedure) for the project. At the moment, it is a good tool to process some phrases/vocabulary, and it handles bidireccional input (so you can query in Danish and get English, and the other way around). 

(it also supports other language combinations, but I haven't put much effort (yet?) into making that more accessible, nor is it thoroughly tested)

![the MVP for the Ankigarden looks like this](https://sbsbsb.sbs/images/ankigarden_final_public_version.png)

## Cool! And how?

In fact, it is not doing anything too fancy: it's mostly API calls and some mild logic to create flashcards. 

This relies on [DeepL](https://deepl.com) for text translations and [SoundOfText](https://soundoftext.com) for pronunciation audio generation (and a special thanks goes to [Flora Moon](https://soundoftext.com/#about) for the latter tool 💞); you need an account for the first; for SoundOfText, just try to be mindful of data use — and in the future I'll try to think of a more robust solution, too.

## Is it finished?

Not by any chance! But a few friends have asked to use it — and I could really use the feedback. So this is still a private repository, and lots of work shall still be done — you can the roadmap yourself at [the log](https://sbsbsb.sbs/ankigarden-log) — but for the time-being, I don't think there will be any major works on this (I need to actually __use__ the tool instead of just tinkering with it!).

## And how can I get this thing going?

Yep! Let's go.

- install the `requirements.txt` as usual, in, ideally, a Python virtual environment ([just do it the usual way](https://docs.python.org/3/library/venv.html#creating-virtual-environments), or use something fancier like [direnv](https://github.com/direnv/direnv) instead)

- Ensure you have Anki running on your machine; [AnkiConnnect](https://ankiweb.net/shared/info/2055492159) should be installed and running;

- Manually import the `sample-deck-ankigarden.apkg` into your machine. This will implicitly also import my `Basic (and reversed) with pronunciation` notetype, which, to start with, can be useful (but you can now, or later, modify your notetypes as you wish);

```
ANKI_CONNECT_BASE_URL = "http://localhost:8765/"

AUDIOS_SOURCE_DIR = "./audios/"
AUDIOS_ANKI_DIR = "./anki_audios_dir/"
```

The `AUDIOS_SOURCE_DIR` is a temporary directory in which generated audio files are stored; upon flashcard creation, they are moved to `AUDIOS_ANKI_DIR` — this latter is not arbitrary: [the official documentation](https://docs.ankiweb.net/files.html#file-locations) discloses the paths (which are different between Windows and Linux). For example, mine is at `~/.local/share/Anki2/alex/collection.media`, but then I created a symbolic link (similar to Windows' shortcuts) and mapped it to `anki_audios_dir`.

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

Then...err...fool around! It __should__ work, but you know how to reach me for any questions or problems arising (and I'll try to fix them, too!).

Oh, and I almost forgot: for now, it runs as `python main.py`

## Anything else I should know?

Yes! The usual workflow is to

a) write a prompt on `target` or `source`; press `Enter`.

(optionally, fill the `context` prompt to reduce ambiguity or try to *massage* the output into specific words or terms)

b) the `audio` pronunciation field should have been automatically filled; press `Enter` to retrieve (download) the pronunciation file.

(also, if `noun` is in `tags`, it will gemerate twice the pronunciation prompt; this is useful for Danish in particular, since, for example, *bog* is *book*, but *the book* is *bogen*; words are suffixed by their gender article — either *en* or *et*; this will be further worked upon, but the idea is to also get the gender of the word on the flashcard).

c) when the audio file is retrieved, the flashcard is ready to be saved.
