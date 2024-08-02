from typing import List, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Placeholder, Static

from hearts_textual import data


class SummaryScreen(ModalScreen):
    game: data.Game

    def __init__(self, game: data.Game):
        super().__init__()

        self.game = game

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        header = [player.name for player in self.game.players]
        header.insert(0, "Round")
        table.add_columns(*header)

        rows = []
        for round_index in range(0, self.game.round - 1):
            round_scores = [player.scores[round_index] for player in self.game.players]
            round_scores.insert(0, round_index + 1)
            rows.append(round_scores)

        table.add_rows(rows)
