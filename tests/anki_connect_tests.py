import unittest
from objects import Flashcard
from typing import Tuple
from logger import logger
from pprint import pprint as pp
from anki_database import (
        send_request_to_anki,
        create_anki_dict_from_flashcard
        )


class TestAnkiConnectInterface(unittest.TestCase):

    def setUp(self):
        self.fc1 = Flashcard( 
                target = 'hvor længe tror du, der er åbent?',
                target_lang = 'Danish',
                source = 'how long do you think it is open?',
                source_lang = 'English',
                context = 'time',
                audio_filename = 'hvor_længe_er_der_åbent?.mp3',
                content_type = None,
                notetype = 'Basic (and reversed) with pronunciation',
                target_audio_query = None,
                tags = 'ankigarden pimsleur-26',
                deck = 'alex-danish'
               )
        self.fc2 = Flashcard( 
                target = 'hvor længe er der lukket?',
                target_lang = 'Danish',
                source = 'how long is it closed?',
                source_lang = 'English',
                context = 'time',
                audio_filename = 'hvor_længe_er_der_lukket?.mp3',
                content_type = None,
                notetype = 'Basic (and reversed) with pronunciation',
                target_audio_query = None,
                tags = 'ankigarden pimsleur-26',
                deck = 'alex-danish'
               )


    def test_can_connect_to_anki(self):
        action = "getNumCardsReviewedToday"
        self.assertTrue(send_request_to_anki(action) is not False)


    def test_can_convert_Flashcard_into_json_query(self):
        fc_dict = create_anki_dict_from_flashcard(self.fc1)
        EXPECTED = {'deckName': 'alex-danish',
                    'modelName': 'Basic (and reversed) with pronunciation',
                    'fields': {'source': 'how long do you think it is open?',
                               'target': 'hvor længe tror du, der er åbent?',
                               'pronunciation': '[sound:hvor_længe_er_der_åbent?.mp3]'},
                    'tags': ['ankigarden',
                             'pimsleur-26']
                    }
        self.assertEqual(fc_dict, EXPECTED)


    def test_successful_query_into_adding_note(self):
        action = "canAddNotesWithErrorDetail"
        notes = list(map(lambda fc: create_anki_dict_from_flashcard(fc),
                         [self.fc1, self.fc2]))
        params = {"notes": notes}
        res = send_request_to_anki(action, params)
        self.assertTrue(all(res))


    def test_successful_adds_note(self):
        action = "addNotes"
        notes = list(map(lambda fc: create_anki_dict_from_flashcard(fc),
                         [self.fc1]))
        params = {"notes": notes}
        res = send_request_to_anki(action, params)
        self.assertTrue(all(res))
        action = "deleteNotes"
        send_request_to_anki("deleteNotes", {"notes": res})



if __name__ == "__main__":
    unittest.main(failfast=True)
