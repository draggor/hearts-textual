from typing import List, Optional

import pytest

from hearts_textual.commands import (
    run_command,
    GAME,
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


class TestGameLoopBots:
    @pytest.fixture(autouse=True)
    def setup_game(self, mocker, websocket, join):
        GAME.bots = True
        self.w1 = websocket()
        name = player_names[0]
        run_helper(join(name), self.w1)
        self.sockets = [self.w1]
        self.p1 = SOCKETS_TO_PLAYERS[self.w1]

        def mock_shuffle(self):
            return self

        mocker.patch("hearts_textual.data.Game.shuffle", mock_shuffle)
        mocker.patch("hearts_textual.data.Game.shuffle_players", mock_shuffle)

        run_helper(new_game_str, self.w1)
        run_helper(next_round_str, self.w1)
        game, _ = run_helper(next_turn_str, self.w1)
        self.game = game

    def test_game_started(self):
        assert type(self.game) == Game

    def test_play_first_card(self, play_card):
        player = self.game.get_lead_player()

        assert player == None
