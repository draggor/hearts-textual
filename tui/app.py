from textual import on
from textual.app import App
from textual.screen import Screen

from tui.game_screen import GameScreen
from tui.login_screen import LoginScreen
from tui.messages import BasicMessage, ToasterMessage


class HeartsApp(App):
    CSS_PATH = "app.css"

    websocket = None
    websocket_task = None

    def on_ready(self) -> None:
        self.push_screen(GameScreen())
        self.push_screen(LoginScreen(self))

    @on(BasicMessage)
    def handle_message(self, message: BasicMessage) -> None:
        self.query_one("#Footer").update(message.message)

    @on(ToasterMessage)
    def toaster(self, message: ToasterMessage) -> None:
        self.notify(
            message.message,
            title=message.title,
            severity=message.severity,
            timeout=message.timeout,
        )


if __name__ == "__main__":
    HeartsApp().run()
