#!/usr/bin/env python3

import argparse
from bots import OneCardBot
from pyminion.bots.examples import BigMoney
from pyminion.core import Card
from pyminion.expansions.base import base_set
from pyminion.expansions.intrigue import intrigue_set
from pyminion.expansions.seaside import seaside_set
from pyminion.game import Game
from pyminion.player import Player
from pyminion.simulator import Simulator, SimulatorResult
import random
import sys
import time
from typing import Iterable

def run_sim(players: list[Player], kingdom_cards: list[Card], iterations: int, seed: int) -> SimulatorResult:
    random.seed(seed)

    expansions = [base_set, intrigue_set, seaside_set]
    game = Game(
        players,
        expansions,
        kingdom_cards=kingdom_cards,
        log_stdout=False,
        log_file=False,
    )

    sim = Simulator(game, iterations=iterations)

    try:
        result = sim.run()
    except:
        print(f'seed={seed}, iterations={iterations}, kingdom={kingdom_cards}', file=sys.stderr)
        raise

    return result

def rank_cards(cards: Iterable[Card], iterations: int, seed: int) -> list[tuple[float, Card]]:
    ranked_cards: list[tuple[float, Card]] = []
    for card in cards:
        one_card_bot = OneCardBot(card)
        big_money_bot = BigMoney()
        players: list[Player] = [
            one_card_bot,
            big_money_bot,
        ]

        result = run_sim(players, [card], iterations, seed)

        for player_result in result.player_results:
            if player_result.player is one_card_bot:
                score = player_result.wins / iterations
                ranked_cards.append((score, card))
                break

    ranked_cards.sort(key=lambda x: x[0], reverse=True)
    return ranked_cards

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations', type=int, default=100, help='number of simulation iterations')
    parser.add_argument('-s', '--seed', type=int, help='random seed')

    args = parser.parse_args()
    return args

def main() -> None:
    args = parse_args()

    if args.seed is None:
        seed = time.time_ns() & 0xffff_ffff
    else:
        seed: int = args.seed

    cards = base_set + intrigue_set + seaside_set
    ranked_cards = rank_cards(cards, args.iterations, seed)
    for score, card in ranked_cards:
        print(f'{score:.1%}: {card.name}')

if __name__ == '__main__':
    main()
