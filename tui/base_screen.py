from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Static


class BaseScreen(Container):

    def compose(self) -> ComposeResult:
        yield Static("Welcome to Hearts Textual!", id="Header")
        yield Static(id="Footer")
