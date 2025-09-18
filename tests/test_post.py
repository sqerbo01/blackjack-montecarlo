import pandas as pd
from app.post import summarize_results, filter_by_dealer

def test_summarize_results_basic():
    df = pd.DataFrame({"outcome":[1, -1, 0, 1, 1], "dealer_up_val":[10,10,10,10,10]})
    s = summarize_results(df)
    assert s["n"] == 5
    assert abs(s["ev"] - (1-1+0+1+1)/5) < 1e-9
    assert abs(s["p_win"] - 3/5) < 1e-9
    assert abs(s["p_push"] - 1/5) < 1e-9
    assert abs(s["p_lose"] - 1/5) < 1e-9

def test_filter_by_dealer():
    df = pd.DataFrame({"dealer_up_val":[10,11,10], "outcome":[1,0,-1]})
    out = filter_by_dealer(df, 10)
    assert len(out) == 2
    assert set(out["outcome"]) == {1, -1}
