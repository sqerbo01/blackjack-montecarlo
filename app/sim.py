import random
from dataclasses import dataclass
from typing import Literal, Tuple, List

from .rules import hand_value, is_blackjack

CardVal = int  # Ace as 11; 2..9 as 2..9; T/J/Q/K as 10

@dataclass
class RulesConfig:
    n_decks: int = 6
    dealer_hits_soft_17: bool = True  # H17=True, S17=False
    blackjack_payout: Literal["3:2", "6:5"] = "3:2"

@dataclass
class PolicyConfig:
    # baseline: player hits until HARD 17+ (soft 17 hits)
    kind: Literal["baseline"] = "baseline"

def fresh_shoe(n_decks: int) -> List[CardVal]:
    """Create a fresh shoe of n decks with card values (A as 11)."""
    single_deck = [11, 10, 10, 10, 10] + [9,8,7,6,5,4,3,2]  # simplified counts per rank not exact 4x each
    # Use exact counts: 4 of each rank per deck
    deck = []
    for _ in range(n_decks):
        deck += [11]*4  # A
        deck += [10]*16 # T,J,Q,K
        deck += [9]*4 + [8]*4 + [7]*4 + [6]*4 + [5]*4 + [4]*4 + [3]*4 + [2]*4
    random.shuffle(deck)
    return deck

def draw(shoe: List[CardVal]) -> CardVal:
    if not shoe:
        raise RuntimeError("Shoe is empty.")
    return shoe.pop()

def play_player(player: List[CardVal], dealer_up: CardVal, policy: PolicyConfig) -> List[CardVal]:
    """Baseline policy: hit until HARD 17+ (soft 17 hits)."""
    while True:
        total, is_soft = hand_value(player)
        if total > 21:
            return player
        # stop on hard 17+; if soft 17, keep hitting
        if total > 17:
            return player
        if total == 17 and not is_soft:
            return player
        # else hit
        # (we don't use dealer_up in this baseline policy, but keep signature for extensibility)
        player.append(draw._last_draw())  # placeholder; replaced below
        # (see patched version under)
    # unreachable

# We need a shoe-aware player play function; patching above:
def play_player(player: List[CardVal], dealer_up: CardVal, policy: PolicyConfig, shoe: List[CardVal]) -> List[CardVal]:  # type: ignore[func-override]
    while True:
        total, is_soft = hand_value(player)
        if total > 21:
            return player
        if total > 17:
            return player
        if total == 17 and not is_soft:
            return player
        player.append(draw(shoe))
    # unreachable

def play_dealer(dealer_cards: List[CardVal], rules: RulesConfig, shoe: List[CardVal]) -> List[CardVal]:
    """Dealer hits until 17+; hits soft 17 if rules.dealer_hits_soft_17."""
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
            else:
                return dealer_cards
        dealer_cards.append(draw(shoe))

def resolve_outcome(player_final: List[CardVal], dealer_final: List[CardVal], rules: RulesConfig, is_initial: bool, player_initial: List[CardVal]) -> float:
    """
    Returns outcome in units of initial bet:
    +1 (player win), -1 (player loss), 0 (push), +1.5 or +1.2 for natural blackjack depending on payout.
    """
    p_total, _ = hand_value(player_final)
    d_total, _ = hand_value(dealer_final)

    # natural blackjack handling
    if is_initial and len(player_initial) == 2 and is_blackjack(player_initial):
        # if dealer also has blackjack (only if dealer had 10/A upcard and natural), it's a push
        if len(dealer_final) == 2 and is_blackjack(dealer_final):
            return 0.0
        return 1.5 if rules.blackjack_payout == "3:2" else 1.2

    # busts
    if p_total > 21:
        return -1.0
    if d_total > 21:
        return 1.0

    # compare
    if p_total > d_total:
        return 1.0
    if p_total < d_total:
        return -1.0
    return 0.0

def simulate_once(p1: CardVal, p2: CardVal, dealer_up: CardVal, rules: RulesConfig, policy: PolicyConfig, shoe: List[CardVal]) -> float:
    """Simulate one round from a specific initial state; dealer hole and subsequent draws from shoe."""
    # deal initial
    player = [p1, p2]
    dealer = [dealer_up, draw(shoe)]

    # if player has natural blackjack, resolve immediately (unless dealer also has)
    is_initial = True
    if is_blackjack(player):
        # dealer peeks by playing to 2 cards (already 2); resolution will check dealer natural
        return resolve_outcome(player, dealer, rules, is_initial=True, player_initial=player)

    # player plays
    player = play_player(player, dealer_up, policy, shoe)
    is_initial = False

    # dealer plays if player not busted
    if hand_value(player)[0] <= 21:
        dealer = play_dealer(dealer, rules, shoe)

    # resolve
    return resolve_outcome(player, dealer, rules, is_initial=False, player_initial=player)

def simulate_ev(p1: CardVal, p2: CardVal, dealer_up: CardVal, n_sims: int, rules: RulesConfig | None = None, policy: PolicyConfig | None = None, seed: int | None = 42) -> Tuple[float, float, dict]:
    """
    Monte Carlo EV for a given 2-card player hand and dealer upcard.
    Returns (ev_mean, se_mean, stats_dict).
    """
    rules = rules or RulesConfig()
    policy = policy or PolicyConfig()
    if seed is not None:
        random.seed(seed)

    outcomes = []
    for _ in range(n_sims):
        shoe = fresh_shoe(rules.n_decks)
        # remove the known initial cards from the top by drawing until we match counts (simpler: just deal from shoe)
        # To avoid bias, just draw from the shoe normally; initial known cards are conceptual. Instead, prepend them:
        # We'll simulate by *pre-setting* player and dealer upcard and then drawing the rest from shoe.
        # That’s already accomplished by passing p1, p2, dealer_up, and drawing dealer hole from shoe.
        outcomes.append(simulate_once(p1, p2, dealer_up, rules, policy, shoe))

    # summary stats
    n = len(outcomes)
    ev = sum(outcomes) / n if n else 0.0
    # standard error
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
