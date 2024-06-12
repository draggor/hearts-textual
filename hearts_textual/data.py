import copy
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from enum import Enum, StrEnum
from random import shuffle
from typing import Any, Dict, List, Optional, NewType

from rich.pretty import pprint

suit_order = ["♧", "♦︎", "♤", "♥︎"]
value_order = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

ArgsType = Dict[str, object]
ErrorType = NewType("ErrorType", str)


@dataclass_json
@dataclass
class Message:
    command: str
    args: ArgsType = field(default_factory=dict)


class Suits(StrEnum):
    CLUBS = "♧"
    DIAMONDS = "♦︎"
    SPADES = "♤"
    HEARTS = "♥︎"

    def __lt__(self, other: "Suits") -> bool:  # type: ignore[override]
        return suit_order.index(self).__lt__(suit_order.index(other))


suit_mapping = {
    "C": Suits.CLUBS,
    "♧": Suits.CLUBS,
    "D": Suits.DIAMONDS,
    "♢": Suits.DIAMONDS,
    "S": Suits.SPADES,
    "♤": Suits.SPADES,
    "H": Suits.HEARTS,
    "♡": Suits.HEARTS,
}


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

    def __lt__(self, other: "Values") -> bool:  # type: ignore[override]
        return value_order.index(self).__lt__(value_order.index(other))


@dataclass_json
@dataclass(order=True)
class Card:
    suit: Suits
    value: Values

    def __str__(self):
        return f"{self.value.value}{self.suit.value}"

    def __repr__(self):
        return f"{self.value.value}{self.suit.value}"


def parse_card(card: str) -> Card:
    value = [enum for enum in Values if enum.value == card[0]][0]
    return Card(value=value, suit=suit_mapping[card[1]])


DECK = [Card(suit=suit, value=value) for suit in Suits for value in Values]
TWO_OF_CLUBS = Card(value=Values.TWO, suit=Suits.CLUBS)
QUEEN_OF_SPADES = Card(value=Values.QUEEN, suit=Suits.SPADES)
HEART = Suits.HEARTS


