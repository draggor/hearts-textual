from hearts_textual.data import Game

import pytest


class TestGame:
    @pytest.fixture(autouse=True)
    def new_game(self):
        self.game = Game()
        self.game.reset()

    def test_reset(self):
        game = self.game

        assert game.round == 0
        assert len(game.deck) == 52
        assert game.lead_player is None
        assert len(game.players) == 4
        assert len(game.played_cards) == 0
