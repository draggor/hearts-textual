from typing import Any, Dict

from hearts_textual.data import Card, Game, Player, Message


COMMANDS = {}
GAME = Game()
GAME.reset()

SOCKETS_TO_PLAYERS: Dict[Any, Player] = {}
PLAYERS_TO_SOCKETS: Dict[Player, Any] = {}


def reset() -> None:
    """
    Currently only for testing???
    """
    GAME.reset()
    SOCKETS_TO_PLAYERS: Dict[Any, Player] = {}
    PLAYERS_TO_SOCKETS: Dict[Player, Any] = {}


def require_start(func):
    """
    Must come after @command decorator
    """

    def inner(*args, **kwargs):
        if GAME.started:
            return func(*args, **kwargs)

        return create(echo, message="Game not started!")

    inner.__name__ = func.__name__

    return inner


def command(func):
    """
    @command decorator
    """

    def create(**args) -> Message:
        return Message(command=func.__name__, args=args)

    setattr(func, "create", create)
    COMMANDS[func.__name__] = func

    return func


def create(func, **args) -> Message:
    """
    Helper function to @command.create because mypy complains
    """
    return func.create(**args)  # type: ignore


# TODO: this either needs to return a Message or
#       run_command needs to be -> Optional[Message]
@command
def echo(*, websocket, message: str):
    return message


def run_command(message_str: str, websocket) -> Message:
    """
    Primary hook on both server and client to parse and run
    a json message & command
    """
    message = Message.from_json(message_str)  # type: ignore

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

    # return create(echo, message=f"{player.name} has connected!")
    return create(update, state=GAME, messages=[f"{player.name} has connected!"])
    # return create(update, state=GAME)


@command
def draw(*, websocket) -> Message:
    return create(echo, message=f"{GAME.deck.pop()}")


@command
def update(*, websocket, state, messages: list[str]):
    """
    Only should be run on clients
    """
    GAME = Game.from_dict(state)
    return messages


@command
def new_game(*, websocket) -> Message:
    count = GAME.player_connected_count()
    if count != 4 and not GAME.bots:
        return create(echo, message=f"Must have exactly 4 players!  We have {count}")

    GAME.new_game()

    return create(update, state=GAME)


@command
@require_start
def next_round(*, websocket) -> Message:
    GAME.next_round()
    return create(update, state=GAME)


@command
@require_start
def next_turn(*, websocket) -> Message:
    GAME.next_turn()
    return create(update, state=GAME)


@command
@require_start
def play_card(*, websocket, card) -> Message:
    c = Card.from_dict(card)  # type: ignore
    player = SOCKETS_TO_PLAYERS[websocket]

    result = GAME.play_card(c, player)

    if type(result) is not Game:
        return create(echo, message=result)

    return create(update, state=GAME)
