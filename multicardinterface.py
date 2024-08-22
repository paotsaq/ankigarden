from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Input, Placeholder, Button, ListItem, ListView
from textual.reactive import reactive
from textual.message import Message
from objects import Flashcard
from const import DATABASE_FILE_PATH
from anki_database import (
        create_connection_to_database,
        close_connection_to_database
        )
from logger import logger
from time import sleep


class FlashcardRow(Widget):
    """handles each row, representing a single flashcard;
       any changes will trigger a recompose of the element."""

    source = reactive("", recompose=True)
    target = reactive("", recompose=True)
    audio_query = reactive("", recompose=True)
    tags = reactive("", recompose=True)

    class Submitted(Message):

        def __init__(self, fc, id) -> None:
            super().__init__()
            self.fc = fc
            self.id = id


    def __init__(self, id: str, fc: Flashcard) -> None:
        super().__init__()
        self.fc = fc
        self.id = id
        self.source = self.fc.source
        self.target = self.fc.target
        self.tags = self.fc.tags
        self.fc.get_audio_file_path()

    def compose(self) -> ComposeResult:
        yield Container(
                Horizontal(
                    Placeholder(variant="size", classes="flashcardLineStatus"),
                    Input(value=self.target, classes="flashcardLineInput", id="target_input"),
                    Input(value=self.source, placeholder="source", classes="flashcardLineInput", id="source_input"),
                    Input(placeholder="tags", classes="flashcardLineInput"),
                    Input(value=self.fc.audio_filename, placeholder="audio query", classes="flashcardLineInput", id="audio_input"),
                    Vertical(Button(classes="flashcardLineButton"),
                             Button(classes="flashcardLineButton"))
                    ),
                classes="flashcardRow")

        
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """requests translation and sends
        updated flashcard to parent widget"""
        if event.input.id == "target_input":
            self.target = event.input.value
            self.fc.target = event.input.value
            self.fc.get_source_from_target()
            self.source = self.fc.source
        if event.input.id == "source_input":
            self.fc.source = event.input.value
            self.source = self.fc.source
        DURATION = 0.3
        self.styles.animate("opacity", value=0.0, duration=DURATION)
        self.styles.animate("opacity", value=1.0, duration=DURATION, delay=DURATION)
        self.post_message(self.Submitted(self.fc, self.id))
        print(f"on widget: {self.fc}")


class FlashcardPanel(Widget):
    """Oversees creation and modification of Flashcard objects
    (which are, themselves, elements of our database)"""


    def __init__(self) -> None:
        super().__init__()
        fc1 = Flashcard(id='fc1',
                        source="",
                        source_lang="English",
                        target = "det tro jeg ikke",
                        target_lang="Danish")
        fc2 = Flashcard(id="fc2",
                        source="",
                        source_lang="English",
                        target = "det vil jeg ikke",
                        target_lang="Danish")
        self.fcs = [fc1, fc2]


    def load_flashcards_from_database(self, fc_ids: list[int]):
        session, engine = create_connection_to_database(DATABASE_FILE_PATH)
        res = session.query(Flashcard).filter(
                Flashcard.id.is_(fc_id)).all()
        close_connection_to_database(session, engine)
        return res


    def compose(self) -> ComposeResult:
        fr = list(map(lambda fc: FlashcardRow(fc=fc, id=fc.id),
                  self.fcs))
        for fcr in fr:
            yield fcr

    def on_flashcard_row_submitted(self, message):
        # look for which flashcard it corresponds to, via its id
        for fc in self.fcs:
            print(fc, fc.id, message.id)
            if fc.id == message.id:
                self.fcs.remove(fc)
                self.fcs.append(message.fc)
                print("FOUND IT!")
                break
        print(self.fcs)


class FlashcardCreator(App):
    CSS_PATH = "interface.tcss"

    def compose(self) -> ComposeResult:
        yield Placeholder(classes="batchInfo")
        yield FlashcardPanel()
        yield Placeholder(classes="batchInfo")


if __name__ == "__main__":
    app = FlashcardCreator()
    app.run()
