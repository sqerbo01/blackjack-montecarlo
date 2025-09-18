from pathlib import Path
import pandas as pd

CARD_MAP = {**{str(i): i for i in range(2, 10)}, "T":10, "J":10, "Q":10, "K":10, "A":11}

def parse_card(c) -> int:
    """
    Parse a card symbol or number to its blackjack value.
    Accepts: 'A','T','J','Q','K','2'..'9' or numeric like 2,3,...,10.
    """
    if isinstance(c, (int, float)):
        c = str(int(c))
    else:
        c = str(c).strip().upper()
    if c not in CARD_MAP:
        raise ValueError(f"Invalid card: {c}")
    return CARD_MAP[c]

def load_presets(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)  # columns: p1,p2,dealer_up
    required = {"p1", "p2", "dealer_up"}
    if not required.issubset(df.columns):
        raise ValueError("presets.csv must have columns p1,p2,dealer_up")
    for col in ["p1","p2","dealer_up"]:
        df[col + "_val"] = df[col].map(parse_card)
    return df

