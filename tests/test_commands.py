from typing import List, Optional

from rich import print_json
from rich.pretty import pprint
import pytest

from hearts_textual.commands import (
    run_command,
    SOCKETS_TO_PLAYERS,
    PLAYERS_TO_SOCKETS,
)
from hearts_textual.data import Card, Suits, Values, Game, TWO_OF_CLUBS

from tests.fixtures import (
    hands,
    final_scores,
    run_helper,
    echo,
    join,
    play_card,
    websocket,
    player_names,
    four_players_and_sockets,
    game_reset,
    swap_cards,
    new_game_str,
    next_round_str,
    next_turn_str,
)


class TestCommands:
    def test_echo(self, echo, websocket, capsys):
        messages, _ = run_command(echo("honk"), websocket())

        assert messages[0] == "toaster('honk')"

    def test_join(self, join, websocket):
        message = run_command(join("Homer"), websocket())

        assert message.command == "update"
        assert message.args["messages"][0] == "toaster('Homer has connected!')"

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
        state, command = run_helper(new_game_str, w1)

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
            order: List[int] = [0, 1, 2, 3],
        ) -> Game:
            if indexes is not None:
                i1, i2, i3, i4 = indexes
                run_helper(play_card(self.p1.hand[i1]), self.sockets[order[0]])
                run_helper(play_card(self.p2.hand[i2]), self.sockets[order[1]])
                run_helper(play_card(self.p3.hand[i3]), self.sockets[order[2]])
                game, _ = run_helper(
                    play_card(self.p4.hand[i4]), self.sockets[order[3]]
                )
                return game  # type: ignore
            if cards is not None:
                c1, c2, c3, c4 = [Card.parse(card) for card in cards]
                run_helper(play_card(c1), self.sockets[order[0]])
                run_helper(play_card(c2), self.sockets[order[1]])
                run_helper(play_card(c3), self.sockets[order[2]])
                game, _ = run_helper(play_card(c4), self.sockets[order[3]])
                return game  # type: ignore

            raise Exception("must use one of: indexes, cards")

        return inner

    @pytest.fixture
    def one_full_round(self, swap_cards, one_full_turn):
        def inner() -> Game:
            swap_cards(
                "3H,7H,JH,4H,8H,QH,9H,KH".split(","),
                "5C,9C,KC,4D,8D,QD,7S,JS".split(","),
            )
            game = one_full_turn(cards=["2C", "3C", "4C", "3S"], order=[0, 1, 2, 3])
            game = one_full_turn(cards=["3D", "2H", "KD", "QD"], order=game.turn_order)
            game = one_full_turn(cards=["AC", "JC", "QC", "3H"], order=game.turn_order)
            game = one_full_turn(cards=["KC", "7C", "8C", "4H"], order=game.turn_order)
            game = one_full_turn(cards=["QS", "KS", "JS", "6H"], order=game.turn_order)
            game = one_full_turn(cards=["AD", "JD", "7H", "9D"], order=game.turn_order)
            game = one_full_turn(cards=["TD", "7D", "8H", "5D"], order=game.turn_order)
            game = one_full_turn(cards=["9S", "AS", "9H", "8S"], order=game.turn_order)
            game = one_full_turn(cards=["TS", "TH", "4S", "5S"], order=game.turn_order)
            game = one_full_turn(cards=["5H", "AH", "TC", "8D"], order=game.turn_order)
            game = one_full_turn(cards=["KH", "9C", "6D", "7S"], order=game.turn_order)
            game = one_full_turn(cards=["QH", "6C", "4D", "6S"], order=game.turn_order)
            game = one_full_turn(cards=["JH", "5C", "2D", "2S"], order=game.turn_order)
            return game  # type: ignore

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
        card = Card.parse("QC")
        message, _ = run_helper(play_card(card), socket)

        assert message == "Card Q♧ not in Player Menace's hand"

    def test_play_two_full_turns(self, one_full_turn):
        game = one_full_turn(cards=["2C", "3C", "4C", "5C"])
        game = one_full_turn(cards=["9C", "6C", "7C", "8C"], order=[3, 0, 1, 2])

        assert game.get_lead_player() == self.p4
        assert game.turn_order == [3, 0, 1, 2]
        assert game.hearts_broken is False
        assert game.summary["last_hand"][0] == Card.parse("9C")
        assert len(game.played_cards) == 0

    def test_play_heart_denied(self, play_card):
        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        message, _ = run_helper(play_card("4H"), self.w2)

        assert message == "Card 4♡ is invalid, hearts not broken!"

    def test_play_queen_of_spades_denied(self, play_card, swap_cards):
        swap_cards("QS", "KS")
        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        message, _ = run_helper(play_card("QS"), self.w2)

        assert message == "Card Q♤ is invalid, can't throw crap on the first turn!"

    def test_play_card_out_of_suit_denied(self, play_card, swap_cards):
        swap_cards(["4S", "8S", "QS"], ["3C", "7C", "JC"])

        run_helper(play_card(TWO_OF_CLUBS), self.w1)
        run_helper(play_card("2D"), self.w2)
        message, _ = run_helper(play_card("3D"), self.w3)

        assert message == "Card 3♢ is invalid, must play a ♧!"

    def test_play_out_of_order_denied(self, play_card):
        run_helper(play_card("2C"), self.w1)
        message, _ = run_helper(play_card("8C"), self.w3)

        assert message == "It's not Penguin's turn!  It is Goose's!"

    def test_break_hearts(self, play_card, swap_cards, one_full_turn):
        swap_cards(
            "3H,7H,JH,4H,8H,QH,5H,9H,KH".split(","),
            "5C,9C,KC,4D,8D,QD,3S,7S,JS".split(","),
        )
        game = one_full_turn(cards=["2C", "3C", "4C", "2H"])

        assert game.turn == 2
        assert game.hearts_broken

    def test_play_hearts_after_break(self, play_card, swap_cards, one_full_turn):
        swap_cards(
            "3H,7H,JH,4H,8H,QH,9H,KH".split(","), "5C,9C,KC,4D,8D,QD,7S,JS".split(",")
        )

        one_full_turn(cards=["2C", "3C", "4C", "3S"])
        one_full_turn(cards=["3D", "2H", "KD", "QD"], order=[2, 3, 0, 1])
        game = one_full_turn(cards=["9D", "AD", "JD", "KH"])

        assert game.turn == 4
        assert game.hearts_broken

    def test_play_full_round(self, swap_cards, one_full_turn):
        swap_cards(
            "3H,7H,JH,4H,8H,QH,9H,KH".split(","), "5C,9C,KC,4D,8D,QD,7S,JS".split(",")
        )
        game = one_full_turn(cards=["2C", "3C", "4C", "3S"])
        game = one_full_turn(cards=["3D", "2H", "KD", "QD"], order=game.turn_order)
        game = one_full_turn(cards=["AC", "JC", "QC", "3H"], order=game.turn_order)
        game = one_full_turn(cards=["KC", "7C", "8C", "4H"], order=game.turn_order)
        game = one_full_turn(cards=["QS", "KS", "JS", "6H"], order=game.turn_order)
        game = one_full_turn(cards=["AD", "JD", "7H", "9D"], order=game.turn_order)
        game = one_full_turn(cards=["TD", "7D", "8H", "5D"], order=game.turn_order)
        game = one_full_turn(cards=["9S", "AS", "9H", "8S"], order=game.turn_order)
        game = one_full_turn(cards=["TS", "TH", "4S", "5S"], order=game.turn_order)
        game = one_full_turn(cards=["5H", "AH", "TC", "8D"], order=game.turn_order)
        game = one_full_turn(cards=["KH", "9C", "6D", "7S"], order=game.turn_order)
        game = one_full_turn(cards=["QH", "6C", "4D", "6S"], order=game.turn_order)
        game = one_full_turn(cards=["JH", "5C", "2D", "2S"], order=game.turn_order)

        scores = [player.scores[-1] for player in game.players]

        assert game.round == 2
        assert game.turn == 1
        assert game.ended == False
        assert scores == [3, 16, 2, 5]

    def test_play_two_full_rounds(self, one_full_round):
        one_full_round()
        game = one_full_round()

        scores = [player.scores[-1] for player in game.players]

        assert game.round == 3
        assert game.turn == 1
        assert scores == [3, 16, 2, 5]

    def test_play_to_end(self, one_full_round):
        game = one_full_round()
        game = one_full_round()
        game = one_full_round()
        game = one_full_round()
        game = one_full_round()
        game = one_full_round()
        game = one_full_round()

        scores = [player.scores[-1] for player in game.players]
        total_scores = [player.score_total() for player in game.players]

        assert game.round == 8
        assert game.turn == 0
        assert game.ended
        assert scores == [3, 16, 2, 5]
        assert total_scores == [21, 112, 14, 35]
