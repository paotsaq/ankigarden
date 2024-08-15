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

    # sends a good request;
    def test_send_valid_request(self):
        """Sends a good, well formed request,
        expecting success and an ID in response"""
        target = "DA"
        query = "This is an interesting thing"
        success, translation = request_translation_from_api(target, query)
        self.assertTrue(success)
        # NOTE not exactly the best test; translations may vary...
        self.assertEqual(translation, "Dette er en interessant ting")

    # sends an invalid request, or there was an error;
    def test_send_invalid_request(self):
        target = "SILLY"
        query = "This is an interesting thing"
        success, translation = request_translation_from_api(target, query)
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main(failfast=True)
