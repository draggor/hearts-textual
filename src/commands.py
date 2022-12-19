from data import Card, Deck, Game, Player, Message


COMMANDS = {}
GAME = Game()
GAME.reset()


def command(func):
    COMMANDS[func.__name__] = func

    def create(**args):
        return Message(command=func.__name__, args=args)

    setattr(func, "create", create)

    return func


@command
def echo(message: str):
    print(f"Broadcast: {message}")


def run_command(message_str: str, websocket) -> Message:
    message = Message.from_json(message_str)  # type: ignore
    # print(message)
    if message.command in COMMANDS:
        return COMMANDS[message.command](**message.args)

    return echo.create(message=f"Command {message.command} not found!")


@command
def help():
    return echo.create(message=f"Commands: {', '.join(COMMANDS.keys())}")


@command
def join(name):
    player = Player(name=name)
    GAME.players.append(player)
    return echo.create(message=f"{name} has connected!")


@command
def draw():
    return echo.create(message=f"{GAME.deck.cards.pop()}")


@command
def new_game():
    count = GAME.player_count()
    if count != 4:
        return echo.create(message=f"Must have exactly 4 players!  We have {count}")

    GAME.reset()

    return echo.create(message="Starting...")
