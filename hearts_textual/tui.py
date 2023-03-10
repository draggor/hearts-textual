#!/usr/bin/env python


import json
import asyncio
from rich.json import JSON
import websockets
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static, Input
from textual import events

from hearts_textual.client import client
from hearts_textual.data import Game


with open("tests/game_state.json") as f:
    game_json_str = f.read()
    game = Game.from_json(game_json_str)


class Card(Button):
    pass


class Blank(Static):
    pass


class Hand(Static):
    def compose(self) -> ComposeResult:
        for card in game.players[0].hand:
            yield Card(str(card))


class PlayArea(Static):
    left = "1"
    top = "2"
    right = "3"
    bottom = "4"

    def compose(self) -> ComposeResult:
        yield Blank("")
        yield Card(self.top)
        yield Blank("")
        yield Card(self.left)
        yield Blank("")
        yield Card(self.right)
        yield Blank("")
        yield Card(self.bottom)
        yield Blank("")


class Name(Widget):
    """Generates a greeting."""

    who = reactive("name")

    def render(self) -> str:
        return f"Name: {self.who}!"


class HeartsTUI(App):
    CSS_PATH = "tui.css"
    client_running = False
    websocket = None
    websocket_task = None

    def compose(self) -> ComposeResult:
        yield Name()
        yield Input(placeholder="Your Name", id="name_input")
        yield PlayArea()
        yield Hand()
        yield Static("Stuff", id="debug_window")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            name = message.value.strip()
            if len(name) > 0:
                self.websocket_task = asyncio.create_task(client(self, name))
                self.client_running = True

                self.setup_ui(name)

                self.handle_server_response('{"message": "Connecting..."}')

    def handle_server_response(self, response) -> None:
        self.query_one("#debug_window", Static).update(JSON(response))

    def setup_ui(self, name) -> None:
        self.query_one(Name).who = name
        self.query_one("#name_input").display = False
        self.query_one(PlayArea).display = True
        self.query_one(Hand).display = True


if __name__ == "__main__":
    app = HeartsTUI()
    app.run()
