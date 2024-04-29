#!/usr/bin/env python3

from bots import OneCardBot, MultiCardBot
from pyminion.bots.examples import BigMoney
from pyminion.core import Card
from pyminion.expansions.base import (
    base_set,
    silver,
    gold,
    chapel,
    village,
    witch,
)
from pyminion.expansions.intrigue import intrigue_set
from pyminion.expansions.seaside import seaside_set
from pyminion.game import Game
from pyminion.human import Human
from pyminion.player import Player

def main() -> None:
    players: list[Player] = []

    one_card_bot = OneCardBot(witch)
    players.append(one_card_bot)

    card_counts: list[tuple[int, Card]] = [
        (2, silver),
        (1, chapel),
        (2, village),
        (2, witch),
    ]
    multi_card_bot = MultiCardBot(card_counts)
    players.append(multi_card_bot)

    kingdom_cards: list[Card] = [
        chapel,
        village,
        witch,
    ]

    game = Game(
        players=players,
        expansions=[
            base_set,
            intrigue_set,
            seaside_set,
        ],
        kingdom_cards=kingdom_cards,
        log_stdout=True,
        log_file=True,
    )

    game.play()

if __name__ == '__main__':
    main()
