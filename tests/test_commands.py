from string import Template
from typing import List, Optional

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
from hearts_textual.data import Card, Suits, Values, Game, TWO_OF_CLUBS, parse_card


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



def run_helper(command, socket):
    message = run_command(command, socket)

    if message is None:
        return None

    if 'state' in message.args:
        return message.args['state'], message.command
    if 'message' in message.args:
        return message.args['message'], message.command

    raise Exception(f"Message went wrong: {message}")


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
        if type(card) is str:
            card = parse_card(card)
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
            card1 = parse_card(card1str)
            card2 = parse_card(card2str)
            p1 = GAME.has_card(card1)
            p2 = GAME.has_card(card2)
            p1.hand.remove(card1)
            p1.hand.append(card2)
            p1.hand.sort()
            p2.hand.remove(card2)
            p2.hand.append(card1)
            p2.hand.sort()

    return inner


class TestCommands:
    def test_echo(self, echo, websocket, capsys):
        result = run_helper(echo, websocket())

        captured = capsys.readouterr()

        assert captured.out == "Broadcast: honk\n"

    def test_join(self, join, websocket):
        message, command = run_helper(join("Homer"), websocket())

        assert command == "echo"
        assert message == "Homer has connected!"

    def test_new_game_not_enough_players_1(self, join, websocket):
        w = websocket()
        run_helper(join("A Goose"), w)
        message, command = run_helper(new_game_str, w)

        assert message == "Must have exactly 4 players!  We have 1"

    def test_new_game_not_enough_players_3(self, join, websocket):
        w1 = websocket()
        w2 = websocket()
        w3 = websocket()
        run_helper(join("A Goose"), w1)
        run_helper(join("A Burd"), w2)
        run_helper(join("A Menace"), w3)
        message, command = run_helper(new_game_str, w1)

        assert message == "Must have exactly 4 players!  We have 3"

    def test_new_game(self, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        state, command= run_helper(new_game_str, w1)

        assert command == "update"
        assert state.started

    def test_next_round_fail(self, join, websocket):
        w = websocket()
        run_helper(join("Honk"), w)
        message, _ = run_helper(next_round_str, w)

        assert message == "Game not started!"

    def test_next_round(self, four_players_and_sockets):
        [w1, w2, w3, w4] = four_players_and_sockets
        run_helper(new_game_str, w1)
        game, _ = run_helper(next_round_str, w1)

        for player in game.players:
            assert len(player.hand) == 13
            assert player.connected


class TestGameLoop:
    @pytest.fixture(autouse=True)
    def setup_game(self, mocker, four_players_and_sockets):
        self.sockets = four_players_and_sockets
        [w1, w2, w3, w4] = self.sockets
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

        run_helper(new_game_str, w1)
        run_helper(next_round_str, self.w1)
        game, _ = run_helper(next_turn_str, self.w1)
        self.game = game

    @pytest.fixture
    def one_full_turn(self, play_card):
        def inner(
            *,
            indexes: Optional[List[int]] = None,
            cards: Optional[List[str]] = None,
            order: List[int] = [0, 1, 2, 3]
        ) -> Game:
            if indexes is not None:
                i1, i2, i3, i4 = indexes
                run_helper(play_card(self.p1.hand[i1]), self.sockets[order[0]])
                run_helper(play_card(self.p2.hand[i2]), self.sockets[order[1]])
                run_helper(play_card(self.p3.hand[i3]), self.sockets[order[2]])
                game, _ = run_helper(play_card(self.p4.hand[i4]), self.sockets[order[3]])
                return game  # type: ignore
            if cards is not None:
                c1, c2, c3, c4 = [parse_card(card) for card in cards]
                run_helper(play_card(c1), self.sockets[order[0]])
                run_helper(play_card(c2), self.sockets[order[1]])
                run_helper(play_card(c3), self.sockets[order[2]])
                game, _ = run_helper(play_card(c4), self.sockets[order[3]])
                return game  # type: ignore

            raise Exception("must use one of: indexes, cards")

        return inner

    def test_play_first_card(self, play_card):
        socket = PLAYERS_TO_SOCKETS[self.game.get_lead_player()]
        card = self.game.get_lead_player().hand[0]
        new_game, _ = run_helper(play_card(card), socket)

        assert new_game.played_cards[0] == TWO_OF_CLUBS
        assert len(new_game.get_lead_player().hand) == 12


    def test_invalid_first_card_not_two_of_clubs(self, play_card):
        socket = PLAYERS_TO_SOCKETS[self.game.get_lead_player()]
        card = Card(suit=Suits.CLUBS, value=Values.SIX)
        message, _ = run_helper(play_card(card), socket)

        assert message == "Card 6♧ is invalid, must be 2♧"

    def test_invalid_first_player(self, play_card):
        card = Card(suit=Suits.CLUBS, value=Values.SIX)
        message, _ = run_helper(play_card(card), self.w2)

        assert message == "It's not Goose's turn!  It is Homer's!"

    def test_play_one_full_turn(self, one_full_turn):
        game = one_full_turn(cards=["2C", "3C", "4C", "5C"])

        assert game.get_lead_player() == self.p4
        assert game.turn_order == [3, 0, 1, 2]
        assert game.hearts_broken is False
        assert game.summary["last_hand"][0] == TWO_OF_CLUBS
        assert len(game.played_cards) == 0

    def test_invalid_second_card_not_in_hand(self, play_card, one_full_turn):
        game = one_full_turn(cards=["2C", "3C", "4C", "5C"])
        socket = PLAYERS_TO_SOCKETS[self.game.get_lead_player()]
        card = parse_card("QC")
        message, _ = run_helper(play_card(card), socket)

        assert message == "Card Q♧ not in Player Menace's hand"

    def test_play_two_full_turns(self, one_full_turn):
        game = one_full_turn(cards=["2C", "3C", "4C", "5C"])
        game = one_full_turn(cards=["9C", "6C", "7C", "8C"], order=[3, 0, 1, 2])

        assert game.get_lead_player() == self.p4
        assert game.turn_order == [3, 0, 1, 2]
        assert game.hearts_broken is False
        assert game.summary["last_hand"][0] == parse_card("9C")
        assert len(game.played_cards) == 0

    def test_play_heart_denied(self, play_card):
        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        message, _ = run_helper(play_card("4H"), self.w2)

        assert message == "Card 4♥︎ is invalid, hearts not broken!"

    def test_play_queen_of_spades_denied(self, play_card, swap_cards):
        swap_cards("QS", "KS")
        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        message, _ = run_helper(play_card("QS"), self.w2)

        assert message == "Card Q♤ is invalid, can't throw crap on the first turn!"

    def test_play_card_out_of_suit_denied(self, play_card, swap_cards):
        swap_cards(["4S", "8S", "QS"], ["3C", "7C", "JC"])

        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        run_helper(play_card('2D'), self.w2)
        message, _ = run_helper(play_card("3D"), self.w3)

        assert message == "Card 3♦︎ is invalid, must play a ♧!"

    def test_player_order_1(self, play_card):
        run_helper(play_card('2C'), self.w1)
        message, _ = run_helper(play_card('8C'), self.w3)

        assert message == "It's not Penguin's turn!  It is Goose's!"

    # def test_play_three_full_turns(self, one_full_turn):
    #    pprint(GAME)
    #    for player in GAME.players:
    #        pprint(player.hand)
    #    game = one_full_turn(cards=["2C", "3C", "4C", "5C"])
    #    game = one_full_turn(cards=["9C", "6C", "7C", "8C"], order=[3, 0, 1, 2])

    #    assert game.get_lead_player() == self.p4
    #    assert game.turn_order == [3, 0, 1, 2]
    #    assert game.hearts_broken is False
    #    assert game.summary["last_hand"][0] == parse_card("9C")
    #    assert len(game.played_cards) == 0
