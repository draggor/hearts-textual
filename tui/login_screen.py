import asyncio

from textual import events, on
from textual.app import App, ComposeResult
from textual.messages import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from hearts_textual.client import client


class LoginScreen(Screen):

    app = None

    class LoginMessage(Message):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__()

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Your Name", id="name_input")
        yield Button("Connect", id="connect_button")
        yield Static(id="Footer")

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

            self.post_message(self.LoginMessage(f"Connecting as {name}..."))
