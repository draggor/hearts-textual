import copy
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum, StrEnum
from random import shuffle
from typing import Any, Dict, List, Optional

from rich.pretty import pprint


class Suits(StrEnum):
    CLUBS = "♣︎"
    DIAMONDS = "♦︎"
    SPADES = "♠︎"
    HEARTS = "♥︎"


class Values(StrEnum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


@dataclass_json
@dataclass
class Card:
    value: Values
    suit: Suits

    def __str__(self):
        return f"{self.value.value}{self.suit.value}"


DECK = [Card(suit=suit, value=value) for suit in Suits for value in Values]
TWO_OF_CLUBS = Card(value=Values.TWO, suit=Suits.CLUBS)
QUEEN_OF_SPADES = Card(value=Values.QUEEN, suit=Suits.SPADES)
HEART = Suits.HEARTS


@dataclass_json
@dataclass
class Player:
    name: str
    connected: bool = False
    hand: List[Card] = field(default_factory=list)
    pile: List[Card] = field(default_factory=list)
    scores: List[int] = field(default_factory=list)

    def score_round(self) -> int:
        hearts_score = len([card for card in self.pile if card.suit == HEART])
        queen_score = 13 if QUEEN_OF_SPADES in self.pile else 0
        print(f"{self.name}: {hearts_score}H {queen_score}Q")

        return hearts_score + queen_score

    def score_total(self) -> int:
        total = 0

        for score in self.scores:
            total += score

            if total == 100:
                total -= 100

        return total


passing_orders = [
    [1, 2, 3, 0],
    [3, 0, 1, 2],
    [2, 3, 0, 1],
    None,
]
PassingOrder = Optional[List[int]]


def default_players() -> List[Player]:
    return [
        Player(name="One"),
        Player(name="Two"),
        Player(name="Three"),
        Player(name="Four"),
    ]


@dataclass_json
@dataclass
class Game:
    round: int = 0
    deck: List[Card] = field(default_factory=lambda: DECK.copy())
    lead_player: Optional[Player] = None
    players: List[Player] = field(default_factory=default_players)
    played_cards: List[Card] = field(default_factory=list)

    def passing_order(self) -> PassingOrder:
        return passing_orders[self.round - 1 % 4]

    def new_deck(self) -> "Game":
        self.deck = DECK.copy()

        return self

    def shuffle(self) -> "Game":
        shuffle(self.deck)

        return self

    def shuffle_players(self) -> "Game":
        shuffle(self.players)

        return self

    def player_connected_count(self) -> int:
        return len([True for player in self.players if player.connected])

    def get_open_seat(self) -> Optional[Player]:
        for player in self.players:
            if not player.connected:
                return player

        return None

    def reset(self) -> "Game":
        self.round = 0
        self.lead_player = None
        self.new_deck().shuffle().shuffle_players()
        for player in self.players:
            player.hand = []
            player.scores = []

        return self

    def deal(self) -> "Game":
        for i in range(0, len(self.deck)):
            player_index = i % 4
            card = self.deck.pop()

            if card is TWO_OF_CLUBS:
                self.lead_player = self.players[player_index]

            self.players[player_index].hand.append(card)

        return self

    def score_round(self) -> "Game":
        scores = [player.score_round() for player in self.players]
        if 26 in scores:
            for i in range(4):
                self.players[i].scores.append(26 - scores[i])
        else:
            for i in range(4):
                self.players[i].scores.append(scores[i])

        return self

    def end_round(self) -> "Game":
        return self

    def next_round(self) -> "Game":
        self.round += 1
        self.new_deck().shuffle()
        for player in self.players:
            player.hand = []
        self.deal()

        return self


ArgsType = Dict[str, object]


@dataclass_json
@dataclass
class Message:
    command: str
    args: ArgsType = field(default_factory=dict)
