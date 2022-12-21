from .data import Card, Game, Player, Message


COMMANDS = {}
GAME = Game()
GAME.reset()

SOCKETS_TO_PLAYERS = {}
PLAYERS_TO_SOCKETS = {}


def command(func):
    COMMANDS[func.__name__] = func

    def create(**args) -> Message:
        return Message(command=func.__name__, args=args)

    setattr(func, "create", create)

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


names = ["four", "three", "two", "one"]


@command
def join(*, websocket, name: str) -> Message:
    # TODO: we no longer make new players, need to associate an unclaimed
    #       player with a websocket
    print(name)
    if name == "random":
        name = names.pop()
    player = Player(name=name)
    GAME.players.append(player)
    return create(echo, message=f"{name} has connected!")


@command
def draw(*, websocket) -> Message:
    return create(echo, message=f"{GAME.deck.pop()}")


@command
def update(*, websocket, state):
    game = Game.from_json(state)
    print(game)


@command
def new_game(*, websocket) -> Message:
    count = GAME.player_count()
    if count != 4:
        return create(echo, message=f"Must have exactly 4 players!  We have {count}")

    GAME.reset()
    GAME.next_round()

    return create(echo, message="Starting...")
