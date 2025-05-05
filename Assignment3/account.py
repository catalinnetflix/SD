from collections import defaultdict
from events import *

class Account:
    def __init__(self):
        self.balances = defaultdict(float)
        self.shares = defaultdict(lambda: defaultdict(float))

    def apply(self, event):
        if isinstance(event, FundsDebited):
            if self.balances[event.user_id] >= event.amount:
                self.balances[event.user_id] -= event.amount
            else:
                raise ValueError(f"Insufficient funds for {event.user_id} to debit {event.amount}")
        elif isinstance(event, FundsCredited):
            self.balances[event.user_id] += event.amount
        elif isinstance(event, SharesCredited):
            self.shares[event.user_id][event.share_name] += event.quantity
        elif isinstance(event, SharesDebited):
            if self.shares[event.user_id][event.share_name] >= event.quantity:
                self.shares[event.user_id][event.share_name] -= event.quantity
            else:
                raise ValueError(
                    f"Insufficient shares for {event.user_id} to debit {event.quantity} of {event.share_name}")
