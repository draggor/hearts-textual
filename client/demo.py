from decimal import Decimal

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual import events
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Static, Placeholder


class Header(Placeholder):
    pass


class PlayArea(Container):
    def compose(self) -> ComposeResult:
        yield Placeholder(id='P2')
        yield Placeholder(id='P4')
        yield Placeholder(id='P1')
        yield Placeholder(id='P3')


class Hand(Placeholder):
    pass


class GameScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id='Header')
        yield Hand(id='Hand')
        yield PlayArea(id='PlayArea')

class HeartsApp(App):
    CSS_PATH = "demo.css"

    def on_ready(self) -> None:
        self.push_screen(GameScreen())

    #def compose(self) -> ComposeResult:
    #    """Add our buttons."""
    #    yield Container(
    #        Static(id="topbar"),
    #        Static(id="leftspace"),
    #        Button("3♤", id="card0", variant="warning"),
    #        Button("10♤", id="card1", variant="warning"),
    #        Button("2♡", id="card2", variant="warning"),
    #        Static(id="rightspace"),
    #        Static(id="midbar"),
    #        Button("K♡", id="hand0"),
    #        Button("J♡", id="hand1"),
    #        Button("3♡", id="hand2"),
    #        Button("6♡", id="hand3"),
    #        Button("2♡", id="hand4"),
    #        Button("2♧", id="hand5"),
    #        Button("A♧", id="hand6"),
    #        Button("7♧", id="hand7"),
    #        Button("8♤", id="hand9"),
    #        Button("Q♤", id="hand11"),
    #        Button("8♢", id="hand8"),
    #        Button("9♢", id="hand10"),
    #        Button("Q♢", id="hand12"),
    #        id="tableau",
    #    )


if __name__ == "__main__":
    HeartsApp().run()
