from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalScroll
from textual.messages import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Input, Placeholder, Static

from hearts_textual import data
from tui.base_screen import BaseScreen
from tui.messages import CommandMessage


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
    p1name = reactive("")
    p2name = reactive("")
    p3name = reactive("")
    p4name = reactive("")
    game: data.Game = reactive(None, recompose=True)

    def __init__(self, game: data.Game) -> None:
        super().__init__()
        self.game = game

    def watch_game(self, game) -> None:
        if game is not None:
            for pcard, card in zip(
                [self.p1card, self.p2card, self.p3card, self.p4card], game.played_cards
            ):
                pcard.card = card

            names = [player.name for player in self.game.players]
            for pname, name in zip([p1name, p2name, p3name, p4name], names):
                pname = name

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
    game = reactive(None, recompose=True)

    class PlayCardMessage(Message):
        def __init__(self, card: data.Card) -> None:
            self.card = card
            super().__init__()

    def __init__(self, game: data.Game, *, id: str = ""):
        super().__init__()

        self.game = game

        if game is not None:
            cards = self.game.players[0].hand
            self.cards = [Card(card, in_hand=True, id=repr(card)) for card in cards]
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

    def remove_card(self, event: Button.Pressed) -> None:
        card = event.button.card
        player = self.game.players[0]
        game_or_error = self.game.play_card(card, player)

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

    # hand = demo_game.players[0].hand
    game: data.Game = reactive(None, recompose=True)
    app: App = None

    def __init__(self, app: App):
        super().__init__()
        self.app = app

    def compose(self) -> ComposeResult:
        with BaseScreen():
            # Without nested container, Hand docks to bottom over footer in BaseScreen
            with Container():
                yield Hand(self.game)
                yield PlayArea(self.game)

    @on(Hand.PlayCardMessage)
    def handle_play_card(self, message: Hand.PlayCardMessage) -> None:
        self.query_one(PlayArea).play_card(message.card)
