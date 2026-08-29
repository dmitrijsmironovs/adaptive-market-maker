from collections import defaultdict
import logging
from mm.models import Order, OrderType, Trade
from mm.order_book import OrderBook, CrossingLimitOrder

logger = logging.getLogger(__name__)

class Exchange:
    def __init__(self, tick: float = 0.01): 
        self.book = OrderBook(tick) 
        self.trades: list[Trade] = [] 
        self.time = 0
        self._next_id = 1
        self._orders_by_trader = defaultdict(set) #dict mapping trader_id to set of active order_ids for that trader

    def submit(self, order: Order) -> list[Trade]:
        order.order_id = self._next_id #generates next unique order ID
        self._next_id += 1 #increments order ID counter
        order.timestamp = self.time #sets order timestamp to current exchange time
        if order.order_type is OrderType.MARKET: #if order is a market order, matches against book
            trades = self.book.match_market_order(order) #executes market order against resting liquidity
            self.trades.extend(trades) #appends executed trades to exchange trade history
            return trades #returns list of newly executed trades
        try: #if order is a limit order, attempts to place it on the book
            self.book.add_limit_order(order) #adds limit order to order book
            self._orders_by_trader[order.trader_id].add(order.order_id) #tracks active order under trader ID
        except CrossingLimitOrder as exc: #catches crossing limit order exception
            logger.warning("rejected crossing limit order at t=%s: %s", self.time, exc) #logs warning on rejected order
        return [] #returns empty trade list when order is placed or rejected

    def cancel_all(self, trader_id: str) -> int: #cancels all active limit orders belonging to a specific trader
        ids = list(self._orders_by_trader[trader_id]) #fetches list of active order IDs for trader
        cancelled = sum(1 for oid in ids if self.book.cancel(oid)) #sums count of successfully cancelled orders
        self._orders_by_trader[trader_id].clear() #clears active order tracker for trader
        return cancelled #returns count of cancelled orders

    def assert_invariants(self) -> None: #checks that order book remains uncrossed
        b, a = self.book.best_bid(), self.book.best_ask() #fetches current top of book prices
        if b is not None and a is not None: #if liquidity exists on both sides, checks spread
            assert b < a, f"crossed book: bid {b} >= ask {a}" #asserts best bid is strictly lower than best ask