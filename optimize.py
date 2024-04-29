#!/usr/bin/env python3

from bots import OneCardBot
from pyminion.bots.examples import BigMoney
from pyminion.core import Card
from pyminion.expansions.base import base_set, chapel, market, village
from pyminion.expansions.intrigue import intrigue_set
from pyminion.expansions.seaside import seaside_set
from pyminion.game import Game
from pyminion.player import Player
from pyminion.simulator import Simulator
import sys
from typing import Iterable

def rank_cards(cards: Iterable[Card], iterations: int) -> list[tuple[float, Card]]:
    ranked_cards: list[tuple[float, Card]] = []
    expansions = [base_set, intrigue_set, seaside_set]
    for card in cards:
        one_card_bot = OneCardBot(card)
        big_money_bot = BigMoney()
        players: list[Player] = [
            one_card_bot,
            big_money_bot,
        ]
        game = Game(
            players,
            expansions,
            kingdom_cards=[card],
            log_stdout=False,
            log_file=False,
        )
        sim = Simulator(game, iterations=iterations)
        result = sim.run()

        for player_result in result.player_results:
            if player_result.player is one_card_bot:
                score = player_result.wins / iterations
                ranked_cards.append((score, card))
                break

    ranked_cards.sort(key=lambda x: x[0], reverse=True)
    return ranked_cards

def main() -> None:
    if len(sys.argv) > 1:
        iterations = int(sys.argv[1])
    else:
        iterations = 100

    cards = base_set[:]
    ranked_cards = rank_cards(cards, iterations)
    for score, card in ranked_cards:
        print(f'{score:.1%}: {card.name}')

if __name__ == '__main__':
    main()
