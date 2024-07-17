from data import hashabledict
from string import Template

import pytest

from hearts_textual.commands import (
    run_command,
    Message,
    reset,
    GAME,
    SOCKETS_TO_PLAYERS,
    PLAYERS_TO_SOCKETS,
)
from hearts_textual.data import Card


base_template = Template('{"command": "$command", "args": $args}')
echo_template = Template(
    base_template.substitute(command="echo", args='{"message": "$message"}')
)
join_template = Template(
    base_template.substitute(command="join", args='{"name": "$name"}')
)
new_game_str = base_template.substitute(command="new_game", args="{}")
next_round_str = base_template.substitute(command="next_round", args="{}")
next_turn_str = base_template.substitute(command="next_turn", args="{}")
play_card_template = Template(
    base_template.substitute(command="play_card", args='{"card": $card}')
)


def hands():
    pprint("Hands:")
    for player in GAME.players:
        pprint(player.hand)


def final_scores():
    pprint("scores")
    for player in GAME.players:
        pprint([player.score_total()] + player.scores)


def run_helper(command, socket):
    message = run_command(command, socket)

    if message is None:
        return None

    if "state" in message.args:
        return message.args["state"], message.command
    if "message" in message.args:
        return message.args["message"], message.command

    raise Exception(f"Message went wrong: {message}")


@pytest.fixture
def echo():
    def inner(message):
        return echo_template.substitute(message=message)

    return inner


@pytest.fixture
def join():
    def inner(name):
        return join_template.substitute(name=name)

    return inner


@pytest.fixture
def play_card():
    def inner(card):
        if type(card) is str:
            card = Card.parse(card)
        return play_card_template.substitute(card=card.to_json())

    return inner


@pytest.fixture
def websocket():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return hashabledict(_id=count)

    return inner


player_names = ["Homer", "Goose", "Penguin", "Menace"]


@pytest.fixture
def four_players_and_sockets(join, websocket):
    sockets = []

    for i in range(4):
        w = websocket()
        name = player_names[i]
        run_helper(join(name), w)
        sockets.append(w)

    return sockets


@pytest.fixture(autouse=True)
def game_reset():
    yield None
    reset()


@pytest.fixture
def swap_cards():
    def inner(cards1, cards2):
        if type(cards1) is not list:
            cards1 = [cards1]

        if type(cards2) is not list:
            cards2 = [cards2]

        for card1str, card2str in zip(cards1, cards2):
            card1 = Card.parse(card1str)
            card2 = Card.parse(card2str)
            p1 = GAME.has_card(card1)
            p2 = GAME.has_card(card2)
            p1.hand.remove(card1)
            p1.hand.append(card2)
            p1.hand.sort()
            p2.hand.remove(card2)
            p2.hand.append(card1)
            p2.hand.sort()

    return inner
