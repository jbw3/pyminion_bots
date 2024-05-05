#!/usr/bin/env python3

from bots import MultiCardBot
from pyminion.bots.examples import BigMoney
from pyminion.core import Card
from pyminion.expansions.base import base_set
from pyminion.expansions.intrigue import intrigue_set, replace
from pyminion.expansions.seaside import seaside_set
from pyminion.game import Game
from pyminion.player import Player
from pyminion.simulator import Simulator
import random
import sys

def main() -> None:
    argv_len = len(sys.argv)
    if argv_len < 2:
        print('Error: No crash log given', file=sys.stderr)
        sys.exit(1)
    elif argv_len > 2:
        print('Error: Too many arguments', file=sys.stderr)
        sys.exit(1)

    crash_log = sys.argv[1]
    seed = -1
    iteration = -1
    card_counts: list[tuple[int, Card]] = []
    with open(crash_log, 'r') as f:
        for line in f:
            if line.startswith('Traceback'):
                break
            split = line.split('=')
            if split[0] == 'seed':
                seed = int(split[1])
            elif split[0] == 'iterations':
                iteration = int(split[1])

    random.seed(seed)

    card_counts.append((10, replace))

    card_bot = MultiCardBot(card_counts)
    big_money_bot = BigMoney()
    players: list[Player] = [
        card_bot,
        big_money_bot,
    ]

    expansions = [base_set, intrigue_set, seaside_set]
    kingdom_cards = [card for _, card in card_counts]
    game = Game(
        players,
        expansions,
        kingdom_cards,
        log_stdout=False,
        log_file=True,
        log_file_name='replay_crash.log',
    )

    sim = Simulator(game, iterations=iteration)
    sim.run()

if __name__ == '__main__':
    main()
