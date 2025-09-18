# Blackjack EV — Monte Carlo (Streamlit + Docker)
![CI](https://github.com/<YOUR_USER>/<YOUR_REPO>/actions/workflows/ci.yml/badge.svg)

Estimate EV of a 2-card starting hand vs dealer upcard using Monte Carlo.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python -m streamlit run app/streamlit_app.py
