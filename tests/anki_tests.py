import unittest
from sound_api import (
        download_foreign_audio
        )
from os.path import exists
from os import remove
from const import LANG_MAP
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from objects import Base, Flashcard
from anki_database import (
        retrieve_all_flashcards_from_database,
        create_anki_import_string,
        parse_line_from_prompt,
        create_flashcard_from_prompt_line,
        import_prompts_from_text_file_to_database
        )

TEST_FILES_DIR = "tests/test-files/"

class TestSimpleDatabaseHandling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup test database
        cls.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

    @classmethod
    def tearDownClass(cls):
        # Teardown test database
        cls.session.close()
        cls.engine.dispose()

    # the Flashcard class will have all information pertaining to a flashcard.
    def setUp(self):
        self.fc = Flashcard(target_lang = "Danish", target = "fordi", source_lang = "English")

    def test_can_initialise_Flashcard_object(self):
        self.assertTrue(self.fc is not None)

    def test_save_and_load_flashcard_from_database(self):
        """Test saving a Flashcard to the database and loading it back."""
        # Save a flashcard
        self.session.add(self.fc)
        self.session.commit()

        # Load the flashcard back
        loaded_fc = self.session.query(Flashcard).filter_by(target="fordi").one()
        self.assertEqual(loaded_fc.target, "fordi")
        self.assertEqual(loaded_fc.target_lang, "Danish")
        self.assertEqual(loaded_fc.source_lang, "English")


class TestPromptFileHandlingFlashcardCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup test database
        cls.engine = create_engine('sqlite:///')
        Base.metadata.create_all(cls.engine)
        # NOTE what?
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

    @classmethod
    def tearDownClass(cls):
        # Teardown test database
        cls.session.close()
        cls.engine.dispose()

    def test_can_parse_single_line_of_prompt(self):
        first = "one"
        query, tags, context = parse_line_from_prompt(first)
        self.assertTrue(query == "one" and tags is None and context is None)
        second = "one|two"
        query, tags, context = parse_line_from_prompt(second)
        self.assertTrue(query == "one" and tags == "two" and context is None)
        third = "one|two|three"
        query, tags, context = parse_line_from_prompt(third)
        self.assertTrue(query == "one" and tags == "two" and context == "three")

    def test_can_create_flashcard_from_prompt_line(self):
        first_prompt = "hvor længe er der åbent?|common-phrases nice sentence"
        target = "Danish"
        source = "English"
        first_fc = create_flashcard_from_prompt_line(first_prompt, target, source)
        self.assertTrue(first_fc.target == "hvor længe er der åbent?" and
                        first_fc.target_lang == "Danish" and
                        first_fc.source_lang == "English" and
                        first_fc.tags == "common-phrases nice sentence")

    def test_can_parse_prompt_file_and_create_flashcards(self):
        prompts_filepath = TEST_FILES_DIR + "test-last-prompts.txt"
        import_prompts_from_text_file_to_database(prompts_filepath,
                                                  self.session,
                                                  "Danish",
                                                  "English"
                                                  )
        fcs = retrieve_all_flashcards_from_database(self.session)
        self.assertEqual(len(fcs), 3)


class TestAnkiImportFileCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup test database
        cls.engine = create_engine('sqlite:///./tests/test-ankigarden.db')
        Base.metadata.create_all(cls.engine)
        # NOTE what?
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

    @classmethod
    def tearDownClass(cls):
        # Teardown test database
        cls.session.close()
        cls.engine.dispose()

    def test_can_load_all_flashcards(self):
        fcs = retrieve_all_flashcards_from_database(self.session)
        self.assertEqual(len(fcs), 5)

    def test_can_produce_anki_import_string(self):
        # NOTE I seem to have lost the database at some point.
        # must recreate it at some point
        fcs = retrieve_all_flashcards_from_database(self.session)
        self.maxDiff = None
        SEP = "|"
        TAGS_COLUMN = 4
        NOTETYPE_COLUMN = 5
        DECK = "alex-danish"
        TAGS = ["ankigarden", "pimsleur-25"]
        COLUMNS = ["source", "target", "pronunciation"]
        NOTETYPE = "Basic (and reversed) with pronunciation"
        EXPECTED = """#separator:|\n#tags:ankigarden pimsleur-25\n#columns:source|target|pronunciation\n#deck: alex-danish\n#tags column: 4\n#notetype column: 5\n\neighty|firs|[sound:firs.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nbecause|fordi|[sound:fordi.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nstore|butik|[sound:butik.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nclosed|lukket|[sound:lukket.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nopen|åben|[sound:åben.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|"""
        self.assertEqual(EXPECTED,
                         create_anki_import_string(fcs,
                                                   SEP,
                                                   TAGS_COLUMN,
                                                   NOTETYPE_COLUMN,
                                                   DECK,
                                                   TAGS,
                                                   COLUMNS,
                                                   NOTETYPE)
                         )

    def test_can_produce_anki_import_file(self):
        # NOTE this is implemented at `create_anki_import_file`
        # but the function is so simple, I did not do any tests.
        pass


if __name__ == "__main__":
    unittest.main()
