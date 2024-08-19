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
from anki_routine import (
        create_anki_import_string
        )


class TestDatabaseHandling(unittest.TestCase):

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


class TestAnkiImportFileCreation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup test database
        cls.engine = create_engine('sqlite:///test-ankigarden.db')
        Base.metadata.create_all(cls.engine)
        # NOTE what?
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

    @classmethod
    def tearDownClass(cls):
        # Teardown test database
        cls.session.close()
        cls.engine.dispose()

    def test_can_produce_anki_import_string(self):
        SEP = "|"
        TAGS_COLUMN = 4
        NOTETYPE_COLUMN = 5
        DECK = "alex-danish"
        TAGS = ["ankigarden", "pimsleur-25"]
        COLUMNS = ["source", "target", "pronunciation"]
        NOTETYPE = "Basic (and reversed) with pronunciation"
        fcs = self.session.query(Flashcard).all()
        EXPECTED = """#separator:|\n#tags:ankigarden pimsleur-25\n#columns:source|target|pronunciation\n#deck: alex-danish\n#tags column: 4\n#notetype column: 5\n\neighty|firs|[sound:firs.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nbecause|fordi|[sound:fordi.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nStore|butik|[sound:butik.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nclosed|lukket|[sound:lukket.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|\nopen|åben|[sound:åben.mp3]|ankigarden pimsleur-25|Basic (and reversed) with pronunciation|"""
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
        SEP = "|"
        TAGS_COLUMN = 4
        NOTETYPE_COLUMN = 5
        DECK = "alex-danish"
        TAGS = ["ankigarden", "pimsleur-25"]
        COLUMNS = ["source", "target", "pronunciation"]
        NOTETYPE = "Basic (and reversed) with pronunciation"
        fcs = self.session.query(Flashcard).all()

if __name__ == "__main__":
    unittest.main(failfast=True)
