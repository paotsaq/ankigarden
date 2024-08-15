import unittest
from deepl_api import (
    request_translation_from_api
        )
from os.path import (
        exists
        )
from os import (
        remove
        )

# DEEPL API

## PHASE 1 - interact with deepL API

class TestSendPOSTRequestToRetrieveTranslation(unittest.TestCase):

    # sends a good request with source language;
    def test_send_valid_request(self):
        """Sends a good, well formed request,
        expecting success and an ID in response"""
        target = "DA"
        source = "EN"
        query = "This is an interesting thing"
        success, translation, _ = request_translation_from_api(target, query, source)
        self.assertTrue(success)
        # NOTE not exactly the best test; translations may vary...
        self.assertEqual(translation, "Dette er en interessant ting")

    # sends an invalid request, or there was an error;
    def test_send_invalid_request(self):
        target = "SILLY"
        query = "This is an interesting thing"
        success, translation, _ = request_translation_from_api(target, query)
        self.assertFalse(success)

    # sends a good request, but without target language;
    def test_send_valid_request_without_target(self):
        """Sends a good, well formed request,
        expecting success and an ID in response"""
        target = "DA"
        query = "This is an interesting thing"
        success, translation, source = request_translation_from_api(target, query)
        self.assertTrue(success)
        self.assertEqual(source, "EN")
        # NOTE not exactly the best test; translations may vary...
        self.assertEqual(translation, "Dette er en interessant ting")


if __name__ == "__main__":
    unittest.main(failfast=True)
