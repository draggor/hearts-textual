from decimal import Decimal

from textual.app import App, ComposeResult
from textual import events
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Static


class HeartsApp(App):
    """A working 'desktop' calculator."""

    CSS_PATH = "hearts.css"

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")

    NAME_MAP = {
        "asterisk": "multiply",
        "slash": "divide",
        "underscore": "plus-minus",
        "full_stop": "point",
        "plus_minus_sign": "plus-minus",
        "percent_sign": "percent",
        "equals_sign": "equals",
        "minus": "minus",
        "plus": "plus",
    }

    def watch_numbers(self, value: str) -> None:
        """Called when numbers is updated."""
        # Update the Numbers widget
        # self.query_one("#numbers", Static).update(value)

    def compute_show_ac(self) -> bool:
        """Compute switch to show AC or C button"""
        return self.value in ("", "0") and self.numbers == "0"

    def watch_show_ac(self, show_ac: bool) -> None:
        """Called when show_ac changes."""
        # self.query_one("#c").display = not show_ac
        # self.query_one("#ac").display = show_ac

    def compose(self) -> ComposeResult:
        """Add our buttons."""
        yield Container(
            Static(id="topbar"),
            Static(id="leftspace"),
            Button("3♤", id="card0", variant="warning"),
            Button("10♤", id="card1", variant="warning"),
            Button("2♡", id="card2", variant="warning"),
            Static(id="rightspace"),
            Static(id="midbar"),
            Button("K♡", id="hand0"),
            Button("J♡", id="hand1"),
            Button("3♡", id="hand2"),
            Button("6♡", id="hand3"),
            Button("2♡", id="hand4"),
            Button("2♧", id="hand5"),
            Button("A♧", id="hand6"),
            Button("7♧", id="hand7"),
            Button("8♤", id="hand9"),
            Button("Q♤", id="hand11"),
            Button("8♢", id="hand8"),
            Button("9♢", id="hand10"),
            Button("Q♢", id="hand12"),
            id="tableau",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""

        button_id = event.button.id
        assert button_id is not None
        button_value = event.button.label

        if button_id.startswith("card"):
            self.query_one("#midbar", Static).update(
                f"Ignoring button push from table."
            )
        elif button_value == "":
            self.query_one("#midbar", Static).update(
                f"{button_id} has already been played."
            )
        else:
            self.query_one("#midbar", Static).update(f"{button_value} was played.")
            event.button.label = ""


if __name__ == "__main__":
    HeartsApp().run()
