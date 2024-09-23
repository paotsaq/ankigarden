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
from typing import List, Dict


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
        added: int = 0
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
        self.notetype = notetype
        self.added = added

    def __repr__(self):
        return ("|" +
                " | ".join([
                    f"source: {self.source}",
                    f"target: {self.target}",
                    f"context: {self.context}" if self.context else "",
                    f"audio_filename: {self.audio_filename}",
                    ]) +
                "|")

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
    part_of_speech: str
    must_get_part_of_speech: bool = False
    must_get_gender: bool = False
    must_get_parent: bool = False
    normalization_log: List[Dict[str, str]] = field(default_factory=list)

    def log_change(self, method: str, field: str, original: str, normalized: str):
        self.normalization_log.append({
            "method": method,
            "field": field,
            "original": original,
            "normalized": normalized
        })

    def normalize_tags(self):
        ALLOWED_TAGS = ['noun', 'verb', 'declension']
        TAGS_TO_SUPPRESS = ['vocabulary']
        original = self.tags
        original_tags_list = original.split()

        if original_tags_list == []:
            self.must_get_part_of_speech = True
            self.log_change("set must_get_part_of_speech", "must_get_part_of_speech",
                            False, self.must_get_part_of_speech)
            return

        lower_cased_tags = list(map(lambda tag: tag.lower(),
                                    self.tags.split()))

        if lower_cased_tags != original_tags_list:
            self.tags = " ".join(lower_cased_tags)
            self.log_change("lowercased tags", "tags", original, self.tags)

        filtered = list(filter(lambda tag: tag not in TAGS_TO_SUPPRESS,
                       original_tags_list))

        if filtered != original_tags_list:
            self.tags = " ".join(filtered)
            self.log_change("removed tags", "tags", original, self.tags)

        if 'declension' in original_tags_list and self.parent is None:
            self.must_get_parent = True
            self.log_change("set must_get_parent", "must_get_parent",
                            False, self.must_get_parent)

        if 'noun' in original_tags_list:
            ALLOWED_NAME_TAGS = ['common-gender', 'neuter-gender']
            # must have information about gender
            if not ('common-gender' in original_tags_list
                    or 'neuter-gender' in original_tags_list):
                self.must_get_gender = True
            self.log_change("set must_get_gender", "must_get_gender",
                            False, self.must_get_gender)


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

    @classmethod
    def from_lute_entry(cls, entry: LuteEntry, part_of_speech: str):
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
            part_of_speech=part_of_speech,
        )
        normalized.normalize()
        return normalized

Base = declarative_base()

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

    # Factory method to create LuteTableEntry from LuteEntry
    @classmethod
    def from_lute_entry(cls, lute_entry: 'LuteEntry') -> 'LuteTableEntry':
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
