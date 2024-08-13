import unittest
from sound_api import (
        request_sound_from_api,
        retrieve_sound_from_api,
        saves_audio_file
        )
from os.path import (
        exists
        )
from os import (
        remove
        )

class TestSendPOSTRequestToCreateSound(unittest.TestCase):

    # sends a good request;
    def test_send_valid_request(self):
        """Sends a good, well formed request,
        expecting success and an ID in response"""
        language = "da-DK"
        sound = "Jeg siger interessante ting"
        success, audio_id = request_sound_from_api(language, sound)
        self.assertTrue(audio_id is not None)

    # sends an invalid request, or there was an error;
    def test_send_invalid_request(self):
        language = "SILLY"
        sound = "Jeg siger en ikke så interessant ting"
        success, audio_id = request_sound_from_api(language, sound)
        self.assertFalse(success)

class TestSendGETRequestToRetrieveSound(unittest.TestCase):

    def test_send_valid_audio_id(self):
        """Sends a good, well formed request,
        expecting success and an audio file URL"""
        VALID_ID = "a6a76b50-596a-11ef-bbfe-19a6f1097474"
        success, audio_url = retrieve_sound_from_api(VALID_ID, 0)
        self.assertTrue(success)
        self.assertEqual(audio_url,
                         "https://files.soundoftext.com/a6a76b50-596a-11ef-bbfe-19a6f1097474.mp3")

    def test_send_invalid_audio_id(self):
        """Sends an invalid request"""
        success, audio_url = retrieve_sound_from_api("Dette er tydeligvis ikke et id", 0)
        self.assertFalse(success)

class TestSaveAudioFileFromRequest(unittest.TestCase):

    def test_save_file_from_request(self):
        """follows a link to save a file in a directory"""
        FILE_SAVE_PATH = "./test_audio.mp3"
        VALID_AUDIO_PATH = "https://files.soundoftext.com/a6a76b50-596a-11ef-bbfe-19a6f1097474.mp3"
        res = saves_audio_file(VALID_AUDIO_PATH, FILE_SAVE_PATH)
        self.assertTrue(res)
        self.assertTrue(exists(FILE_SAVE_PATH))

        # Delete the file
        remove(FILE_SAVE_PATH)

        # Verify the file no longer exists
        self.assertFalse(exists(FILE_SAVE_PATH))



if __name__ == "__main__":
    unittest.main(failfast=True)
