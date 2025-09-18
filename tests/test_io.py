import pandas as pd
from app.io import parse_card, load_presets

def test_parse_card():
    assert parse_card("A") == 11
    assert parse_card("T") == 10
    assert parse_card("7") == 7

def test_load_presets(tmp_path):
    p = tmp_path / "presets.csv"
    pd.DataFrame([{"p1":"A","p2":"9","dealer_up":"6"}]).to_csv(p, index=False)
    df = load_presets(p)
    assert {"p1_val","p2_val","dealer_up_val"}.issubset(df.columns)
    assert df.loc[0,"p1_val"] == 11
