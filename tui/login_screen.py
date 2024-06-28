import asyncio

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Static

from hearts_textual.client import client
from tui.base_screen import BaseScreen
from tui.messages import BasicMessage


class LoginScreen(Screen):

    app = None

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def compose(self) -> ComposeResult:
        with BaseScreen():
            with Center():
                yield Input(placeholder="Your Name", id="name_input")
            with Center():
                yield Button("Connect", id="connect_button")

    @on(Button.Pressed, "#connect_button")
    def handle_submit_button(self) -> None:
        name = self.query_one("#name_input", Input).value
        if name:
            self.handle_submit(name)

    @on(Input.Submitted, "#name_input")
    def handle_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            self.handle_submit(message.value)

    def handle_submit(self, name: str) -> None:
        name = name.strip()
        if len(name) > 0:
            self.query_one("#connect_button", Button).disabled = True
            self.query_one("#name_input", Input).disabled = True

            self.websocket_task = asyncio.create_task(client(self.app, name))

            self.post_message(BasicMessage(f"Connecting as {name}..."))
