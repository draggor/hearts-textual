from .data import Card, Game, Player, Message

from rich.pretty import pprint


COMMANDS = {}
GAME = Game()
GAME.reset()

SOCKETS_TO_PLAYERS = {}  # type: ignore
PLAYERS_TO_SOCKETS = {}  # type: ignore


def reset() -> None:
    GAME.reset()
    SOCKETS_TO_PLAYERS = {}  # type: ignore
    PLAYERS_TO_SOCKETS = {}  # type: ignore


def require_start(func):
    def inner(*args, **kwargs):
        if GAME.started:
            return func(*args, **kwargs)

        return create(echo, message="Game not started!")

    inner.__name__ = func.__name__

    return inner


def command(func):
    def create(**args) -> Message:
        return Message(command=func.__name__, args=args)

    setattr(func, "create", create)
    COMMANDS[func.__name__] = func

    return func


def create(func, **args) -> Message:
    return func.create(**args)  # type: ignore


@command
def echo(*, websocket, message: str):
    print(f"Broadcast: {message}")


def run_command(message_str: str, websocket) -> Message:
    message = Message.from_json(message_str)  # type: ignore
    # print(message)
    if message.command in COMMANDS:
        message.args["websocket"] = websocket
        return COMMANDS[message.command](**message.args)  # type: ignore

    return create(echo, message=f"Command {message.command} not found!")


@command
def help(*, websocket) -> Message:
    return create(echo, message=f"Commands: {', '.join(COMMANDS.keys())}")


@command
def join(*, websocket, name: str) -> Message:
    player = GAME.get_open_seat()

    if player is None:
        return create(echo, message=f"{name} tried to connect, but no open seats!")

    if name is not None and name != "random":
        player.name = name

    player.connected = True

    SOCKETS_TO_PLAYERS[websocket] = player
    PLAYERS_TO_SOCKETS[player] = websocket

    return create(echo, message=f"{player.name} has connected!")


@command
def draw(*, websocket) -> Message:
    return create(echo, message=f"{GAME.deck.pop()}")


@command
def update(*, websocket, state):
    """
    Only should be run on clients
    """
    GAME = Game.from_json(state)
    print(GAME)


@command
def new_game(*, websocket) -> Message:
    count = GAME.player_connected_count()
    if count != 4:
        return create(echo, message=f"Must have exactly 4 players!  We have {count}")

    GAME.new_game()

    return create(update, state=GAME)


@command
@require_start
def next_round(*, websocket) -> Message:
    GAME.next_round()
    return create(update, state=GAME)
