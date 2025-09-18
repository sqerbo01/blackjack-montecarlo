from app.sim import RulesConfig, PolicyConfig, simulate_ev

def test_simulate_ev_runs_and_shapes():
    rules = RulesConfig(n_decks=1, dealer_hits_soft_17=True, blackjack_payout="3:2")
    policy = PolicyConfig(kind="baseline")
    ev, se, stats = simulate_ev(p1=11, p2=10, dealer_up=6, n_sims=2000, rules=rules, policy=policy, seed=123)
    assert isinstance(ev, float)
    assert isinstance(se, float)
    assert stats["n"] == 2000
    assert "wins" in stats and "losses" in stats and "pushes" in stats and "outcomes" in stats

def test_ev_reasonable_boundaries():
    # Player 11+10 (A,T) vs dealer 6 should be ≥ 0 on average (good spot)
    rules = RulesConfig(n_decks=1, dealer_hits_soft_17=True, blackjack_payout="3:2")
    policy = PolicyConfig(kind="baseline")
    ev, se, _ = simulate_ev(11, 10, 6, n_sims=2000, rules=rules, policy=policy, seed=1)
    assert ev > -0.2 and ev < 2.0  # loose sanity bounds

def test_blackjack_bonus_applies():
    # With natural blackjack, EV should reflect 3:2 bonus on average (unless dealer also has BJ)
    rules = RulesConfig(n_decks=1, dealer_hits_soft_17=True, blackjack_payout="3:2")
    policy = PolicyConfig(kind="baseline")
    ev, se, _ = simulate_ev(11, 10, 5, n_sims=2000, rules=rules, policy=policy, seed=7)
    assert ev > 0.2  # loose positive bound due to BJ bonus
