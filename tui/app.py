import asyncio

from textual import on
from textual.app import App
from textual.reactive import reactive
from textual.screen import Screen

from hearts_textual import data
from hearts_textual.commands import GAME

from tui.game_screen import GameScreen
from tui.login_screen import LoginScreen
from tui.messages import BasicMessage, CommandMessage, ToasterMessage

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


class HeartsApp(App):
    CSS_PATH = "app.css"

    websocket = None
    websocket_task = None
    command_queue = asyncio.Queue()
    game = reactive(None)

    def on_ready(self) -> None:
        self.push_screen(GameScreen(self))
        self.push_screen(LoginScreen(self))

    def action_toaster(self, message: str) -> None:
        self.post_message(ToasterMessage(message))

    def action_new_game(self) -> None:
        self.pop_screen()

    def action_update_game(self) -> None:
        self.game = GAME
        self.toaster(ToasterMessage("game updated"))

    def watch_game(self, game) -> None:
        self.screen.game = game

    @on(BasicMessage)
    async def handle_message(self, message: BasicMessage) -> None:
        # self.query_one("#Footer").update(message.message)
        await self.run_action(message.message)

    @on(ToasterMessage)
    def toaster(self, message: ToasterMessage) -> None:
        self.notify(
            message.message,
            title=message.title,
            severity=message.severity,
            timeout=message.timeout,
        )

    @on(CommandMessage)
    async def send_command(self, message: CommandMessage) -> None:
        await self.command_queue.put(message.command)


if __name__ == "__main__":
    HeartsApp().run()
