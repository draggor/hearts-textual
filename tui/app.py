from textual import on
from textual.app import App
from textual.screen import Screen

from tui.game_screen import GameScreen
from tui.login_screen import LoginScreen


class HeartsApp(App):
    CSS_PATH = "app.css"

    websocket = None
    websocket_task = None

    def on_ready(self) -> None:
        self.push_screen(GameScreen())
        # self.push_screen(LoginScreen(self))

    @on(LoginScreen.LoginMessage)
    def handle_message(self, message: LoginScreen.LoginMessage) -> None:
        self.query_one("#Footer").update(message.message)


if __name__ == "__main__":
    HeartsApp().run()