@dataclass_json
@dataclass()
class Player:
    name: str
    connected: bool = False
    hand: List[Card] = field(default_factory=list)
    play: Optional[Card] = None
    pile: List[Card] = field(default_factory=list)
    scores: List[int] = field(default_factory=list)

    def __hash__(self) -> int:
        return f"{self.name}".__hash__()

    def score_round(self) -> int:
        hearts_score = len([card for card in self.pile if card.suit == HEART])
        queen_score = 13 if QUEEN_OF_SPADES in self.pile else 0

        return hearts_score + queen_score

    def score_total(self) -> int:
        total = 0

        for score in self.scores:
            total += score

            if total == 100:
                total -= 100

        return total

    def has_suit(self, suit: Suits) -> bool:
        cards_in_suit = [card for card in self.hand if card.suit == suit]

        return len(cards_in_suit) >= 1

    def suit_count(self, suit: Suits) -> int:
        cards_in_suit = [card for card in self.hand if card.suit == suit]

        return len(cards_in_suit)


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
    turn: int = 0
    started: bool = False
    ended: bool = False
    hearts_broken: bool = False
    deck: List[Card] = field(default_factory=lambda: DECK.copy())
    lead_player: Optional[int] = None
    players: List[Player] = field(default_factory=default_players)
    turn_order: List[int] = field(default_factory=list)
    played_cards: List[Card] = field(default_factory=list)
    summary: Dict[str, object] = field(default_factory=dict)

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
        self._new_and_reset()
        self.started = False
        for player in self.players:
            player.connected = False

        return self

    def _new_and_reset(self) -> "Game":
        self.round = 0
        self.turn = 0
        self.lead_player = None
        self.hearts_broken = False
        self.played_cards = []
        self.lead_player = None
        self.turn_order = []
        self.ended = False
        self.new_deck().shuffle().shuffle_players()
        self.summary = {}
        for player in self.players:
            player.hand = []
            player.scores = []

        return self

    def new_game(self) -> "Game":
        self._new_and_reset()
        self.started = True
        self.ended = False

        return self

    def deal(self) -> "Game":
        self.deck.reverse()
        for i in range(0, len(self.deck)):
            player_index = i % 4
            card = self.deck.pop()

            if card == TWO_OF_CLUBS:
                self.lead_player = player_index

            self.players[player_index].hand.append(card)

        for player in self.players:
            player.hand.sort()

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
        self.turn = 0
        self.new_deck().shuffle()
        for player in self.players:
            player.hand = []
            player.pile = []
        self.deal()
        self.turn_order = [0, 1, 2, 3]
        self.summary = {}

        return self

    def next_turn(self) -> "Game":
        self.turn += 1
        if self.turn > 1:
            self.lead_player = self.hand_winner()
            self.get_lead_player().pile.extend(self.played_cards)
            self.summary = {"last_hand": self.played_cards}
        self.played_cards = []

        index = 0
        if self.players is not None and self.lead_player is not None:
            index = self.lead_player
        self.turn_order = [(index + i) % 4 for i in range(4)]

        return self

    def _first_turn_check(self, card: Card, player: Player) -> Optional[ErrorType]:
        if (
            self.turn == 1
            and self.lead_player is not None
            and not self.is_lead_player(player)
        ):
            return ErrorType(
                f"Player {player.name} not allowed to play yet, must be {self.get_lead_player().name}!"
            )

        if card != TWO_OF_CLUBS:
            return ErrorType(f"Card {card} is invalid, must be {TWO_OF_CLUBS}")

        return None

    def is_lead_player(self, player: Player) -> bool:
        if self.lead_player is None:
            return False

        return player == self.players[self.lead_player]

    def get_lead_player(self) -> Player:
        if self.lead_player is None:
            raise Exception("Can't call get_lead_player() outside of a game")

        return self.players[self.lead_player]

    def hand_winner(self) -> int:
        pc = zip(self.played_cards, self.turn_order)
        cards_in_suit = [
            (card, pi) for card, pi in pc if card.suit == self.played_cards[0].suit
        ]
        cards_in_suit.sort()
        cards_in_suit.reverse()
        winning_card, player_index = cards_in_suit[0]
        return player_index

    def has_card(self, card: Card) -> Optional[Player]:
        for player in self.players:
            if card in player.hand:
                return player

        return None

    def play_card(self, card: Card, player: Player) -> "GameOrErrorType":
        current_player = self.players[self.turn_order[len(self.played_cards)]]
        if player != current_player:
            return ErrorType(
                f"It's not {player.name}'s turn!  It is {current_player.name}'s!"
            )

        if self.turn == 1 and len(self.played_cards) == 0:
            error_message = self._first_turn_check(card, player)
            if error_message is not None:
                return error_message

        if self.turn == 1 and len(self.played_cards) > 0:
            if card == QUEEN_OF_SPADES:
                return ErrorType(
                    "Card Q♤ is invalid, can't throw crap on the first turn!"
                )

        if (
            card.suit == HEART
            and not self.hearts_broken
            and len(player.hand) != player.suit_count(HEART)
        ):
            return ErrorType(f"Card {card} is invalid, hearts not broken!")

        if (
            len(self.played_cards) > 0
            and player.has_suit(self.played_cards[0].suit)
            and self.played_cards[0].suit != card.suit
        ):
            return ErrorType(
                f"Card {card} is invalid, must play a {self.played_cards[0].suit}!"
            )

        if card in player.hand:
            if card.suit == HEART:
                self.hearts_broken = True
            player.play = card
            player.hand.remove(card)
            self.played_cards.append(card)

            if len(self.played_cards) == 4 and self.turn <= 13:
                self.next_turn()
                if self.turn > 13:
                    self.score_round()
                    self.next_round()

                    for player in self.players:
                        if player.score_total() > 100:
                            self.ended = True

                    if not self.ended:
                        self.next_turn()

            return self

        return ErrorType(f"Card {card} not in Player {player.name}'s hand")

    def end_game(self) -> "Game":
        self.ended = True

        return self


GameOrErrorType = Game | ErrorType
