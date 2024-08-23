from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
        Input,
        Placeholder,
        Button,
        ListItem,
        ListView,
        Footer
        )
from textual.reactive import reactive
from textual.message import Message
from objects import Flashcard
from const import (
        DATABASE_FILE_PATH,
        EMOJI_FLAG
        )
from anki_database import (
        create_connection_to_database,
        close_connection_to_database,
        )
from logger import logger
from time import sleep
from playsound import playsound
from os.path import exists

class EscapableInput(Input):

    class EscapeRequest(Message):
        """single purpose class to bubble
        request to the parent widget to regain focus"""

        def __init__(self) -> None:
            super().__init__()

    def key_escape(self) -> None:
        self.post_message(self.EscapeRequest())


class FlashcardColumn(Widget):
    """handles the information of a single flashcard;
       any changes will trigger a recompose of the element."""

    can_focus = True
    source = reactive("", recompose=True)
    target = reactive("", recompose=True)
    context = reactive("")
    audio_query = reactive("", recompose=True)
    tags = reactive("", recompose=True)


    BINDINGS = [
        ("t", "focus_elem('target')", "(t)arget"),
        ("s", "focus_elem('source')", "(s)ource"),
        ("c", "focus_elem('context')", "(c)ontext"),
        ("g", "focus_elem('tags')", "ta(g)s"),
        ("a", "focus_elem('audio')", "(a)udio prompt"),
        ("r", "focus_elem('retrieve')", "(r)etrieve audio"),
        ("p", "focus_elem('play')", "(p)lay audio"),
        ("f", "focus_elem('save')", "save (f)lashcard"),
    ]

    class Submitted(Message):
        """single purpose class to bubble
        contents to the parent widget"""

        def __init__(self, fc: Flashcard, action: str) -> None:
            super().__init__()
            self.fc = fc
            self.action = action


    def __init__(self, fc: Flashcard) -> None:
        super().__init__()
        self.fc = fc
        self.source = self.fc.source
        self.target = self.fc.target
        self.tags = self.fc.tags
        self.context = self.fc.context

    def compose(self) -> ComposeResult:
        yield Container(
                Vertical(
                    EscapableInput(value=self.context, placeholder="context?",
                                   classes="flashcardLineInput", id="context_input"),
                    EscapableInput(value=self.target, placeholder=f"target {EMOJI_FLAG[self.fc.target_lang]}",
                          classes="flashcardLineInput", id="target_input"),
                    EscapableInput(placeholder="tags",
                          classes="flashcardLineInput", id="tags_input"),
                    EscapableInput(value=self.source, placeholder=f"source {EMOJI_FLAG[self.fc.source_lang]}",
                          classes="flashcardLineInput", id="source_input"),
                    Horizontal(
                        EscapableInput(value=self.target, placeholder="audio query",
                              classes="flashcardAudioInput", id="audio_input"),
                        Button(label="download audio",
                               classes="flashcardLineButton", id="audio_button")),
                    Button(label="create flashcard",
                           classes="flashcardButton", id="flashcard_button")),
                classes="flashcardRow")

        
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """signals request for query to parent widget"""
        DURATION = 0.3
        self.styles.animate("opacity", value=0.0, duration=DURATION)
        self.styles.animate("opacity", value=1.0, duration=DURATION, delay=DURATION)
        self.post_message(self.Submitted(self.fc, event.input.id))
        print(f"on widget: {self.fc}\n{event}")


    def on_button_pressed(self, event: Button.Pressed) -> None:  
        if event.button.id == "audio_button":
            if (self.fc.audio_filename != "" and
                exists("./audios/" + self.fc.audio_filename)):
                    playsound("./audios/" + self.fc.audio_filename)
        elif event.button.id == "flashcard_button":
            self.post_message(self.Submitted(self.fc,
                                             event.button.id))
            
    def action_focus_elem(self, field: str) -> None:
        if field in ["retrieve", "play"]:
            self.query_one(f"#audio_button").action_press()
        elif field == "save":
            self.query_one(f"#flashcard_button").action_press()
        else:
            self.query_one(f"#{field}_input").focus()

    def on_escapable_input_escape_request(self):
        self.focus()


class SingleFlashcardPanel(Widget):
    """Oversees creation and modification of a single Flashcard
    (which are, themselves, elements of our database)"""


    def __init__(self) -> None:
        super().__init__()
        self.fc = Flashcard(source="",
                            source_lang="English",
                            target = "",
                            target_lang="Danish")

    def compose(self) -> ComposeResult:
        yield FlashcardColumn(self.fc)

    def on_flashcard_column_submitted(self, message):
        self.fc = message.fc
        # translation was requested from target to source
        if ((message.action == "context_input" and
            self.query_one("#target_input").value != "") or
            (message.action == "target_input")):
            self.fc.target = self.query_one("#target_input").value
            self.fc.context = self.query_one("#context_input").value
            self.fc.get_audio_file_path()
            self.fc.get_source_from_target()
            self.query_one("#audio_button").label = f"Retrieve {self.fc.audio_filename}"
            self.query_one("#source_input").value = self.fc.source
            if self.query_one("#audio_input").value == "" :
                self.query_one("#audio_input").value = self.fc.target
        # retrieves audio file
        if ((message.action == "audio_input" and
             self.query_one("#audio_input").value != "")):
            self.fc.get_audio_file()
            self.query_one("#audio_button").label = f"Play {self.fc.audio_filename}"
        # saves flashcard to database
        if message.action == "flashcard_button":
            session, engine = create_connection_to_database(DATABASE_FILE_PATH)
            session.add(self.fc)
            session.commit()
            close_connection_to_database(session, engine)


class FlashcardCreator(App):
    CSS_PATH = "interface-column.tcss"

    def compose(self) -> ComposeResult:
        yield Placeholder(classes="batchInfo")
        yield SingleFlashcardPanel()
        yield Footer()


if __name__ == "__main__":
    app = FlashcardCreator()
    app.run()
