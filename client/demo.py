from decimal import Decimal

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual import events
from textual.containers import Container, HorizontalScroll
from textual.css.query import NoMatches
from textual.reactive import reactive, var
from textual.widgets import Button, Static, Placeholder, Label

from hearts_textual import data


class Header(Placeholder):
    pass


class PlayCard(Container):

    card_str = reactive("")

    def __init__(self, card_str: str, *, id=""):
        super().__init__()

        self.card_str = card_str

    def compose(self) -> ComposeResult:
        yield Card(self.card_str)


class PlayArea(Container):
    def compose(self) -> ComposeResult:
        yield Static("Homer", id="P2")
        yield Static("Goose", id="P4")
        yield Static("Penguin", id="P1")
        yield Static("Menace", id="P3")
        yield Container(id="blank1")
        yield PlayCard("2C", id="card1")
        yield Container(id="blank2")
        yield PlayCard("5C", id="card2")
        yield Container(id="blank3")
        yield PlayCard("QC", id="card3")
        yield Container(id="blank4")
        yield PlayCard("AC", id="card4")
        yield Container(id="blank5")


class Card(Button):

    def __init__(self, card_str: str, *, id: str = ""):
        super().__init__()

        self.card = data.Card.parse(card_str)

        # TODO: red/black status should be derived from the data.Suits enum
        if self.card.suit in [data.Suits.CLUBS, data.Suits.SPADES]:
            self.add_class("black")
        if self.card.suit in [data.Suits.DIAMONDS, data.Suits.HEARTS]:
            self.add_class("red")

        self.label = str(self.card)


class Hand(HorizontalScroll):

    cards = reactive([])

    def __init__(self, cards: list[str], *, id: str = ""):
        super().__init__()

        self.cards = [Card(card_str, id=card_str) for card_str in cards]
        self.cards.sort(key=lambda card: card.card)

    def compose(self) -> ComposeResult:
        for card in self.cards:
            yield card


class GameScreen(Screen):

    hand = [
        "KH",
        "JH",
        "3H",
        "6H",
        "2H",
        "2C",
        "AC",
        "7C",
        "8S",
        "QS",
        "8D",
        "9D",
        "QD",
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Hand(self.hand, id="Hand")
        yield PlayArea(id="PlayArea")


class HeartsApp(App):
    CSS_PATH = "demo.css"

    def on_ready(self) -> None:
        self.push_screen(GameScreen())


if __name__ == "__main__":
    HeartsApp().run()
