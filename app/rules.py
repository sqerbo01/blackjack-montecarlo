# Basic blackjack rules helpers: card parsing, hand value, and blackjack check.

CARD_MAP = {**{str(i): i for i in range(2, 10)}, "T": 10, "J": 10, "Q": 10, "K": 10, "A": 11}

def parse_card_symbol(sym: str) -> int:
    s = sym.strip().upper()
    if s not in CARD_MAP:
        raise ValueError(f"Invalid card symbol: {sym}")
    return CARD_MAP[s]

def hand_value(card_values: list[int]) -> tuple[int, bool]:
    """
    Compute best blackjack total and whether it's soft.
    Ace is represented as 11 in inputs. We can downgrade 11->1 by subtracting 10.
    """
    total = sum(card_values)
    aces_as_eleven = sum(1 for v in card_values if v == 11)

    # Convert some Aces from 11 to 1 until not busting or no Aces left to convert
    while total > 21 and aces_as_eleven > 0:
        total -= 10
        aces_as_eleven -= 1

    # If any Ace still counts as 11, the hand is soft
    is_soft = aces_as_eleven > 0
    return total, is_soft

def is_blackjack(card_values: list[int]) -> bool:
    if len(card_values) != 2:
        return False
    total, _ = hand_value(card_values)
    has_ace = 11 in card_values
    has_ten_value = any(v == 10 for v in card_values)
    return total == 21 and has_ace and has_ten_value

