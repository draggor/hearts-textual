from collections import deque
from typing import List

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Placeholder, Static

from hearts_textual import data
from tui.base_screen import BaseScreen
from tui.messages import CommandMessage, ToasterMessage, UpdateMessage


class Header(Placeholder):
    pass


class Footer(Static):
    pass


class PlayCard(Container):

    card = reactive(None, recompose=True)

    def __init__(self, card: data.Card = None, *, id=""):
        super().__init__(id=id)

        self.card = card

    def compose(self) -> ComposeResult:
        if self.card is not None:
            yield Card(self.card, id=repr(self.card))


class PlayArea(Container):

    # p1card = reactive(None, recompose=True)
    # p2card = reactive(None, recompose=True)
    # p3card = reactive(None, recompose=True)
    # p4card = reactive(None, recompose=True)
    p1name = reactive("")
    p2name = reactive("")
    p3name = reactive("")
    p4name = reactive("")
    game: data.Game = reactive(None, recompose=True)
    translation: [0, 1, 2, 3]
    card_slots = ["p1card", "p2card", "p3card", "p4card"]

    def __init__(self, game: data.Game, translation: List[int]) -> None:
        super().__init__()
        self.game = game
        self.translation = translation

    async def watch_game(self, game) -> None:
        if game is not None:
            # Perform the rotation of players and card slots
            # TODO: something is wrong in player list and turn order in Game class
            for order, card in zip(game.turn_order, game.played_cards):
                pcard = self.card_slots[self.translation[order]]
                self.query_one(f"#{pcard}").card = card

            names = [player.name for player in self.game.players]
            # for pname, name in zip(["P1", "P2", "P3", "P4"], names):
            for pname, t in zip(["P1", "P2", "P3", "P4"], self.translation):
                name = names[t]
                self.query_one(f"#{pname}").update(name)

    def compose(self) -> ComposeResult:
        # Docks for player names
        yield Static(self.p2name, id="P2")
        yield Static(self.p4name, id="P4")
        yield Static(self.p1name, id="P1")
        yield Static(self.p3name, id="P3")

        # Grid
        # Top Left
        yield Container(id="blank1")

        # Top Middle
        yield PlayCard(id="p2card")

        # Top Right
        yield Container(id="blank2")

        # Middle Left
        yield PlayCard(id="p1card")

        # Center
        yield Container(id="blank3")

        # Middle Right
        yield PlayCard(id="p3card")

        # Bottom Left
        yield Container(id="blank4")

        # Bottom Middle
        yield PlayCard(id="p4card")

        # Bottom Right
        yield Container(id="blank5")


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

    cards = reactive([], recompose=True)
    selected = reactive(-1)
    hand = reactive(None, recompose=True)

    class PlayCardMessage(Message):
        def __init__(self, card: data.Card) -> None:
            self.card = card
            super().__init__()

    def __init__(self, hand: List[Card], *, id: str = ""):
        super().__init__()

        self.hand = hand

        if hand is not None:
            self.cards = [Card(card, in_hand=True, id=repr(card)) for card in hand]
            self.cards.sort(key=lambda card: card.card)

    def compose(self) -> ComposeResult:
        yield Footer(id="Footer")
        for card in self.cards:
            yield card

    # If this comes after the below handler, it gets triggered. I do not understand
    # why that is: at the time of button press it won't have the hand_selected class
    @on(Card.Pressed, ".hand_selected")
    def play_card(self, event: Button.Pressed) -> None:
        card = event.button.card.to_dict()

        self.post_message(CommandMessage(command="play_card", args={"card": card}))

    # Maybe individual cards should have the selected handler, and post a message
    # about it being done so the parent can unselect? This is doing both atm.
    @on(Card.Pressed, ".hand_card")
    def toggle_selected(self, event: Button.Pressed) -> None:
        event.button.selected = not event.button.selected

        for card in self.cards:
            if card is not event.button:
                card.selected = False


class GameScreen(Screen):

    # hand = demo_game.players[0].hand
    game: data.Game = reactive(None, recompose=True)
    hand: List[Card] = None
    app: App = None
    translation = [0, 1, 2, 3]

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def compose(self) -> ComposeResult:
        with BaseScreen():
            # Without nested container, Hand docks to bottom over footer in BaseScreen
            with Container():
                yield Hand(self.hand)
                yield PlayArea(self.game, self.translation)

    @on(UpdateMessage)
    async def handle_game_update(self, message: UpdateMessage) -> None:
        self.game = message.game
        if self.game is not None:
            player = self.game.get_player_by_name(self.app.name)

            # Make sure the YOU player is above your hand
            index = self.game.players.index(player)
            d = deque(self.translation)
            d.rotate(3 - index)
            self.translation = list(d)

            self.hand = player.hand
