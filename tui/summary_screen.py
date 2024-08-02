from typing import List, Optional

from rich.text import Text

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Placeholder, Static

from hearts_textual import data
from tui.messages import BasicMessage


class SummaryScreen(ModalScreen):
    game: data.Game

    def __init__(self, game: data.Game):
        super().__init__()

        self.game = game

    def compose(self) -> ComposeResult:
        with Container(id="summary"):
            with Center():
                yield DataTable()
            with Center():
                yield Button("Ok", id="summary_button")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "none"

        header = [player.name for player in self.game.players]
        header.insert(0, "Round")
        table.add_columns(*header)

        rows = []
        for round_index in range(0, self.game.round - 1):
            round_scores = [
                Text(str(player.scores[round_index]), justify="right")
                for player in self.game.players
            ]
            round_scores.insert(0, Text(str(round_index + 1), justify="right"))
            rows.append(round_scores)

        totals = [
            Text(str(sum(player.scores)), justify="right")
            for player in self.game.players
        ]
        totals.insert(0, "Total:")
        rows.append(totals)

        table.add_rows(rows)

        self.post_message(BasicMessage("focus('summary_button')"))

    @on(Button.Pressed, "#summary_button")
    async def close_summary_screen(self) -> None:
        self.post_message(BasicMessage("pop_screen()"))
