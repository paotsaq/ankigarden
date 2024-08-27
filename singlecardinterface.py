from textual.app import App, ComposeResult, RenderResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
        Input,
        Placeholder,
        Button,
        ListItem,
        ListView,
        Header,
        Footer,
        Static,
        RadioSet,
        RadioButton
        )
from textual.reactive import reactive
from textual.message import Message
from objects import Flashcard
from const import (
        DATABASE_FILE_PATH,
        EMOJI_FLAG,
        USE_CONFIGS,
        AUDIOS_SOURCE_DIR,
        )
from anki_database import (
        create_connection_to_database,
        close_connection_to_database,
        create_anki_dict_from_flashcard,
        send_request_to_anki,
        move_audio_files_to_anki_mediadir
        )
from logger import logger
from time import sleep
from playsound import playsound
from os.path import exists

class EscapableInput(Input):
    """just a class that communicates on esc key press"""

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
        ("c", "focus_elem('context')", "(c)ontext"),
        ("t", "focus_elem('target')", "(t)arget"),
        ("s", "focus_elem('source')", "(s)ource"),
        ("g", "focus_elem('tags')", "ta(g)s"),
        ("a", "focus_elem('audio')", "(a)udio"),
        ("p", "focus_elem('play')", "(p)lay "),
        ("f", "focus_elem('save')", "save (f)c"),
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
                    EscapableInput(placeholder="tags",
                          classes="flashcardLineInput", id="tags_input"),
                    EscapableInput(value=self.target,
                                   placeholder=f"target {EMOJI_FLAG[self.fc.target_lang]}",
                                   classes="flashcardLineInput", id="target_input"),
                    EscapableInput(value=self.source,
                                   placeholder=f"source {EMOJI_FLAG[self.fc.source_lang]}",
                                   classes="flashcardLineInput", id="source_input"),
                    Horizontal(
                        EscapableInput(value=self.target, placeholder="audio query",
                              classes="flashcardAudioInput", id="audio_input"),
                        Button(label="📡", disabled=True,
                               classes="flashcardLineButton", id="audio_button")),
                    Button(label="create flashcard",
                           classes="flashcardButton", id="flashcard_button")),
                classes="flashcardColumn")

        
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """signals request for query to parent widget"""
        self.post_message(self.Submitted(self.fc, event.input.id))
        if event.input.id in ['target_input', 'audio_input']:
            DURATION = 0.3
            self.styles.animate("opacity", value=0.0, duration=DURATION)
            self.styles.animate("opacity", value=1.0, duration=DURATION, delay=DURATION)


    def on_button_pressed(self, event: Button.Pressed) -> None:  
        if event.button.id == "audio_button":
            if (self.fc.audio_filename != "" and
                exists(AUDIOS_SOURCE_DIR + self.fc.audio_filename)):
                    playsound(AUDIOS_SOURCE_DIR + self.fc.audio_filename)
        elif event.button.id == "flashcard_button":
            self.post_message(self.Submitted(self.fc,
                                             event.button.id))
            
    def action_focus_elem(self, field: str) -> None:
        if field == "play":
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

    fc = reactive(None, recompose=True)

    BINDINGS = [
        ("n", "new_flashcard()", "(n)ew fc"),
    ]

    def __init__(self, current_config_key: str) -> None:
        super().__init__()
        self.current_config = USE_CONFIGS[current_config_key]
        self.fc = self.get_new_flashcard()

    def get_new_flashcard(self):
        return Flashcard(source_lang=self.current_config['source_lang'],
                         target_lang=self.current_config['target_lang'],
                         deck=self.current_config['deck'],
                         notetype=self.current_config['notetype']
                         )


    def compose(self) -> ComposeResult:
        yield FlashcardColumn(self.fc)

    def action_new_flashcard(self) -> None:
        self.fc = self.get_new_flashcard()
        self.focus()

    def on_flashcard_column_submitted(self, message):
        self.fc = message.fc
        # translation was requested
        if ((message.action == "target_input" and
             self.query_one("#target_input").value != "") or
            (message.action == "source_input" and
             self.query_one("#source_input").value != "")):
            # context is always taken into account
            self.fc.context = self.query_one("#context_input").value
            # update tags field, too
            self.fc.tags = self.query_one("#tags_input").value
            # if source was input, then invert translation (get target),
            # in any case, produce translation and update local widget variables
            if message.action == "source_input":
                self.fc.source = self.query_one("#source_input").value
                self.fc.get_translation(invert=True)
                self.query_one("#target_input").value = self.fc.target
            else:
                self.fc.target = self.query_one("#target_input").value
                self.fc.get_translation()
                self.query_one("#source_input").value = self.fc.source
            # update audio prompt field when it is empty
            # or NOTE target is very different? This needs to be rethought
            if (self.query_one("#audio_input").value == "" or
                self.fc.target not in self.query_one("#audio_input").value.split()):
                # NOTE this is a bit of a hack, but it saves some time,
                # and it should be updated in the future
                if 'noun' in self.fc.tags.split():
                    double_prompt = ",".join(2*[self.fc.target])
                    self.query_one("#audio_input").value = double_prompt
                else:
                    self.fc.target_audio_query = self.fc.target
                    self.query_one("#audio_input").value = self.fc.target
        # retrieves audio file
        elif ((message.action == "audio_input" and
             self.query_one("#audio_input").value != "")):
            # reupdates `target_audio_query` in case it was manually changed
            self.fc.target_audio_query = self.query_one("#audio_input").value
            self.fc.get_audio_file_path()
            self.query_one("#audio_button").label = f"📡"
            self.query_one("#audio_button").disabled = False
            self.fc.get_audio_file()
            self.query_one("#audio_button").label = "🗣️"
        # saves flashcard to database;
        # NOTE we might consider the possibility of saving incomplete flashcards
        # (for example, in internet deprived environments it might still be useful
        # to signal which flashcards should be made)
        elif message.action == "flashcard_button":
            if (self.fc.target == "" or self.fc.source == ""):
                self.query_one("#flashcard_button").variant = "warning"
                self.query_one("#flashcard_button").label = "missing fields!"
            else:
                fc_dict = create_anki_dict_from_flashcard(self.fc)
                params={"notes": [fc_dict]}
                test_can_add = send_request_to_anki("canAddNotesWithErrorDetail",
                                                    params)
                if test_can_add[0]:
                    send_request_to_anki("addNotes", params)
                    move_audio_files_to_anki_mediadir([self.fc])
                else:
                    logger.error(test_can_add)
        self.query_one(FlashcardColumn).focus()


class SettingsPanel(Screen):
    """A settings to panel to select languages"""

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self) -> None:
        super().__init__()
        # TODO this is not working like this
        self.options_set = RadioSet([RadioButton(option)
                                     for option in USE_CONFIGS])

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.options_set
        yield Footer()


class FlashcardCreator(App):
    CSS_PATH = "interface-column.tcss"

    current_config = reactive("english-to-danish")

    SCREENS = {"settings": SettingsPanel}
    BINDINGS = [
        ("d", "toggle_dark_mode()", "toggle (d)ark mode"),
        ("z", "push_screen('settings')", "settings")
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield SingleFlashcardPanel(self.current_config)
        yield Footer()

    def action_toggle_dark_mode(self) -> None:
        self.dark = not(self.dark)

if __name__ == "__main__":
    app = FlashcardCreator()
    app.run()
