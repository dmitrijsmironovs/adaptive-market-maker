from dataclasses import dataclass, field

@dataclass
class Portfolio:
    cash: float = 0.0 #liquid cash available for trading
    inventory: int = 0 #current net asset position (positive for long, negative for short)
    filled_quantity: int = 0 #total quantity of orders that have been filled (executed) so far

    def on_buy(self, price: float, quantity: int) -> None: #updates portfolio state when a buy order is filled
        self.cash -= price * quantity 
        self.inventory += quantity
        self.filled_quantity += quantity

    def on_sell(self, price: float, quantity: int) -> None: #updates portfolio state when a sell order is filled
        self.cash += price * quantity
        self.inventory -= quantity
        self.filled_quantity += quantity

    def equity(self, mark_price: float) -> float:
        return self.cash + self.inventory * mark_price