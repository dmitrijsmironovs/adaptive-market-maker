from mm.order_book import round_to_tick

class Strategy: #defines abstract base strategy interface for all market makers
    name = "base"
    def observe(self, fair_price: float) -> None: #abstract method signature for strategy observation of fair price
        pass
    def quote(self, fair_price: float, inventory: int) -> tuple[float, float]: #abstract method signature for strategy quotes
        raise NotImplementedError #forces concrete child strategy classes to implement quote generation

class FixedSpreadStrategy(Strategy): #models baseline market maker quoting static half-spread
    name = "fixed" #stores strategy identifier string
    def __init__(self, half_spread=0.05, tick=0.01): #initializes fixed spread parameters
        self.half_spread = half_spread #stores fixed distance from fair price to quote levels
        self.tick = tick #stores minimum price increment for tick rounding
    def quote(self, fair_price, inventory): #generates bid and ask limit prices around fair price
        bid = round_to_tick(fair_price - self.half_spread, self.tick) #rounds bid down/to tick below fair price
        ask = round_to_tick(fair_price + self.half_spread, self.tick) #rounds ask up/to tick above fair price
        return bid, ask #returns bid and ask target price tuple