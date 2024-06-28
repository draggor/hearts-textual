from textual import on
from textual.app import ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Placeholder, Static

from hearts_textual import data
from tui.base_screen import BaseScreen


demo_game = data.Game.from_dict(
    {
        "round": 1,
        "turn": 1,
        "started": True,
        "ended": False,
        "hearts_broken": False,
        "deck": [],
        "lead_player": 0,
        "players": [
            {
                "name": "Homer",
                "connected": True,
                "hand": [
                    {"suit": "C", "value": "2"},
                    {"suit": "C", "value": "6"},
                    {"suit": "C", "value": "T"},
                    {"suit": "C", "value": "A"},
                    {"suit": "D", "value": "5"},
                    {"suit": "D", "value": "9"},
                    {"suit": "D", "value": "K"},
                    {"suit": "S", "value": "4"},
                    {"suit": "S", "value": "8"},
                    {"suit": "S", "value": "Q"},
                    {"suit": "H", "value": "3"},
                    {"suit": "H", "value": "7"},
                    {"suit": "H", "value": "J"},
                ],
                "play": None,
                "pile": [],
                "scores": [],
            },
            {
                "name": "Goose",
                "connected": True,
                "hand": [
                    {"suit": "C", "value": "3"},
                    {"suit": "C", "value": "7"},
                    {"suit": "C", "value": "J"},
                    {"suit": "D", "value": "2"},
                    {"suit": "D", "value": "6"},
                    {"suit": "D", "value": "T"},
                    {"suit": "D", "value": "A"},
                    {"suit": "S", "value": "5"},
                    {"suit": "S", "value": "9"},
                    {"suit": "S", "value": "K"},
                    {"suit": "H", "value": "4"},
                    {"suit": "H", "value": "8"},
                    {"suit": "H", "value": "Q"},
                ],
                "play": None,
                "pile": [],
                "scores": [],
            },
            {
                "name": "Penguin",
                "connected": True,
                "hand": [
                    {"suit": "C", "value": "4"},
                    {"suit": "C", "value": "8"},
                    {"suit": "C", "value": "Q"},
                    {"suit": "D", "value": "3"},
                    {"suit": "D", "value": "7"},
                    {"suit": "D", "value": "J"},
                    {"suit": "S", "value": "2"},
                    {"suit": "S", "value": "6"},
                    {"suit": "S", "value": "T"},
                    {"suit": "S", "value": "A"},
                    {"suit": "H", "value": "5"},
                    {"suit": "H", "value": "9"},
                    {"suit": "H", "value": "K"},
                ],
                "play": None,
                "pile": [],
                "scores": [],
            },
            {
                "name": "Menace",
                "connected": True,
                "hand": [
                    {"suit": "C", "value": "5"},
                    {"suit": "C", "value": "9"},
                    {"suit": "C", "value": "K"},
                    {"suit": "D", "value": "4"},
                    {"suit": "D", "value": "8"},
                    {"suit": "D", "value": "Q"},
                    {"suit": "S", "value": "3"},
                    {"suit": "S", "value": "7"},
                    {"suit": "S", "value": "J"},
                    {"suit": "H", "value": "2"},
                    {"suit": "H", "value": "6"},
                    {"suit": "H", "value": "T"},
                    {"suit": "H", "value": "A"},
                ],
                "play": None,
                "pile": [],
                "scores": [],
            },
        ],
        "turn_order": [0, 1, 2, 3],
        "played_cards": [],
        "summary": {},
    }
)


class Header(Placeholder):
    pass


class Footer(Static):
    pass


class PlayCard(Container):

    card = reactive(None, recompose=True)

    def __init__(self, card: data.Card, *, id=""):
        super().__init__()

        self.card = card

    def compose(self) -> ComposeResult:
        if self.card is not None:
            yield Card(self.card, id=repr(self.card))


class PlayArea(Container):

    p1card = reactive(PlayCard(None, id="p1card"))
    p2card = reactive(PlayCard(None, id="p2card"))
    p3card = reactive(PlayCard(None, id="p3card"))
    p4card = reactive(PlayCard(None, id="p4card"))

    def compose(self) -> ComposeResult:
        # Docks for player names
        yield Static(demo_game.players[1].name, id="P2")
        yield Static(demo_game.players[3].name, id="P4")
        yield Static(demo_game.players[0].name, id="P1")
        yield Static(demo_game.players[2].name, id="P3")

        # Grid
        # Top Left
        yield Container(id="blank1")

        # Top Middle
        yield self.p2card

        # Top Right
        yield Container(id="blank2")

        # Middle Left
        yield self.p1card

        # Center
        yield Container(id="blank3")

        # Middle Right
        yield self.p3card

        # Bottom Left
        yield Container(id="blank4")

        # Bottom Middle
        yield self.p4card

        # Bottom Right
        yield Container(id="blank5")

    def play_card(self, card: data.Card) -> None:
        self.p4card.card = card
        # self.p4card = PlayCard(card_str, id=card_str)


class Card(Button):

    selected = reactive(False)

    def __init__(self, card: data.Card, *, in_hand: bool = False, id: str = ""):
        super().__init__()

        self.card = card

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
        def __init__(self, card: data.Card) -> None:
            self.card = card
            super().__init__()

    def __init__(self, cards: list[data.Card], *, id: str = ""):
        super().__init__()

        self.cards = [Card(card, in_hand=True, id=repr(card)) for card in cards]
        self.cards.sort(key=lambda card: card.card)

    def compose(self) -> ComposeResult:
        yield Footer(id="Footer")
        for card in self.cards:
            yield card

    # If this comes after the below handler, it gets triggered. I do not understand
    # why that is: at the time of button press it won't have the hand_selected class
    @on(Card.Pressed, ".hand_selected")
    def remove_card(self, event: Button.Pressed) -> None:
        card = event.button.card
        player = demo_game.players[0]
        game_or_error = demo_game.play_card(card, player)

        if isinstance(game_or_error, str):
            self.query_one("#Footer").update(game_or_error)
        else:
            self.post_message(self.PlayCardMessage(game_or_error.players[0].play))

            event.button.remove()
            self.cards.remove(event.button)

    # Maybe individual cards should have the selected handler, and post a message
    # about it being done so the parent can unselect? This is doing both atm.
    @on(Card.Pressed, ".hand_card")
    def toggle_selected(self, event: Button.Pressed) -> None:
        event.button.selected = not event.button.selected

        for card in self.cards:
            if card is not event.button:
                card.selected = False


class GameScreen(Screen):

    hand = demo_game.players[0].hand

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with BaseScreen():
            # Without nested container, Hand docks to bottom over footer in BaseScreen
            with Container():
                yield Hand(self.hand, id="Hand")
                yield PlayArea(id="PlayArea")

    @on(Hand.PlayCardMessage)
    def handle_play_card(self, message: Hand.PlayCardMessage) -> None:
        self.query_one("#PlayArea").play_card(message.card)
