import logging #to record warnings
from typing import List, Dict, Set, Optional 
from mm.models import Order, Trade, OrderType, Side 
from mm.order_book import OrderBook, CrossingLimitOrder

logger = logging.getLogger(__name__)

class Exchange:
    def __init__(self, book: OrderBook): #initializes the exchange with an order book
        self.book = book
        self._next_id: int = 1 #counter for generating unique order IDs
        self.timestamp: int = 0 #counter for tracking time steps in the simulation
        self.trades: List[Trade] = [] #list of executed trades
        self._trader_orders: Dict[str, Set[int]] = {} #dictionary mapping trader IDs to sets of their active order IDs

    def submit_order(
        self,
        trader_id: str,
        order_type: OrderType,
        side: Side,
        quantity: int,
        price: Optional[float] = None
    ) -> List[Trade]:
        order_id = self._next_id #generates the next unique order ID
        self._next_id += 1 #increments the order ID counter
        order = Order( #instantiates a new Order object with the provided parameters
            order_id=order_id,
            trader_id=trader_id,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        new_trades: List[Trade] = [] #list of newly executed trades resulting from this order submission
        if order_type is OrderType.LIMIT: #if the order is a limit order, attempts to add it to the order book
            try:
                self.book.add_limit_order(order)
                self._trader_orders.setdefault(trader_id, set()).add(order_id) #adds the order ID to the trader's set of active orders
            except CrossingLimitOrder as e: #if the limit order crosses the book, logs a warning and raises the exception
                logger.warning(f"Crossing limit order dropped for {trader_id}: {e}")
        elif order_type is OrderType.MARKET: #if the order is a market order, attempts to match it against the order book
            new_trades = self.book.execute_market_order(order) #executes the market order and returns a list of trades
            self.trades.extend(new_trades) #adds the new trades to the exchange's list
        return new_trades
    
    def cancel_order(self, order_id: int) -> bool: #cancels a specific order by its ID, returns True if successful, False if the order was not found
        return self.book.cancel(order_id)

    def cancel_all(self, trader_id: str) -> None: #cancels all active orders for a specific trader by their ID
        order_ids = self._trader_orders.get(trader_id, set()).copy()
        for order_id in order_ids:
            if self.book.cancel(order_id):
                self._trader_orders[trader_id].remove(order_id)

    def assert_invariants(self) -> None: #checks that the order book is in a valid state, raises an AssertionError if any invariant is violated
        best_bid = self.book.best_bid()
        best_ask = self.book.best_ask()
        if best_bid is not None and best_ask is not None:
            assert best_bid < best_ask, f"Crossed book: best_bid ({best_bid}) >= best_ask ({best_ask})"