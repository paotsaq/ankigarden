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
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base


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
            status=str(lute_entry.status),  # Convert status to string
            link_status=lute_entry.link_status,
            pronunciation=lute_entry.pronunciation,
        )
