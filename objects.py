from os.path import (
        exists
        )
from deepl_api import (
    request_translation_from_api
        )
from sound_api import (
    download_foreign_audio,
    get_normalised_file_path
        )
from logger import logger
from const import (
        LANG_MAP,
        )
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Flashcard(Base):
    __tablename__ = 'flashcards'

    id = Column(Integer, primary_key=True)
    source = Column(String, unique=True)
    source_lang = Column(String)
    target = Column(String)
    target_lang = Column(String)
    # NOTE not always do we want the audio to match the target
    # for example, with Danish nouns,
    # `friend` is `ven`, but `the friend` is `vennen`,
    # target will be `ven(nen)` but I want audio for `ven, vennen`
    # target_audio_query = Column(String)
    context = Column(Text)
    deck = Column(String)
    audio_filename = Column(String)
    content_type = Column(String)
    tags = Column(String)  # Assuming tags are stored as a comma-separated string for simplicity
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

    def get_source_from_target(self):
        """fetches translation from deepL;
        defaults to english if self.source_lang is None"""
        success, translation, _ = request_translation_from_api(target_lang=LANG_MAP[self.source_lang]["deepl_code"],
                                                               query=self.target, 
                                                               source_lang=LANG_MAP[self.target_lang]["deepl_code"],
                                                               context=self.context) 
        if not success:
            logger.error("Did not update flashcard with new source!")
        self.source = translation.lower()
        logger.info(f"Updated {self.__repr__()} with source!")

    def get_audio_file_path(self):
        self.audio_filename = get_normalised_file_path(self.target)
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
                                                         self.target,
                                                         './audios/')
        if not success:
            logger.error(f"Did not download audio for {self.__repr__()}!")
            return 
