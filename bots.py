import logging
from pyminion.bots.optimized_bot import OptimizedBot, OptimizedBotDecider
from pyminion.core import Card, CardType, DeckCounter, get_action_cards
from pyminion.expansions.base import (
    estate,
    duchy,
    province,
    copper,
    silver,
    gold,
)
from pyminion.expansions.alchemy import (
    potion,
)
from pyminion.game import Game
from pyminion.player import Player
from typing import Iterator

logger = logging.getLogger()

class OneCardBotDecider(OptimizedBotDecider):
    def __init__(self, card: Card):
        self.card = card

    def action_priority(self, player: "Player", game: "Game") -> Iterator[Card]:
        if CardType.Action in self.card.type:
            while player.state.actions > 0 and self.card in player.hand.cards:
                yield self.card

    def buy_priority(self, player: "Player", game: "Game") -> Iterator[Card]:
        counter = DeckCounter(player.get_all_cards())
        gold_count = counter[gold]
        silver_count = counter[silver]
        card_count = counter[self.card]

        province_cost = province.get_cost(player, game)
        gold_cost = gold.get_cost(player, game)
        silver_cost = silver.get_cost(player, game)
        card_cost = self.card.get_cost(player, game)

        money = player.state.money
        if money >= province_cost:
            yield province
        elif card_cost > gold_cost and money >= card_cost:
            yield self.card
        elif money >= gold_cost and (card_cost != gold_cost or gold_count <= card_count):
            yield gold
        elif card_cost > silver_cost and money >= card_cost:
            yield self.card
        elif money >= silver_cost and (card_cost != silver_cost or silver_count <= card_count):
            yield silver
        elif money >= card_cost:
            yield self.card

class OneCardBot(OptimizedBot):
    def __init__(self, card: Card, name: str = "One-Card Bot"):
        super().__init__(OneCardBotDecider(card), name)

class MultiCardBotDecider(OptimizedBotDecider):
    def __init__(self, card_counts: list[tuple[int, Card]]):
        self.card_counts = card_counts[:]
        self.greening = False

        card_names: set[str] = set(c.name for _, c in self.card_counts)
        if "Silver" not in card_names:
            self.card_counts.append((1, silver))
        if "Gold" not in card_names:
            self.card_counts.append((2, gold))
        if "Potion" not in card_names and any(c.base_cost.potions > 0 for _, c in self.card_counts):
            self.card_counts.append((1, potion))

    def action_priority(self, player: "Player", game: "Game") -> Iterator[Card]:
        while player.state.actions > 0:
            actions = list(get_action_cards(player.hand.cards))
            if len(actions) == 0:
                break

            actions.sort(key=lambda c: (c.actions, c.get_cost(player, game)), reverse=True)
            logger.info(f"Prioritized actions: {actions}")
            yield actions[0]

    def buy_priority(self, player: "Player", game: "Game") -> Iterator[Card]:
        while player.state.buys > 0:
            buy_cards: list[tuple[float, Card]] = []
            counter = DeckCounter(player.get_all_cards())

            if not self.greening:
                province_start_count = province.get_pile_starting_count(game)
                if game.supply.pile_length("Province") < province_start_count:
                    logger.info("Greening!")
                    self.greening = True

            if not self.greening:
                for target_count, card in self.card_counts:
                    current_count = counter[card]
                    if current_count / target_count < 0.9:
                        break
                else:
                    logger.info("Greening!")
                    self.greening = True

            if self.greening:
                num_provinces = game.supply.pile_length("Province")
                num_duchies = game.supply.pile_length("Duchy")
                num_estates = game.supply.pile_length("Estate")
                if num_provinces > 0 and province.get_cost(player, game) <= player.state.money:
                    buy_cards.append((100, province))
                if num_duchies > 0 and num_provinces <= 2 and duchy.get_cost(player, game) <= player.state.money:
                    buy_cards.append((90, duchy))
                if num_estates > 0 and num_provinces == 0 and estate.get_cost(player, game) <= player.state.money:
                    buy_cards.append((80, estate))

            available_card_names: set[str] = set(c.name for c in game.supply.available_cards())
            for target_count, card in self.card_counts:
                current_count = counter[card]
                cost = card.get_cost(player, game)
                if current_count < target_count and cost.money <= player.state.money and cost.potions <= player.state.potions and card.name in available_card_names:
                    priority = cost.money + (cost.potions * 2)
                    priority -= current_count / target_count
                    buy_cards.append((priority, card))

            if len(buy_cards) == 0:
                break

            buy_cards.sort(key=lambda x: x[0], reverse=True)
            logger.info(f"Prioritized buys: {buy_cards}")
            yield buy_cards[0][1]

class MultiCardBot(OptimizedBot):
    def __init__(self, card_counts: list[tuple[int, Card]], name: str = "Multi-Card Bot"):
        super().__init__(MultiCardBotDecider(card_counts), name)
