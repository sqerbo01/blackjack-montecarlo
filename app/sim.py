import random
from dataclasses import dataclass
from typing import List, Literal, Tuple

from .rules import hand_value, is_blackjack

CardVal = int  # Ace=11; T/J/Q/K=10; 2..9 as themselves


@dataclass
class RulesConfig:
    n_decks: int = 6
    dealer_hits_soft_17: bool = True  # H17=True, S17=False
    blackjack_payout: Literal["3:2", "6:5"] = "3:2"


@dataclass
class PolicyConfig:
    kind: Literal["baseline"] = "baseline"  # hit until hard 17+ (soft 17 hits)


def fresh_shoe(n_decks: int) -> List[CardVal]:
    deck: List[CardVal] = []
    for _ in range(n_decks):
        deck += [11] * 4  # A
        deck += [10] * 16  # T,J,Q,K
        deck += [9] * 4 + [8] * 4 + [7] * 4 + [6] * 4 + [5] * 4 + [4] * 4 + [3] * 4 + [2] * 4
    random.shuffle(deck)
    return deck


def draw(shoe: List[CardVal]) -> CardVal:
    if not shoe:
        raise RuntimeError("Shoe is empty.")
    return shoe.pop()


def play_player(player: List[CardVal], dealer_up: CardVal, policy: PolicyConfig, shoe: List[CardVal]) -> List[CardVal]:
    # baseline policy: stop on hard 17+; soft 17 hits
    while True:
        total, is_soft = hand_value(player)
        if total > 21:
            return player
        if total > 17:
            return player
        if total == 17 and not is_soft:
            return player
        player.append(draw(shoe))


def play_dealer(dealer_cards: List[CardVal], rules: RulesConfig, shoe: List[CardVal]) -> List[CardVal]:
    while True:
        total, is_soft = hand_value(dealer_cards)
        if total > 21:
            return dealer_cards
        if total > 17:
            return dealer_cards
        if total == 17:
            if rules.dealer_hits_soft_17 and is_soft:
                dealer_cards.append(draw(shoe))
                continue
            return dealer_cards
        dealer_cards.append(draw(shoe))


def resolve_outcome(
    player_final: List[CardVal],
    dealer_final: List[CardVal],
    rules: RulesConfig,
    is_initial: bool,
    player_initial: List[CardVal],
) -> float:
    p_total, _ = hand_value(player_final)
    d_total, _ = hand_value(dealer_final)

    # natural blackjack bonus
    if is_initial and len(player_initial) == 2 and is_blackjack(player_initial):
        if len(dealer_final) == 2 and is_blackjack(dealer_final):
            return 0.0
        return 1.5 if rules.blackjack_payout == "3:2" else 1.2

    if p_total > 21:
        return -1.0
    if d_total > 21:
        return 1.0
    if p_total > d_total:
        return 1.0
    if p_total < d_total:
        return -1.0
    return 0.0


def simulate_once(
    p1: CardVal, p2: CardVal, dealer_up: CardVal, rules: RulesConfig, policy: PolicyConfig, shoe: List[CardVal]
) -> float:
    player = [p1, p2]
    dealer = [dealer_up, draw(shoe)]

    if is_blackjack(player):
        return resolve_outcome(player, dealer, rules, is_initial=True, player_initial=player)

    player = play_player(player, dealer_up, policy, shoe)

    if hand_value(player)[0] <= 21:
        dealer = play_dealer(dealer, rules, shoe)

    return resolve_outcome(player, dealer, rules, is_initial=False, player_initial=player)


def simulate_ev(
    p1: CardVal,
    p2: CardVal,
    dealer_up: CardVal,
    n_sims: int,
    rules: RulesConfig | None = None,
    policy: PolicyConfig | None = None,
    seed: int | None = 42,
) -> Tuple[float, float, dict]:
    rules = rules or RulesConfig()
    policy = policy or PolicyConfig()
    if seed is not None:
        random.seed(seed)

    outcomes: List[float] = []
    for _ in range(n_sims):
        shoe = fresh_shoe(rules.n_decks)
        outcomes.append(simulate_once(p1, p2, dealer_up, rules, policy, shoe))

    n = len(outcomes)
    ev = sum(outcomes) / n if n else 0.0
    if n > 1:
        mean = ev
        var = sum((x - mean) ** 2 for x in outcomes) / (n - 1)
        se = (var ** 0.5) / (n ** 0.5)
    else:
        se = 0.0

    stats = {
        "n": n,
        "wins": sum(1 for x in outcomes if x > 0),
        "pushes": sum(1 for x in outcomes if x == 0),
        "losses": sum(1 for x in outcomes if x < 0),
        "outcomes": outcomes,
    }
    return ev, se, stats
