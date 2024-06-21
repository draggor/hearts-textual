from decimal import Decimal

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.css.query import NoMatches
from textual.messages import Message
from textual.reactive import reactive, var
from textual.screen import Screen
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

    p1card = reactive(None, recompose=True)
    p2card = reactive(None, recompose=True)
    p3card = reactive(None, recompose=True)
    p4card = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        # Docks for player names
        yield Static("Homer", id="P2")
        yield Static("Goose", id="P4")
        yield Static("Penguin", id="P1")
        yield Static("Menace", id="P3")

        # Grid
        yield Container(id="blank1")

        if self.p2card is not None:
            yield self.p1card
        else:
            yield Container(id="p2blank")

        yield Container(id="blank2")

        if self.p1card is not None:
            yield self.p1card
        else:
            yield Container(id="p1blank")

        yield Container(id="blank3")

        if self.p3card is not None:
            yield self.p3card
        else:
            yield Container(id="p3blank")

        yield Container(id="blank4")

        if self.p4card is not None:
            yield self.p4card
        else:
            yield Container(id="p4blank")

        yield Container(id="blank5")

    def play_card(self, card_str: str) -> None:
        self.p4card = PlayCard(card_str, id=card_str)


class Card(Button):

    selected = reactive(False)

    def __init__(self, card_str: str, *, in_hand: bool = False, id: str = ""):
        super().__init__()

        self.card = data.Card.parse(card_str)

        if in_hand:
            self.add_class("hand_card")

        self.add_class(self.card.suit.color())

        self.label = str(self.card)

    def watch_selected(self, selected: bool) -> None:
        if selected:
            self.add_class("hand_selected")
        else:
            self.remove_class("hand_selected")

    def play(self) -> None:
        self.remove_class("hand_selected", "hand_card")
        self.add_class("play_card")

    def remove(self) -> None:
        self.add_class("hide_card")


class Hand(HorizontalScroll):

    cards = reactive([])
    selected = reactive(-1)

    class PlayCardMessage(Message):
        def __init__(self, card_str: str) -> None:
            self.card_str = card_str
            super().__init__()

    def __init__(self, cards: list[str], *, id: str = ""):
        super().__init__()

        self.cards = [Card(card_str, in_hand=True, id=card_str) for card_str in cards]
        self.cards.sort(key=lambda card: card.card)

    def compose(self) -> ComposeResult:
        for card in self.cards:
            yield card

    # If this comes after the below handler, it gets triggered. I do not understand
    # why that is: at the time of button press it won't have the hand_selected class
    @on(Card.Pressed, ".hand_selected")
    def remove_card(self, event: Button.Pressed) -> None:
        event.button.remove()
        self.cards.remove(event.button)
        self.post_message(self.PlayCardMessage(repr(event.button.card)))
        # event.button.play()

    # Maybe individual cards should have the selected handler, and post a message
    # about it being done so the parent can unselect? This is doing both atm.
    @on(Card.Pressed, ".hand_card")
    def toggle_selected(self, event: Button.Pressed) -> None:
        event.button.selected = not event.button.selected

        for card in self.cards:
            if card is not event.button:
                card.selected = False


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

    def __init__(self):
        super().__init__()
        self.play_area = PlayArea(id="PlayArea")

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Hand(self.hand, id="Hand")
        yield self.play_area

    @on(Hand.PlayCardMessage)
    def handle_play_card(self, message: Hand.PlayCardMessage) -> None:
        self.play_area.play_card(message.card_str)


class HeartsApp(App):
    CSS_PATH = "demo.css"

    def on_ready(self) -> None:
        self.push_screen(GameScreen())


if __name__ == "__main__":
    HeartsApp().run()
