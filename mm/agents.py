import numpy as np
from mm.models import Order, OrderType, Side

class NoiseTrader: #background trading agent that submits random market orders
    def __init__(self, trader_id="noise", arrival_prob=0.6, max_size=5, rng=None):
        self.trader_id = trader_id #unique identifier for the noise trader instance
        self.arrival_prob = arrival_prob #probability that the trader submits an order on any given step
        self.max_size = max_size #upper bound for the randomized order quantity
        self.rng = rng or np.random.default_rng(0) #instantiates seeded random generator if none is provided

    def act(self) -> list[Order]: #determines whether the trader acts this step and returns a list with new marker order or empty list
        if self.rng.random() > self.arrival_prob: #if (not probability of arrival), the trader does not act
            return []
        side = Side.BUY if self.rng.random() < 0.5 else Side.SELL #randomly selects BUY or SELL side with 50/50 probability
        size = int(self.rng.integers(1, self.max_size + 1)) #draws a random integer order size between 1 and max_size inclusive
        return [Order(self.trader_id, side, OrderType.MARKET, size)] #instantiates and returns a single market order inside a list
