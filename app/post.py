import pandas as pd

def summarize_results(df: pd.DataFrame) -> dict:
    # df must have a column 'outcome' with values +1, 0, -1 (and +1.5 if BJ 3:2)
    n = len(df)
    if n == 0:
        return {"n":0,"ev":0.0,"p_win":0.0,"p_push":0.0,"p_lose":0.0,"se":0.0}
    ev = df["outcome"].mean()
    p_win = (df["outcome"] > 0).mean()
    p_push = (df["outcome"] == 0).mean()
    p_lose = (df["outcome"] < 0).mean()
    # standard error of the mean for Monte Carlo
    se = df["outcome"].std(ddof=1) / (n ** 0.5) if n > 1 else 0.0
    return {"n":n, "ev":ev, "p_win":p_win, "p_push":p_push, "p_lose":p_lose, "se":se}

def filter_by_dealer(df: pd.DataFrame, dealer_up_val: int) -> pd.DataFrame:
    return df[df["dealer_up_val"] == dealer_up_val].copy()
