from data import Card, Deck, Game, Player, Message


COMMANDS = {}
GAME = Game()
GAME.reset()


def command(func):
    COMMANDS[func.__name__] = func


def run_command(message_str: str, websocket):
    message = Message.from_json(message_str)
    print(message)
    if message.command in COMMANDS:
        return COMMANDS[message.command](**message.args)

    return f"Command {message.command} not found!"


@command
def help():
    return f"Commands: {', '.join(COMMANDS.keys())}"


@command
def join(name):
    player = Player(name=name)
    GAME.players.append(player)
    return f"{name} has connected!"


@command
def draw():
    return f"{GAME.deck.cards.pop()}"


@command
def new_game():
    count = GAME.player_count()
    if count != 4:
        return f"Must have exactly 4 players!  We have {count}"

    GAME.reset()

    return "Starting..."
