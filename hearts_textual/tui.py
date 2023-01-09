#!/usr/bin/env python


import websockets
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static, Input
from textual import events


class Card(Static):
    pass


class Name(Widget):
    """Generates a greeting."""

    who = reactive("name")

    def render(self) -> str:
        return f"Name: {self.who}!"


class HeartsTUI(App):
    CSS_PATH = "tui.css"

    def compose(self) -> ComposeResult:
        yield Name()
        yield Input(placeholder="Your Name", id="name_input")
        yield Button("Q♤")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            name = message.value.strip()
            if len(message.value) > 0:
                self.query_one(Name).who = name
                self.query_one("#name_input").display = "none"


if __name__ == "__main__":
    app = HeartsTUI()
    app.run()
