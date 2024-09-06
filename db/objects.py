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
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import MetaData

CONVENTION = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

class Base(DeclarativeBase):

    metadata = MetaData(naming_convention=CONVENTION)


class Flashcard(Base):
    __tablename__ = 'flashcards'

    id = Column(Integer, primary_key=True,
                unique=True)
    source = Column(String)
    source_lang = Column(String, default="English")
    target = Column(String)
    target_lang = Column(String, default="Danish")
    # NOTE context is used to get more accurate translations
    context = Column(Text)
    # NOTE not always do we want the audio to match the target
    # for example, with Danish nouns,
    # `friend` is `ven`, but `the friend` is `vennen`,
    # target will be `ven(nen)` but I want audio for `ven, vennen`
    target_audio_query = Column(String)
    audio_filename = Column(String)
    tags = Column(String)  # Assuming tags are stored as a comma-separated string for simplicity
    # NOTE content_type is still not very useful — but it might be
    # to distinguish whether something is a noun or a verb, etc.
    content_type = Column(String)
    deck = Column(String)
    notetype = Column(String)
    # NOTE the following is a boolean; 
    added = Column(Integer, default=0)

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
