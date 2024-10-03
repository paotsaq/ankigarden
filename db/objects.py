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

### LUTE_TERMS_TAGS
PARENT_TAGS = [
        'noun',
        'verb',
        'adjective',
        'conjunction',
        'preposition',
        'adverb',
        'proper-noun',
        'building',
        ]
CHILD_TAGS = [
        'declension',
        'conjugation'
        ]
ALLOWED_NOUN_TAGS = [
        'common-gender',
        'neuter-gender'
        ]
ALLOWED_VERB_TAGS = [
        'group-I',
        'group-II',
        'irregular'
        ]
TAGS_TO_SUPPRESS = ['vocabulary']
ANKIGARDEN_WORKING_TAG = "ankigarden-needs-work"
ANKIGARDEN_FINAL_TAG = "ankigarden-term"

@dataclass
class LuteEntry:
    term: str
    parent: str
    translation: str
    language: str
    tags: str
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

    def __repr__(self):
        return (f"term: {self.term} | translation: {self.translation} | parent: {self.parent}")


@dataclass
# NOTE this is still very hardcoded for Danish!
class NormalizedLuteEntry(LuteEntry):
    must_get_part_of_speech: bool = False
    must_get_parent: bool = False
    must_get_definition: bool = False
    must_get_gender: bool = False
    must_get_conjugation_pattern: bool = False
    must_clean_ion_tag: bool = False
    normalization_log: List[Dict[str, str]] = field(default_factory=list)

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
            # TODO load `must_` flags from tags?
        )
        # NOTE I'm not sure this is good practice;
        # it should not be taken for granted that normalisation happens at creation
        normalized.normalize()
        return normalized

    def log_change(self, method: str, field: str, original: str, normalized: str, fixed: bool = True):
        self.normalization_log.append({
            "method": method,
            "field": field,
            "original": original,
            "normalized": normalized,
            "fixed": fixed
        })

    def normalize_tags(self):
        original = self.tags
        original_tags_list = original.split()

        # lowercase tags
        lower_cased_tags = list(map(lambda tag: tag.lower(),
                                    original_tags_list))

        if lower_cased_tags != original_tags_list:
            self.tags = " ".join(lower_cased_tags)
            self.log_change("lowercased tags", "tags", original, self.tags)

        # removes unnecessary tags
        filtered = list(filter(lambda tag: tag not in TAGS_TO_SUPPRESS,
                       original_tags_list))

        if filtered != original_tags_list:
            self.tags = " ".join(filtered)
            self.log_change("removed tags", "tags", original, self.tags)

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

    def normalize_get_translation(self):
        if self.translation == '':
            self.must_get_definition = True
            self.log_change("set must_get_definition", "must_get_definition",
                            False, self.must_get_definition, False)

    # NOTE determine specifics about the term role
    def normalize_term_part_of_speech(self):
        if 'noun' in self.tags.split():
            # noun must have information about gender
            if not any(filter(lambda tag: tag in self.tags,
                              ALLOWED_NOUN_TAGS)):
                self.must_get_gender = True
                self.log_change("set must_get_gender", "must_get_gender",
                                False, self.must_get_gender, False)
        elif 'verb' in self.tags.split():
            # verb must have conjugation pattern tag
            if not any(filter(lambda tag: tag in self.tags,
                              ALLOWED_VERB_TAGS)):
                self.must_get_conjugation_pattern = True
                self.log_change("set must_get_conjugation_pattern", "must_get_conjugation_pattern",
                                False, self.must_get_conjugation_pattern, False)


    # NOTE determine whether it is a parent or a child
    # (noun, verb, etc. are parents; declensions or conjugations of
    # these terms are children)
    def normalize_parent_or_child(self):
        # ensure information on part of speech (parent tag)
        any_part_of_speech = any(filter(lambda tag: tag in self.tags,
                                        PARENT_TAGS))
        # checks for child tags
        any_child_tags = any(filter(lambda tag: tag in self.tags,
                                    CHILD_TAGS))
                       # is either a parent term with no child tags
        parent_or_child = (self.parent == '' and not any_child_tags or  
                       # a child with parent information & information on relation
                       self.parent != '' and any_child_tags)
        if not parent_or_child:
            if any_child_tags:
                self.must_get_parent = True
                self.log_change("set must_get_parent", "must_get_parent",
                            False, self.must_get_parent, False)
        if not any_part_of_speech:
            self.must_get_part_of_speech = True
            self.log_change("set must_get_part_of_speech", "must_get_part_of_speech",
                            False, self.must_get_part_of_speech, False)


    def normalize(self):
        self.normalize_remove_extra_spaces()
        self.normalize_lowercase()
        self.normalize_tags()
        self.normalize_get_translation()
        self.normalize_parent_or_child()
        self.normalize_term_part_of_speech()


    def fix_logged_problems(self):
        # if self.status == 'W':
            # logger.warning(f"{self.term} seems to be a learned word. Will skip querying and try matching to Anki database.")
        # else:
        if self.must_get_part_of_speech:
            if len(self.term.split()) > 1:
                logger.info(f"Found more than one word. Is {self.term} a `building` or `common-phrase`?")
                self.tags += " ".join(self.tags.split() + ["is-compound-term"])
            else:
                # TODO later this will be shielded by an API call
                try:
                    categories = get_word_definition(self.term, "Danish")
                    if categories:
                        self.tags += " ".join(list(map(lambda cat: cat["type"],
                                                        categories)))
                        # TODO 'conjugation' should be removed in this case
                        # TODO create parent entry if there is none
                        self.parent += " ".join(list(map(lambda cat: cat["parent"],
                                                        filter(lambda cat: 'parent' in cat,
                                                               categories))))
                        part_of_speech_log = next(filter(lambda log: log["field"] == "must_get_part_of_speech",
                                                    self.normalization_log))
                        # NOTE I don't like this — mutability is iffy. Should be a proper copy.
                        new_log = part_of_speech_log
                        new_log["fixed"] = True
                        self.normalization_log.remove(part_of_speech_log) 
                        self.normalization_log.append(new_log)
                        self.must_get_part_of_speech = False
                except Exception as e:
                    logger.error(f"Problems in Wiktionary API. This is not on the scope of normalisation.\n{e.str}")
    
    def check_eligibility_for_final_tag(self):
        return not (
            self.must_get_part_of_speech or
            self.must_get_parent or
            self.must_get_gender or
            self.must_get_definition or
            self.must_get_conjugation_pattern or
            self.must_clean_ion_tag
            ) 


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


    @classmethod
    def from_lute_entry(cls, lute_entry: NormalizedLuteEntry):
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

    def __repr__(self):
        return (f"term: {self.term} | translation: {self.translation} | parent: {self.parent}")


