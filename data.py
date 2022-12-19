import copy
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum
from random import shuffle
from typing import Dict, List, Optional


Suits = Enum("Suits", ["♠︎", "♥︎", "♦︎", "♣︎"])
Values = Enum(
    "Values", ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
)


@dataclass_json
@dataclass
class Card:
    value: Values
    suit: Suits

    def __repr__(self):
        return f"{self.value.name}{self.suit.name}"


@dataclass_json
@dataclass
class Deck:
    cards: List[Card]


DECK = Deck(cards=[Card(suit=suit, value=value) for suit in Suits for value in Values])


@dataclass_json
@dataclass
class Player:
    name: str
    hand: List[Card] = field(default_factory=list)


passing_orders = [
    [1, 2, 3, 0],
    [3, 0, 1, 2],
    [2, 3, 0, 1],
    None,
]
PassingOrder = Optional[List[int]]


@dataclass_json
@dataclass
class Game:
    round: int = 0
    deck: Deck = field(default_factory=lambda: copy.deepcopy(DECK))
    lead_player: Optional[Player] = None
    players: List[Player] = field(default_factory=list)

    def passing_order(self) -> PassingOrder:
        return passing_orders[self.round - 1 % 4]

    def new_deck(self) -> "Game":
        self.deck = copy.deepcopy(DECK)

        return self

    def shuffle(self) -> "Game":
        if self.deck is not None:
            shuffle(self.deck.cards)

        return self

    def shuffle_players(self) -> "Game":
        shuffle(self.players)

        return self

    def player_count(self) -> int:
        return len(self.players)

    def reset(self) -> "Game":
        self.round = 0
        self.lead_player = None
        self.new_deck().shuffle().shuffle_players()
        if self.players is not None:
            for player in self.players:
                player.hand = None

        return self


@dataclass_json
@dataclass
class Message:
    command: str
    args: Dict[str, object] = field(default_factory=dict)
