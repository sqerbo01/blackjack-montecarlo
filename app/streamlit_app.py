import streamlit as st
import pandas as pd
# --- keep these as the first lines ---

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]  # /app
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# -------------------------------------

from app.sim import simulate_ev, RulesConfig, PolicyConfig
from app.io import parse_card

st.set_page_config(page_title="Blackjack EV Monte Carlo", page_icon="🃏", layout="wide")
st.title("🃏 Blackjack EV — Monte Carlo Simulator")

# --- Controls (sidebar) ---
with st.sidebar:
    st.header("Settings")

    # Card choices shown as symbols; we convert with parse_card()
    cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

    c1 = st.selectbox("Player card 1", cards, index=0)
    c2 = st.selectbox("Player card 2", cards, index=4)  # default "T"
    dealer_up = st.selectbox("Dealer upcard", cards, index=5)  # default "9"

    n_sims = st.slider("Number of simulations", min_value=1_000, max_value=200_000, step=1_000, value=20_000)
    n_decks = st.selectbox("Number of decks", [1, 6, 8], index=1)
    h17 = st.checkbox("Dealer hits soft 17 (H17)", value=True)
    payout = st.selectbox("Blackjack payout", ["3:2", "6:5"], index=0)
    seed = st.number_input("Random seed (optional, -1 to disable)", value=42, step=1)

    st.caption("Tip: increase simulations for tighter confidence intervals (slower).")

# Convert UI selections to numeric values expected by the engine
p1_val = parse_card(c1)
p2_val = parse_card(c2)
dealer_up_val = parse_card(dealer_up)

rules = RulesConfig(n_decks=int(n_decks), dealer_hits_soft_17=bool(h17), blackjack_payout=payout)
policy = PolicyConfig(kind="baseline")

left, mid, right = st.columns([1.2, 1, 1])

if st.button("▶️ Run Simulation", type="primary"):
    with st.spinner("Simulating..."):
        use_seed = None if int(seed) < 0 else int(seed)
        ev, se, stats = simulate_ev(
            p1=p1_val, p2=p2_val, dealer_up=dealer_up_val,
            n_sims=int(n_sims),
            rules=rules, policy=policy, seed=use_seed
        )

    # Metrics
    ci_low = ev - 1.96 * se
    ci_high = ev + 1.96 * se

    with left:
        st.subheader("Results")
        st.metric("EV (per 1 unit bet)", f"{ev:.4f}")
        st.write(f"95% CI: **[{ci_low:.4f}, {ci_high:.4f}]**")
        st.write(f"Simulations: **{stats['n']}**")

    with mid:
        st.subheader("Win / Push / Loss")
        counts = pd.DataFrame(
            {
                "count": [stats["wins"], stats["pushes"], stats["losses"]],
                "rate": [
                    stats["wins"] / stats["n"],
                    stats["pushes"] / stats["n"],
                    stats["losses"] / stats["n"],
                ],
            },
            index=["Win", "Push", "Loss"],
        )
        st.dataframe(counts.style.format({"count": "{:,.0f}", "rate": "{:.2%}"}), use_container_width=True)

    with right:
        st.subheader("Outcome distribution")
        # quick bar chart using rates
        chart_df = counts[["rate"]].rename(columns={"rate": "Rate"})
        st.bar_chart(chart_df)

    # Assumptions
    with st.expander("Assumptions & Notes"):
        st.markdown(
            """
            - Player policy: **baseline** — hit until hard 17+ (soft 17 hits).
            - Dealer rules: **H17** toggle controls whether dealer hits soft 17.
            - Blackjack payout configurable (**3:2** or **6:5**).
            - No doubles/splits/surrender (keeps scope focused for the assignment).
            - Each simulation draws from a freshly shuffled shoe of the selected number of decks.
            """
        )

# Optional: show preset scenarios if a CSV is present (demonstrates your I/O functions for the assignment)
with st.expander("Load example scenarios (presets.csv)"):
    st.caption("This is optional and only here to showcase 'data importing' functions for testing.")
    if st.button("Load presets from data/presets.csv"):
        try:
            from app.io import load_presets
            df = load_presets("data/presets.csv")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load presets: {e}")
