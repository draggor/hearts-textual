from string import Template

from rich.pretty import pprint
import pytest

from data import hashabledict

from hearts_textual.commands import (
    run_command,
    Message,
    reset,
    GAME,
    SOCKETS_TO_PLAYERS,
    PLAYERS_TO_SOCKETS,
)
from hearts_textual.data import Card, Suits, Values, Game, TWO_OF_CLUBS


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


@pytest.fixture
def echo():
    return echo_template.substitute(message="honk")


@pytest.fixture
def join():
    def inner(name):
        return join_template.substitute(name=name)

    return inner


@pytest.fixture
def play_card():
    def inner(card):
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
        run_command(join(name), w)
        sockets.append(w)

    return sockets


@pytest.fixture(autouse=True)
def game_reset():
    yield None
    reset()


class TestCommands:
    def test_echo(self, echo, websocket, capsys):
        result = run_command(echo, websocket())

        captured = capsys.readouterr()

        assert captured.out == "Broadcast: honk\n"

    def test_join(self, join, websocket):
        result = run_command(join("Homer"), websocket())

        assert result.command == "echo"
        assert result.args["message"] == "Homer has connected!"

    def test_new_game_not_enough_players_1(self, join, websocket):
        w = websocket()
        run_command(join("A Goose"), w)
        result = run_command(new_game_str, w)

        assert result.args["message"] == "Must have exactly 4 players!  We have 1"

    def test_new_game_not_enough_players_3(self, join, websocket):
        w1 = websocket()
        w2 = websocket()
        w3 = websocket()
        run_command(join("A Goose"), w1)
        run_command(join("A Burd"), w2)
        run_command(join("A Menace"), w3)
        result = run_command(new_game_str, w1)

        assert result.args["message"] == "Must have exactly 4 players!  We have 3"

    def test_new_game(self, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        result = run_command(new_game_str, w1)

        assert result.command == "update"
        assert result.args["state"].started

    def test_next_round_fail(self, join, websocket):
        w = websocket()
        run_command(join("Honk"), w)
        result = run_command(next_round_str, w)

        assert result.args["message"] == "Game not started!"

    def test_next_round(self, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        run_command(new_game_str, w1)
        result = run_command(next_round_str, w1)
        game = result.args["state"]

        for player in game.players:
            assert len(player.hand) == 13
            assert player.connected


class TestGameLoop:
    @pytest.fixture(autouse=True)
    def setup_game(self, mocker, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        self.w1 = w1
        self.p1 = SOCKETS_TO_PLAYERS[w1]
        self.w2 = w2
        self.p2 = SOCKETS_TO_PLAYERS[w2]
        self.w3 = w3
        self.p3 = SOCKETS_TO_PLAYERS[w3]
        self.w4 = w4
        self.p4 = SOCKETS_TO_PLAYERS[w4]

        def mock_shuffle(self):
            return self

        mocker.patch("hearts_textual.data.Game.shuffle", mock_shuffle)
        mocker.patch("hearts_textual.data.Game.shuffle_players", mock_shuffle)

        run_command(new_game_str, w1)
        run_command(next_round_str, self.w1).args["state"]
        self.game = run_command(next_turn_str, self.w1).args["state"]

    def test_play_first_card(self, play_card):
        socket = PLAYERS_TO_SOCKETS[self.game.lead_player]
        card = self.game.lead_player.hand[0]
        new_game = run_command(play_card(card), socket).args["state"]

        assert new_game.played_cards[0] == TWO_OF_CLUBS
        assert len(new_game.lead_player.hand) == 12

    # def test_invalid_second_card_not_in_hand(self, play_card):
    #    socket = PLAYERS_TO_SOCKETS[self.game.lead_player]
    #    card = Card(suit=Suits.CLUBS, value=Values.KING)
    #    message = run_command(play_card(card), socket).args["message"]

    #    assert message == "Card K♧ not in Player Menace's hand"

    def test_invalid_first_card_not_two_of_clubs(self, play_card):
        socket = PLAYERS_TO_SOCKETS[self.game.lead_player]
        card = Card(suit=Suits.CLUBS, value=Values.SIX)
        message = run_command(play_card(card), socket).args["message"]

        assert message == "Card 6♧ is invalid, must be 2♧"

    def test_invalid_first_player(self, play_card):
        card = Card(suit=Suits.CLUBS, value=Values.SIX)
        message = run_command(play_card(card), self.w2).args["message"]

        assert message == "Player Goose not allowed to play yet, must be Homer!"

    def test_play_one_full_turn(self, play_card):
        run_command(play_card(self.p1.hand[0]), self.w1)
        run_command(play_card(self.p2.hand[0]), self.w2)
        run_command(play_card(self.p3.hand[0]), self.w3)
        result = run_command(play_card(self.p4.hand[0]), self.w4)
        pprint(result)
