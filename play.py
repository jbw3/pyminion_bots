#!/usr/bin/env python3

from pyminion.bots.examples import BigMoney
from pyminion.core import Card
from pyminion.expansions.base import base_set, witch
from pyminion.expansions.intrigue import intrigue_set
from pyminion.expansions.seaside import seaside_set
from pyminion.game import Game
from pyminion.human import Human
from pyminion.player import Player

def main() -> None:
    players: list[Player] = [
        BigMoney(),
        Human(),
    ]

    kingdom_cards: list[Card] = [
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
