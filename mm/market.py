import numpy as np 

class Market: #generates a seeded random walk of prices, with a given volatility regime
    def __init__(self, initial_price=100.0, 
                 n_steps=10_000,
                 regime="normal", seed=0):
        sigmas = {"low": 0.01, "normal": 0.03, "high": 0.08} #volatility regimes given as standard deviation of price shocks
        self.sigma = sigmas[regime]
        self.regime = regime
        self.price = float(initial_price)
        self.n_steps = n_steps
        self.rng = np.random.default_rng(seed)
        self.history = [self.price]

    def draw_shock(self) -> float: #generates a random price shock from a normal distribution of given standard deviation
        return float(self.rng.normal(0.0, self.sigma)) 

    def apply_shock(self, shock: float) -> None: #applies the price shock to the current price
        self.price = max(0.01, self.price + shock) #price cannot go below 0.01 to avoid negative prices
        self.history.append(self.price) #new price is appended to the history of prices