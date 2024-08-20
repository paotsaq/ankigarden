from deepl_api import (
    request_translation_from_api
        )
from sound_api import (
    download_foreign_audio
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

    def get_audio_for_target(self):
        """wraps around the sound_api functionality"""
        if not self.target:
            logger.error(f"Flashcard object has no target yet!")
            return
        success, audio_filename = download_foreign_audio(LANG_MAP[self.target_lang]["sot_code"],
                                                         self.target,
                                                         './audios/')
        if not success:
            logger.error("Did not update flashcard with audio filepath!")
        self.audio_filename = audio_filename
