from os.path import (
        exists
)
from apis.deepl_api import (
    request_translation_from_api
        )
from apis.sound_api import (
    download_foreign_audio,
    get_normalised_file_path
        )
from logger import logger
from const import (
        LANG_MAP,
        )
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from typing import List, Dict, Optional
from apis.wiktionary import (
        get_word_definition
        )

Base = declarative_base()

@dataclass
class LuteEntry:
    term: str
    parent: str
    translation: str
    language: str
    tags: list[str]
    added: datetime
    status: str
    link_status: str
    pronunciation: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            term=data['term'],
            parent=data['parent'],
            translation=data['translation'],
            language=data['language'],
            tags=data['tags'],
            added=datetime.strptime(data['added'], '%Y-%m-%d %H:%M:%S'),
            status='' if data['status'] is None else data['status'],
            link_status=data['link_status'],
            pronunciation=data['pronunciation']
        )

    def knowledge_level(self) -> str:
        if self.status == '':
            return "NoInfo"
        elif self.status == 'W':
            return "Known"
        elif self.status in "12345":
            return "Learning"
        else:
            raise Exception


@dataclass
# NOTE this is still very hardcoded for Danish!
class NormalizedLuteEntry(LuteEntry):
    must_get_part_of_speech: bool = False
    must_get_gender: bool = False
    must_get_parent: bool = False
    must_clean_ion_tag: bool = False
    normalization_log: List[Dict[str, str]] = field(default_factory=list)

    def log_change(self, method: str, field: str, original: str, normalized: str, fixed: bool = True):
        self.normalization_log.append({
            "method": method,
            "field": field,
            "original": original,
            "normalized": normalized,
            "fixed": fixed
        })

    def normalize_tags(self):
        ALLOWED_TAGS = ['noun', 'verb', 'declension', 'conjugation']
        TAGS_TO_SUPPRESS = ['vocabulary']
        original = self.tags
        original_tags_list = original.split(", ")

        # no information about a given term
        # these might be flashcarded already, too
        # TODO separate into `parent` case?
        if original_tags_list == ['']:
            self.must_get_part_of_speech = True
            self.log_change("set must_get_part_of_speech", "must_get_part_of_speech",
                            False, self.must_get_part_of_speech, False)
            return

        # lowercase tags
        lower_cased_tags = list(map(lambda tag: tag.lower(),
                                    self.tags.split(", ")))

        if lower_cased_tags != original_tags_list:
            self.tags = " ".join(lower_cased_tags)
            self.log_change("lowercased tags", "tags", original, self.tags)

        # removes unnecessary tags
        filtered = list(filter(lambda tag: tag not in TAGS_TO_SUPPRESS,
                       original_tags_list))

        if filtered != original_tags_list:
            self.tags = " ".join(filtered)
            self.log_change("removed tags", "tags", original, self.tags)

        # in lute, parent and child terms share tags; so it is possible
        # that a derivation has no parent and must be matched
        if 'declension' in original_tags_list or 'conjugation' in original_tags_list:
            if self.parent is None:
                self.must_get_parent = True
                self.log_change("set must_get_parent", "must_get_parent",
                                False, self.must_get_parent, False)
            else:
                # NOTE I'm not sure what happens in these cases.
                self.must_clean_ion_tag = True
                self.log_change("set must_clean_ion_tag", "must_clean_ion_tag",
                                False, self.must_clean_ion_tag, False)
                pass

        if 'noun' in original_tags_list:
            ALLOWED_NAME_TAGS = ['common-gender', 'neuter-gender']
            # must have information about gender
            if not ('common-gender' in original_tags_list
                    or 'neuter-gender' in original_tags_list):
                self.must_get_gender = True
                self.log_change("set must_get_gender", "must_get_gender",
                                False, self.must_get_gender, False)

    def normalize_lowercase(self):
        original = self.term
        self.term = self.term.lower()
        if original != self.term:
            self.log_change("lowercased term", "term", original, self.term)

    def normalize_remove_extra_spaces(self):
        original = self.term
        self.term = ' '.join(self.term.split())
        if original != self.term:
            self.log_change("removed extra spaces", "term", original, self.term)

    def normalize(self):
        self.normalize_remove_extra_spaces()
        self.normalize_lowercase()
        self.normalize_tags()

    def fix_logged_problems(self):
        if self.must_get_part_of_speech:
            # TODO later this will be shielded by an API call
            categories = get_word_definition(self.term, "Danish")
            if categories:
                self.tags += ", ".join(list(map(lambda cat: cat["type"],
                                                categories)))
                # TODO 'conjugation' should be removed in this case
                # TODO create parent entry if there is none
                self.parent += ", ".join(list(map(lambda cat: cat["parent"],
                                                filter(lambda cat: 'parent' in cat,
                                                       categories))))
                part_of_speech_log = next(filter(lambda log: log["field"] == "must_get_part_of_speech",
                                            self.normalization_log))
                # NOTE I don't like this — mutability is iffy. Should be a proper copy.
                new_log = part_of_speech_log
                new_log["fixed"] = True
                self.normalization_log.remove(part_of_speech_log) 
                self.normalization_log.append(new_log)


    @classmethod
    def from_lute_entry(cls, entry: LuteEntry):
        normalized = cls(
            term=entry.term,
            parent=entry.parent,
            translation=entry.translation,
            language=entry.language,
            tags=entry.tags,
            added=entry.added,
            status=entry.status,
            link_status=entry.link_status,
            pronunciation=entry.pronunciation,
        )
        normalized.normalize()
        return normalized



