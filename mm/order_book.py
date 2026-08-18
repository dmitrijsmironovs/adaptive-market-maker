from collections import deque #for orders at a price level
from mm.models import Side, OrderType, Order, Trade 

TICK = 0.01 #minimum price increment for the order book

def round_to_tick(price: float, tick: float = TICK) -> float: #rounds price to nearest tick size, default is TICK
    return round(round(price / tick) * tick, 10) #2 roundings to avoid float precision issues

class CrossingLimitOrder(Exception): #exception for crossing limit orders, must be a market order instead
    pass

class OrderBook:
    def __init__(self, tick: float = TICK):
        self.tick = tick
        self.bids: dict[float, deque] = {} # price -> deque of buy orders
        self.asks: dict[float, deque] = {} # price -> deque of sell orders
        self._index: dict[int, tuple] = {} # order_id -> (price, side) for fast lookup of orders by id

    def best_bid(self): #returns the highest bid price in order book, or None if there are no bids
        return max(self.bids) if self.bids else None

    def best_ask(self): #returns the lowest ask price in order book, or None if there are no asks
        return min(self.asks) if self.asks else None

    def mid(self): #returns midpoint price between best bid and best ask, or None if either side is empty
        b, a = self.best_bid(), self.best_ask()
        return None if b is None or a is None else (b + a) / 2

    def spread(self): #returns the spread between best ask and best bid, or None if either side is empty
        b, a = self.best_bid(), self.best_ask()
        return None if b is None or a is None else a - b

    def add_limit_order(self, order: Order) -> None: #adds limit order to order book
        price = round_to_tick(order.price, self.tick) #ensure price is rounded to nearest tick
        if order.side is Side.BUY:
            if self.best_ask() is not None and price >= self.best_ask(): 
                raise CrossingLimitOrder(f"buy limit {price} crosses ask {self.best_ask()}") #crossing limit orders not allowed
            book = self.bids
        else:
            if self.best_bid() is not None and price <= self.best_bid():
                raise CrossingLimitOrder(f"sell limit {price} crosses bid {self.best_bid()}")
            book = self.asks
        order.price = price #update order price to rounded tick
        book.setdefault(price, deque()).append(order) #add order to the appropriate price level
        self._index[order.order_id] = (order.side, price, order) #adds order to index dictionary for fast lookup by order_id

    def match_market_order(self, order: Order) -> list[Trade]: #executes market order against order book, returns list of trades
        trades: list[Trade] = [] #list of executed trades
        remaining = order.quantity #still unfulfilled quantity of the market order
        buying = order.side is Side.BUY #boolean indicating if the market order is a buy or sell
        while remaining > 0: #if there is still quantity left to fill
            book = self.asks if buying else self.bids #selects the opposite side of the book to match against
            if not book: #if book is empty, no liquidity left to fill the market order
                break
            price = min(book) if buying else max(book) #gets the best price on the opposite side of the book
            level = book[price] #gets deque of resting orders at that price level
            while remaining > 0 and level: #consumes orders at that price level until either the market order is filled or there are no more resting orders
                resting = level[0] #gets the first resting order in the deque
                qty = min(remaining, resting.quantity) #determines trade quantity
                resting.quantity -= qty #reduces resting order quantity by the filled amount
                remaining -= qty #reduces market order remaining quantity by the filled amount
                trades.append(Trade( #adds trade to the list of executed trades
                    price=price,
                    quantity=qty,
                    buyer_id=order.trader_id if buying else resting.trader_id,
                    seller_id=resting.trader_id if buying else order.trader_id,
                    aggressor_side=order.side,
                    timestamp=order.timestamp,
                ))
                if resting.quantity == 0: #if the resting order is fully filled, removes it from the deque and index
                    level.popleft()
                    self._index.pop(resting.order_id, None)
            if not level: #if the price level is empty, removes it from the book
                del book[price]
        return trades
    
import logging
logger = logging.getLogger(__name__)
        


