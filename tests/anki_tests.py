import unittest
# from sound_api import (
        # download_foreign_audio
        # )
from db.objects import Flashcard
from os.path import exists
from os import remove
from const import LANG_MAP
from apis.anki_database import (
        parse_lute_term_output,
        create_flashcard_from_lute_line
        # retrieve_all_flashcards_from_database,
        # create_anki_import_string,
        # create_flashcard_from_prompt_line,
        # import_prompts_from_text_file_to_database
        )


TEST_FILES_DIR = "tests/test-files/"

class TestLuteCSVFlashcardCreation(unittest.TestCase):

    line = "høj,,high / tall,Danish,vocabulary,2024-08-21 23:00:13,1,,"
    def test_can_parse_single_line_of_prompt(self):
        EXPECTED = {
                'term': 'høj',
                'parent': '',
                'translation': 'high / tall',
                'language': 'Danish',
                'tags': 'vocabulary',
                'added': '2024-08-21 23:00:13',
                'status': '1',
                'link_status': '',
                'pronunciation': ''
                }
        self.assertEqual(EXPECTED, parse_lute_term_output(self.line))


    def test_can_create_flashcard_from_prompt_line(self):
        lute_line_dict = parse_lute_term_output(self.line)
        fc = create_flashcard_from_lute_line(lute_line_dict)
        self.assertTrue(
            fc.target == "høj" and
            fc.target_lang == "Danish" and
            fc.source_lang == "English" and
            fc.source == "high / tall" and
            fc.tags == "vocabulary"
                        )

    # def test_can_parse_prompt_file_and_create_flashcards(self):
        # prompts_filepath = TEST_FILES_DIR + "test-last-prompts#.txt"
        # import_prompts_from_text_file_to_database(prompts_filepath,
                                                  # self.session,
                                                  # "Danish",
                                                  # "English"
                                                  # )
        # fcs = retrieve_all_flashcards_from_database(self.session)
        # self.assertEqual(len(fcs), 3)


# class TestAnkiImportFileCreation(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
        # # Setup test database
        # cls.engine = create_engine('sqlite:///./tests/test-ankigarden.db')
        # Base.metadata.create_all(cls.engine)
        # # NOTE what?
        # cls.Session = sessionmaker(bind=cls.engine)
        # cls.session = cls.Session()

    # @classmethod
    # def tearDownClass(cls):
        # # Teardown test database
        # cls.session.close()
        # cls.engine.dispose()

    # def test_can_load_all_flashcards(self):
        # fcs = retrieve_all_flashcards_from_database(self.session)
        # self.assertEqual(len(fcs), 5)

    # def test_can_produce_anki_import_string(self):
        # # NOTE I seem to have lost the database at some point.
        # # must recreate it at some point
        # fcs = retrieve_all_flashcards_from_database(self.session)
        # self.maxDiff = None
        # SEP = "|"
        # TAGS_COLUMN = 4
        # NOTETYPE_COLUMN = 5
        # DECK = "alex-danish"
        # TAGS = ["ankigarden", "pimsleur-25"]
        # COLUMNS = ["source", "target", "pronunciation"]
        # NOTETYPE = "Basic (and reversed) with pronunciation"
        # EXPECTED = """#separator:|\n#tags:ankigarden pimsleur-25\n#columns:source|target|pronunciation\n#deck: alex-danish\n#tags column: 4\n#notetype column: 5\n\neighty|firs|[sound:firs.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nbecause|fordi|[sound:fordi.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nstore|butik|[sound:butik.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nclosed|lukket|[sound:lukket.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nopen|åben|[sound:åben.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|"""
        # self.assertEqual(EXPECTED,
                         # create_anki_import_string(fcs,
                                                   # SEP,
                                                   # TAGS_COLUMN,
                                                   # NOTETYPE_COLUMN,
                                                   # DECK,
                                                   # TAGS,
                                                   # COLUMNS,
                                                   # NOTETYPE)
                         # )

    # def test_can_produce_anki_import_file(self):
        # # NOTE this is implemented at `create_anki_import_file`
        # # but the function is so simple, I did not do any tests.
        # pass


if __name__ == "__main__":
    unittest.main()
