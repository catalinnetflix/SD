from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Event:
    pass

@dataclass(frozen=True)
class OrderPlaced(Event):
    order_id: str
    user_id: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    share_name: str

@dataclass(frozen=True)
class OrderCancelled(Event):
    order_id: str
    user_id: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    share_name: str

@dataclass(frozen=True)
class TradeExecuted(Event):
    buy_order_id: str
    sell_order_id: str
    quantity: float
    price: float
    share_name: str


@dataclass(frozen=True)
class FundsDebited(Event):
    user_id: str
    amount: float

@dataclass(frozen=True)
class FundsCredited(Event):
    user_id: str
    amount: float

@dataclass(frozen=True)
class SharesCredited(Event):
    user_id: str
    share_name: str
    quantity: float

@dataclass(frozen=True)
class SharesDebited(Event):
    user_id: str
    share_name: str
    quantity: float