# NOTE this might not be needed after all
def convert_to_normalized_lute_entry(table_entry: LuteTableEntry) -> NormalizedLuteEntry:
    lute_entry = LuteEntry(
        term=table_entry.term,
        parent=table_entry.parent,
        translation=table_entry.translation,
        language=table_entry.language,
        tags=table_entry.tags,
        added=table_entry.added,
        status=table_entry.status or '',
        link_status=table_entry.link_status,
        pronunciation=table_entry.pronunciation
    )
    
    normalized_entry = NormalizedLuteEntry.from_lute_entry(lute_entry)
    return normalized_entry


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
        # added_to_anki: bool = False
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

    def __repr__(self):
        return ("|" +
                " | ".join([
                    f"source: {self.source}",
                    f"target: {self.target}",
                    f"context: {self.context}" if self.context else "",
                    f"audio_filename: {self.audio_filename}",
                    ]) +
                "|")

    @classmethod
    def from_lute_entry(cls, entry: NormalizedLuteEntry) -> Optional['Flashcard']:
        return cls(
            source=entry.translation,
            # NOTE this is the default!
            source_lang="English",
            target=entry.term,
            target_lang=entry.language,
            tags=entry.tags,
            )


    def generate_target_audio_query(self) -> None:
        pass

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
                                                         AUDIOS_SOURCE_DIR)
        if not success:
            logger.error(f"Did not download audio for {self.__repr__()}!")
            return 
