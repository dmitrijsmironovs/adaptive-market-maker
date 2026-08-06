from dataclasses import dataclass #autogenerates __init__
from enum import Enum #fixed name choices

#define order side with enum 
class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

#define order type with enum
class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

@dataclass
class Order:
    trader_id: str #"mm", "noise", "informed"
    side: Side 
    order_type: OrderType
    quantity: int #number of units to buy/sell
    price: float | None = None #specified for limit orders, None for market orders

    #blank for new orders, assigned by exchange
    order_id: int | None = None 
    timestamp: int | None = None

    #runs automatically after dataclass builds object, validates attributes
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_type is OrderType.LIMIT and self.price is None:
            raise ValueError("limit orders need a price")
        if self.order_type is OrderType.MARKET and self.price is not None:
            raise ValueError("market orders must not carry a price")

    @dataclass
    class Trade: #match between two orders, executed by exchange
        price: float 
        quantity: int
        buyer_id: str #trader_id of the buyer
        seller_id: str #trader_id of the seller
        aggressor_side: Side #which side's market order triggered the resting limit order
        timestamp: int

    @dataclass
    class Quote: #a snapshot of the current best bid and ask prices and sizes by market maker
        bid_price: float | None #current highest bid price, None if no bids
        ask_price: float | None #current lowest ask price, None if no asks
        size: int
        timestamp: int







