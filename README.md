# Blackjack EV — Monte Carlo (Streamlit + Docker)
![CI](https://github.com/sqerbo01/blackjack-montecarlo/actions/workflows/ci.yml/badge.svg)

Estimate the **expected value (EV)** of a 2-card starting hand in Blackjack versus a dealer upcard via Monte Carlo simulation.

## Features
- Streamlit UI: pick Player Card 1 & 2, Dealer upcard, #sims, decks, H17/S17, payout (3:2 or 6:5).
- Outputs: EV per 1-unit bet, 95% CI, Win/Push/Loss rates, and a small chart.
- Tested “data importing / filtering” functions (`app/io.py`, `app/post.py`) + full CI.

---

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pytest -q
python -m streamlit run app/streamlit_app.py
