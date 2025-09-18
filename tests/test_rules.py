import pytest
from app.rules import parse_card_symbol, hand_value, is_blackjack

def test_parse_card_symbol():
    assert parse_card_symbol("A") == 11
    assert parse_card_symbol("T") == 10
    assert parse_card_symbol("7") == 7
    with pytest.raises(ValueError):
        parse_card_symbol("Z")

def test_hand_value_hard_no_aces():
    total, is_soft = hand_value([10, 7])
    assert total == 17
    assert is_soft is False

def test_hand_value_soft_then_hard_after_hit():
    # A + 6 is soft 17
    total, is_soft = hand_value([11, 6])
    assert total == 17 and is_soft is True
    # Add a T (now should flip Ace to 1 → hard 17)
    total2, is_soft2 = hand_value([11, 6, 10])
    assert total2 == 17 and is_soft2 is False

def test_hand_value_multiple_aces():
    # A + A = soft 12 (11 + 1)
    total, is_soft = hand_value([11, 11])
    assert total == 12 and is_soft is True
    # A + A + 9 = 21 (11 + 1 + 9) still soft (one Ace as 11)
    total2, is_soft2 = hand_value([11, 11, 9])
    assert total2 == 21 and is_soft2 is True
    # Add a 9 → should become 20 hard
    total3, is_soft3 = hand_value([11, 11, 9, 9])
    assert total3 == 20 and is_soft3 is False

def test_is_blackjack_true_and_false():
    assert is_blackjack([11, 10]) is True      # A + T
    assert is_blackjack([10, 11]) is True
    assert is_blackjack([11, 9]) is False      # 20, not BJ
    assert is_blackjack([7, 7, 7]) is False    # not two-card
