import asyncio

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Static

from hearts_textual.client import client
from tui.base_screen import BaseScreen
from tui.messages import BasicMessage, CommandMessage, ToasterMessage


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
                yield Button("Start Game", id="start_button")

    # def on_mount(self) -> None:
    #    self.query_one("#start_button").disabled = True

    @on(Button.Pressed, "#connect_button")
    def handle_submit_button(self) -> None:
        name = self.query_one("#name_input", Input).value
        if name:
            self.handle_submit(name)

    @on(Input.Submitted, "#name_input")
    def handle_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            self.handle_submit(message.value)

    @on(Button.Pressed, "#start_button")
    async def handle_start_button(self) -> None:
        # TODO: need a better/decoupled way of sending this
        # TODO: button state, should be disabled before connect, enabled on connect,
        #       disabled on send, screen pop on game start
        self.post_message(CommandMessage({"command": "new_game", "args": {}}))
        self.post_message(CommandMessage({"command": "next_round", "args": {}}))
        self.post_message(CommandMessage({"command": "next_turn", "args": {}}))

    def handle_submit(self, name: str) -> None:
        name = name.strip()
        if len(name) > 0:
            self.query_one("#connect_button", Button).disabled = True
            self.query_one("#name_input", Input).disabled = True

            self.app.websocket_task = asyncio.create_task(client(self.app, name))

            self.post_message(BasicMessage(f"toaster('Connecting as {name}...')"))
