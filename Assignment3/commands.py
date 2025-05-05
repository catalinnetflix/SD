import uuid
from typing import Optional
from events import *
from domain import OrderBook
from account import Account
from event_store import EventStore


class CommandHandler:
    def __init__(self, event_store: EventStore, order_book: OrderBook, account: Account):
        self.event_store = event_store
        self.order_book = order_book
        self.account = account

    def credit_funds(self, user_id: str, amount: float) -> None:
        event = FundsCredited(user_id, amount)
        self.process_event(event)

    def debit_funds(self, user_id: str, amount: float) -> None:
        event = FundsDebited(user_id, amount)
        self.process_event(event)

    def credit_shares(self, user_id: str, share_name: str, quantity: float) -> None:
        event = SharesCredited(user_id, share_name, quantity)
        self.process_event(event)

    def debit_shares(self, user_id: str, share_name: str, quantity: float) -> None:
        event = SharesDebited(user_id, share_name, quantity)
        self.process_event(event)

    def place_order(self, user_id: str, side: Literal["buy", "sell"],
                    quantity: float, price: float, share_name: str) -> str:

        order_id = str(uuid.uuid4())

        if side == "buy":
            self.debit_funds(user_id, quantity * price)
        elif side == "sell":
            self.debit_shares(user_id, share_name, quantity)

        order_event = OrderPlaced(
            order_id=order_id,
            user_id=user_id,
            side=side,
            quantity=quantity,
            price=price,
            share_name=share_name
        )
        self.process_event(order_event)

        return order_id

    def execute_trade(self, buy_order_id: str, sell_order_id: str,
                      quantity: float, price: float, share_name: str) -> bool:
        buy_order = self.find_order(buy_order_id)
        sell_order = self.find_order(sell_order_id)

        if not buy_order or not sell_order:
            return False

        trade_event = TradeExecuted(
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
            quantity=quantity,
            price=price,
            share_name=share_name
        )
        self.process_event(trade_event)

        self.credit_funds(sell_order.user_id, quantity * price)

        self.credit_shares(buy_order.user_id, share_name, quantity)

        self._handle_partial_fill(buy_order, quantity)
        self._handle_partial_fill(sell_order, quantity)

        return True

    def _handle_partial_fill(self, order: OrderPlaced, executed_quantity: float) -> None:
        remaining = order.quantity - executed_quantity

        if remaining > 0:
            updated_order = OrderPlaced(
                order_id=order.order_id,
                user_id=order.user_id,
                side=order.side,
                quantity=remaining,
                price=order.price,
                share_name=order.share_name
            )
            self.process_event(updated_order)

            if order.side == "sell":
                self.credit_shares(order.user_id, order.share_name, remaining)
        else:
            cancel_event = OrderCancelled(
                order_id=order.order_id,
                user_id=order.user_id,
                side=order.side,
                quantity=order.quantity,
                price=order.price,
                share_name=order.share_name
            )
            self.order_book.apply(cancel_event)
            self.event_store.append(cancel_event)

            if order.side == "buy":
                self.credit_funds(order.user_id, abs(remaining) * order.price)

    def cancel_order(self, order_id: str) -> bool:
        order = self.find_order(order_id)
        if not order:
            return False

        cancel_event = OrderCancelled(
            order_id=order_id,
            user_id=order.user_id,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            share_name=order.share_name
        )

        self.order_book.apply(cancel_event)
        self.event_store.append(cancel_event)
        return True

    def process_event(self, event: Event) -> None:
        self.event_store.append(event)
        self.order_book.apply(event)
        self.account.apply(event)

    def find_order(self, order_id: str) -> Optional[OrderPlaced]:
        order = self.order_book.active_orders.get(order_id)
        if order:
            return order


        return next(
            (e for e in self.event_store.get_all_events()
             if isinstance(e, OrderPlaced) and e.order_id == order_id),
            None
        )
