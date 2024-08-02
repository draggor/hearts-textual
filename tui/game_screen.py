from collections import deque
from typing import List, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Placeholder, Static

from hearts_textual import data
from tui.base_screen import BaseScreen
from tui.summary_screen import SummaryScreen
from tui.messages import (
    BasicMessage,
    CommandMessage,
    ToasterMessage,
    UpdateMessage,
    FooterMessage,
)


class Header(Placeholder):
    pass


class Footer(Static):
    pass


class PlayCard(Container, can_focus=False):
    card = reactive(None, recompose=True)

    def __init__(self, card: data.Card = None, *, id=""):
        super().__init__(id=id)

        self.card = card

    def compose(self) -> ComposeResult:
        if self.card is not None:
            yield Card(self.card)


class PlayArea(Container):
    game: Optional[data.Game] = reactive(None, recompose=True)
    show_summary: bool = reactive(False)
    translation: None
    card_slots = ["p1card", "p2card", "p3card", "p4card"]
    name_slots = ["P1", "P2", "P3", "P4"]

    def __init__(
        self, game: data.Game, translation: List[int], show_summary: bool
    ) -> None:
        super().__init__()
        self.translation = translation
        self.show_summary = show_summary
        self.game = game

    def _show_played_cards(self) -> None:
        if self.game.turn >= 1:
            # Perform the rotation of players and card slots
            for player, t in zip(self.game.players, self.translation):
                pcard = self.card_slots[t]
                pname = self.name_slots[t]
                self.query_one(f"#{pcard}").card = player.play
                self.query_one(f"#{pname}").update(player.name)

    def _show_summary_cards(self) -> None:
        for card_str, order in zip(
            self.game.summary["last_hand"], self.game.summary["turn_order"]
        ):
            card = data.Card.from_dict(card_str)
            pcard = self.card_slots[self.translation[order]]
            self.query_one(f"#{pcard}").card = card

        self.query_one("#next_turn_button").remove_class("hide_card")
        self.post_message(BasicMessage("focus('next_turn_button')"))

    async def watch_game(self, game) -> None:
        if game is not None:
            if self.show_summary:
                self._show_summary_cards()
            else:
                self._show_played_cards()

    async def watch_show_summary(self, show_summary: bool) -> None:
        if not show_summary and self.game is not None:
            self.query_one("#next_turn_button").add_class("hide_card")
            self._show_played_cards()

    @on(Button.Pressed, "#next_turn_button")
    async def disable_next_button(self) -> None:
        self.show_summary = False

    def compose(self) -> ComposeResult:
        # Docks for player names
        yield Static(id="P2")
        yield Static(id="P4")
        yield Static(id="P1")
        yield Static(id="P3")

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
        # yield Container(id="blank3")
        with Container(id="center"):
            yield Button("Next Turn!", id="next_turn_button", classes="hide_card")

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

    def __init__(
        self,
        card: data.Card,
        *,
        in_hand: bool = False,
    ):
        card_str = repr(card)
        super().__init__(id=f"card_{card_str}")

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
            self.cards = [Card(card, in_hand=True) for card in hand]
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
    translation = None
    show_turn_summary: bool = False
    show_round_summary: bool = False

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def compose(self) -> ComposeResult:
        with BaseScreen():
            # Without nested container, Hand docks to bottom over footer in BaseScreen
            with Container():
                yield Hand(self.hand)
                yield PlayArea(
                    self.game,
                    self.translation,
                    self.show_turn_summary,
                )

    @on(FooterMessage)
    async def footer_message(self, message: FooterMessage) -> None:
        self.query_one(Footer).update(message.message)

    def _handle_first_turn(self, game: data.Game, player: data.Player) -> None:
        # Make sure the YOU player is above your hand which is the p4
        # slot, meaning your index needs to be 3
        if game.started and game.turn == 1:
            index = game.players.index(player)
            d = deque([0, 1, 2, 3])
            d.rotate(index - 3)
            # TODO: does this need to be a list again?
            self.translation = list(d)
            names = [player.name for player in game.players]

    def _handle_next_turn(self, game: data.Game) -> None:
        if self.game is not None and self.game.turn > 0 and self.game.turn < game.turn:
            self.show_turn_summary = True
            last_hand = [
                data.Card.from_dict(card) for card in game.summary["last_hand"]
            ]
            self.post_message(
                FooterMessage(str(last_hand + game.summary["turn_order"]))
            )

    def _handle_next_round(self, game: data.Game) -> None:
        if (
            self.game is not None
            and self.game.round > 0
            and self.game.round < game.round
        ):
            self.show_round_summary = True
            self.show_turn_summary = False
            self.app.push_screen(SummaryScreen(game))

    @on(UpdateMessage)
    async def handle_game_update(self, message: UpdateMessage) -> None:
        game = message.game
        if game is not None:
            player = game.get_player_by_name(self.app.name)
            self.hand = player.hand

            self._handle_first_turn(game, player)

            self._handle_next_turn(game)

            self._handle_next_round(game)

        # This has to come after the above prep, because otherwise it was triggering
        # a watch method out of order lower down.  Need to look again and see if
        # reactive is even needed lower down, since we recompose at the top
        self.game = game
