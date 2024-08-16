import unittest
from routine import (
    get_audio_from_source_query,
    get_bulk_audio_from_textfile
        )
from sound_api import (
        normalise_file_path
        )
from os.path import (
        exists
        )
from os import (
        remove
        )

# ROUTINE TESTS

## PHASE 1 - get translation from deepL and pipe to SoT

class TestFirstStepInRoutine(unittest.TestCase):

    def test_whole_routine(self):
        """Sends a good, well formed request,
        expecting success and an ID in response"""
        query = "I would really like to learn languages efficiently."
        target = "DA"
        DEST_FILE_PATH = "./audios/"
        success, translation, audio_file_path = get_audio_from_source_query(target, query, DEST_FILE_PATH)
        self.assertTrue(success)
        # NOTE not exactly the best test; translations may vary...
        self.assertEqual(translation, "Jeg vil virkelig gerne lære sprog effektivt.")

        NORMALISED_FILENAME = normalise_file_path(translation)
        self.assertTrue(exists(DEST_FILE_PATH + NORMALISED_FILENAME))

        # Delete the file
        remove(DEST_FILE_PATH + NORMALISED_FILENAME)

        # Verify the file no longer exists
        self.assertFalse(exists(DEST_FILE_PATH + NORMALISED_FILENAME))

## PHASE 2 - get bulk content from .txt file

class TestBulkAudioGeneration(unittest.TestCase):

    def test_can_receive_various_prompts_in_file(self):
        PROMPT_FILE = "./test_prompts.txt"
        TARGET = "DA"
        DEST_FILE_PATH = "./audios/"
        get_bulk_audio_from_textfile(TARGET, PROMPT_FILE, DEST_FILE_PATH)
        self.assertTrue(exists(DEST_FILE_PATH + "det_burde_fungere_rigtig_godt.mp3"))
        self.assertTrue(exists(DEST_FILE_PATH + "det_er_en_simpel_ting.mp3"))
        self.assertTrue(exists(DEST_FILE_PATH + "her_er_en_anden_simpel_ting.mp3"))

        # Delete the files
        remove(DEST_FILE_PATH + "det_burde_fungere_rigtig_godt.mp3")
        remove(DEST_FILE_PATH + "det_er_en_simpel_ting.mp3")
        remove(DEST_FILE_PATH + "her_er_en_anden_simpel_ting.mp3")

        # # Verify the file no longer exists
        self.assertFalse(exists(DEST_FILE_PATH + "det_burde_fungere_rigtig_godt.mp3"))
        self.assertFalse(exists(DEST_FILE_PATH + "det_er_en_simpel_ting.mp3"))
        self.assertFalse(exists(DEST_FILE_PATH + "her_er_en_anden_simpel_ting.mp3"))
        

if __name__ == "__main__":
    unittest.main(failfast=True)
