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

from .client import client


class Card(Static):
    pass


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
        yield Button("Q♤")
        yield Static("Stuff", id="debug_window")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            name = message.value.strip()
            if len(name) > 0:
                if not self.client_running:
                    self.query_one(Name).who = name
                    self.query_one("#name_input").display = "none"
                    self.websocket_task = asyncio.create_task(client(self, name))
                    self.client_running = True
                    self.handle_server_response({"message": "Connecting..."})

    def handle_server_response(self, response) -> None:
        self.query_one("#debug_window", Static).update(JSON(json.dumps(response)))


if __name__ == "__main__":
    app = HeartsTUI()
    app.run()
