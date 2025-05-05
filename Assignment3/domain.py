from collections import defaultdict
from events import *

class OrderBook:
    def __init__(self,event_store):
        self.buy_orders = defaultdict(list)
        self.sell_orders = defaultdict(list)
        self.active_orders = {}
        self.event_store = event_store

    def apply(self, event):
        if isinstance(event, OrderPlaced):
            self.active_orders[event.order_id] = event
            if event.side == "buy":
                self.buy_orders[event.share_name].append(event)
            else:
                self.sell_orders[event.share_name].append(event)
        elif isinstance(event, OrderCancelled):
            order = self.active_orders.pop(event.order_id, None)

            if order:
                if order.side == "buy":
                    self.buy_orders[order.share_name] = [
                        o for o in self.buy_orders[order.share_name] if o.order_id != event.order_id
                    ]
                    self.event_store.append(FundsCredited(
                        user_id=order.user_id,
                        amount=order.quantity * order.price
                    ))
                else:
                    self.sell_orders[order.share_name] = [
                        o for o in self.sell_orders[order.share_name] if o.order_id != event.order_id
                    ]
                    self.event_store.append(SharesCredited(
                        user_id=order.user_id,
                        share_name=order.share_name,
                        quantity=order.quantity
                    ))
            else:
                print(f"Order with ID {event.order_id} not found in active orders.")


        elif isinstance(event, TradeExecuted):
            self.active_orders.pop(event.buy_order_id, None)
            self.active_orders.pop(event.sell_order_id, None)




