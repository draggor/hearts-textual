#!/usr/bin/env python


import websockets
from textual.app import App, ComposeResult
from textual.widgets import Welcome, Static
from textual import events


class Card(Static):
    pass


class HeartsTUI(App):
    def on_key(self) -> None:
        self.mount(Welcome())

    def on_button_pressed(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = HeartsTUI()
    app.run()
