import pricing_engine

metrics = pricing_engine.calculate_black_scholes(
    S=150.0, K=155.0, T=30/365.0, r=0.05, sigma=0.20, type=pricing_engine.OptionType.Call
)
print(metrics)
print(f"Price: {metrics.price:.4f}, Delta: {metrics.delta:.4f}, Vega: {metrics.vega:.4f}")