class LuteTableEntry(Base):
    __tablename__ = 'lute_terms'

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False)
    parent = Column(String)
    translation = Column(String)
    language = Column(String, nullable=False)
    tags = Column(String)
    added = Column(DateTime, nullable=False)
    status = Column(String)
    link_status = Column(String)
    pronunciation = Column(String)
    anki_note_id = Column(Integer)
    last_synced = Column(DateTime)


    # this will be done from NormalizedLuteEntry, actually
    @classmethod
    def from_lute_entry(cls, lute_entry: NormalizedLuteEntry) -> LuteTableEntry:
        return cls(
            term=lute_entry.term,
            parent=lute_entry.parent,
            translation=lute_entry.translation,
            language=lute_entry.language,
            tags=lute_entry.tags, 
            added=lute_entry.added,
            status=lute_entry.status,
            link_status=lute_entry.link_status,
            pronunciation=lute_entry.pronunciation,
        )


class Flashcard:
    def __init__(
        self,
        source: str = "",
        source_lang: str = "English",
        target: str = "",
        target_lang: str = "Danish",
        context: str = "",
        target_audio_query: str = "",
        audio_filename: str = "",
        tags: str = "",
        content_type: str = "",
        deck: str = "",
        notetype: str = "",
        added_lute_timestamp: int = 0,
        added_to_anki: bool = False
    ):
        self.source = source
        self.source_lang = source_lang
        self.target = target
        self.target_lang = target_lang
        self.context = context
        self.target_audio_query = target_audio_query
        self.audio_filename = audio_filename
        self.tags = tags
        self.content_type = content_type
        self.deck = deck
        self.added_lute_timestamp = added_lute_timestamp
        self.added_to_anki = added_to_anki

    def __repr__(self):
        return ("|" +
                " | ".join([
                    f"source: {self.source}",
                    f"target: {self.target}",
                    f"context: {self.context}" if self.context else "",
                    f"audio_filename: {self.audio_filename}",
                    ]) +
                "|")

    # this will be done from NormalizedLuteEntry, actually
    @classmethod
    def from_lute_entry(cls, entry: LuteEntry) -> Optional['Flashcard']:
        ALLOWED_TAGS = [
                'verb',
                'noun',
                'building',
                'conjunction',
                'adverb'
                ]
        tags = entry.tags.split(', ')
        
        if any(map(lambda tag: tag in ALLOWED_TAGS, 
                   tags)):
            return cls(
                source=entry.term,
                target=entry.translation,
                context=entry.parent,
                tags=entry.tags,
                added_lute_timestamp=int(datetime.strptime(entry.added, "%Y-%m-%d %H:%M:%S").timestamp()),
                added_to_anki=False
            )
        else:
            return None


    def get_translation(self, invert: bool = False) -> bool:
        """fetches translation from deepL;
        if `invert`, then it reverses the query,
        defaults to english if self.source_lang is None"""
        # TODO this can be prettier, but I'll leave it for now
        # NOTE is it sensible to have api dependencies out of this module?
        logger.debug(f"NOW ON SENDING { self.source_lang } { self.target_lang } {invert}")
        if not invert:
            target_lang = LANG_MAP[self.source_lang]["deepl_code"]
            source_lang = LANG_MAP[self.target_lang]["deepl_code"]
            query = self.target
        else:
            target_lang = LANG_MAP[self.target_lang]["deepl_code"]
            source_lang = LANG_MAP[self.source_lang]["deepl_code"]
            query = self.source
        logger.debug(target_lang, source_lang, query)
        success, translation, _ = request_translation_from_api(target_lang=target_lang,
                                                               query=query, 
                                                               source_lang=source_lang[:2],
                                                               context=self.context) 
        if not success:
            logger.error("Did not update flashcard with translation!")
            return False
        if invert:
            self.target = translation.lower()
        else:
            self.source = translation.lower()
        logger.info(f"Updated {self.__repr__()} with translation!")
        return True

    def get_audio_file_path(self):
        self.audio_filename = get_normalised_file_path(self.target_audio_query)
        logger.info(f"Updated {self.__repr__()} with new audio_filename!")

    def get_audio_file(self):
        """wraps around the sound_api functionality"""
        if not self.target:
            logger.error(f"{self.__repr__()} has no target yet!")
            return
        if exists("./audios/" + self.audio_filename):
            logger.error(f"{self.__repr__()} has matching audio downloaded!")
            return
        success, audio_filename = download_foreign_audio(LANG_MAP[self.target_lang]["sot_code"],
                                                         self.target_audio_query,
                                                         './audios/')
        if not success:
            logger.error(f"Did not download audio for {self.__repr__()}!")
            return 
