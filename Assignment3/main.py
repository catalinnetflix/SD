from event_store import EventStore
from commands import CommandHandler
from domain import OrderBook
from account import Account


def capture_state(order_book, account):
    state = {}

    state['active_orders'] = {
        oid: order
        for share_orders in order_book.buy_orders.values()
        for order in share_orders
        for oid in [order.order_id]
        if oid in order_book.active_orders
    }

    state['active_orders'].update({
        oid: order
        for share_orders in order_book.sell_orders.values()
        for order in share_orders
        for oid in [order.order_id]
        if oid in order_book.active_orders
    })

    state['finished_orders'] = [
        order
        for share_orders in order_book.buy_orders.values()
        for order in share_orders
        if order.order_id not in order_book.active_orders
    ]

    state['finished_orders'].extend([
        order
        for share_orders in order_book.sell_orders.values()
        for order in share_orders
        if order.order_id not in order_book.active_orders
    ])

    state['balances'] = dict(account.balances)
    state['shares'] = dict(account.shares)

    return state


def replay(event_store):
    order_book = OrderBook(event_store)
    account = Account()

    for event in event_store.get_all_events():
        order_book.apply(event)
        account.apply(event)

    return order_book, account



def print_state(state):
    print("\nActive Orders:")
    for order_id, order in state['active_orders'].items():
        print(f"  Order ID: {order_id} | {order}")

    print("\nFinished Orders:")
    for order in state['finished_orders']:
        print(f"  {order}")

    print("\nBalances:", state['balances'])
    print("Shares:", state['shares'])
    print("\n" + "=" * 40)


def main():
    store = EventStore()
    order_book = OrderBook(store)
    account = Account()
    handler = CommandHandler(store, order_book, account)

    print("Initializing accounts")
    handler.credit_funds("user1", 10000)
    handler.credit_funds("user2", 5000)
    handler.credit_shares("user1", "AAPL", 10)
    handler.credit_shares("user2", "AAPL", 30)

    order_book, account = replay(store)
    print_state(capture_state(order_book, account))

    print("\nPlacing sell orders")
    sell_order_id_1 = handler.place_order("user2", "sell", 10, 50, "AAPL")
    sell_order_id_2 = handler.place_order("user2", "sell", 5, 55, "AAPL")
    order_book, account = replay(store)
    print_state(capture_state(order_book, account))

    print("\nPlacing buy order")
    buy_order_id = handler.place_order("user1", "buy", 8, 50, "AAPL")
    order_book, account = replay(store)
    print_state(capture_state(order_book, account))

    print("\nExecuting trade")
    handler.execute_trade(buy_order_id, sell_order_id_1, 8, 50, "AAPL")
    order_book, account = replay(store)
    print_state(capture_state(order_book, account))

    print("\nCanceling remaining sell order")
    handler.cancel_order(sell_order_id_2)
    order_book, account = replay(store)
    print_state(capture_state(order_book, account))

    print("\nFinal state:")
    print_state(capture_state(order_book, account))


if __name__ == "__main__":
    main()