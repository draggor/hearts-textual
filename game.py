from data import Card, Deck, Game, Player
from random import shuffle


class GameManager:
    def __init__(self):
        self.game = Game()
        self.game.reset()

    def add_player(player: Player):
        self.game.players.append(player)

    def draw(self) -> Card:
        return self.game.deck.cards.pop()
