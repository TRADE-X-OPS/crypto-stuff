from binance.client import Client
import time

client = Client(api_key='', api_secret='')

last_trade_time = 0
stop_loss_percentage = 0.02  

# Function to fetch the current order book for a pair
def get_order_book(pair, limit=5):
    order_book = client.get_order_book(symbol=pair, limit=limit)
    return order_book

# Function to fetch the current market price for a trading pair
def get_market_price(pair):
    ticker = client.get_symbol_ticker(symbol=pair)
    return float(ticker['price'])

# Function to calculate implied price
def calculate_implied_price(sol_usdt_price, eth_usdt_price, sol_eth_price):
    return sol_usdt_price / eth_usdt_price

# Function to cancel all open orders for a symbol
def cancel_all_orders(symbol):
    orders = client.get_open_orders(symbol=symbol)
    for order in orders:
        try:
            client.cancel_order(symbol=symbol, orderId=order['orderId'])
            print(f"Cancelled order: {order}")
        except Exception as e:
            print(f"Error cancelling order: {e}")

# Function to place a limit buy order
def place_limit_order(symbol, side, quantity, price):
    try:
        order = client.order_limit(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=f"{price:.6f}"
        )
        print(f"Placed {side} order: {order}")
        return order
    except Exception as e:
        print(f"Error placing {side} order: {e}")
        return None

# Function to execute triangular arbitrage
def execute_arbitrage(amount):
    global last_trade_time  # Access the global variable

    # Check if cooldown has passed (5 seconds)
    current_time = time.time()
    if current_time - last_trade_time < 5:
        print("Cooldown in effect. Waiting for 5 seconds before next trade.")
        return  # Exit if cooldown is not over

    # Fetch order books for the pairs
    sol_usdt_order_book = get_order_book('SOLUSDT')
    eth_usdt_order_book = get_order_book('ETHUSDT')
    sol_eth_order_book = get_order_book('SOLETH')

    # Extract the order book prices
    sol_usdt_ask = float(sol_usdt_order_book['asks'][0][0])  
    eth_usdt_bid = float(eth_usdt_order_book['bids'][0][0])  
    sol_eth_bid = float(sol_eth_order_book['bids'][0][0])  

    implied_sol_eth = sol_usdt_ask / eth_usdt_bid

    potential_profit_percentage = ((implied_sol_eth - sol_eth_bid) / sol_eth_bid) * 100

    if potential_profit_percentage >= 0.03:
        print(f"Arbitrage opportunity detected! Potential Profit: {potential_profit_percentage:.6f}%")

        sol_amount = amount / sol_usdt_ask
        print(f"Placing order to buy {sol_amount:.3f} SOL with {amount} USDT at {sol_usdt_ask} USDT per SOL")

        order1 = place_limit_order('SOLUSDT', 'BUY', round(sol_amount, 3), sol_usdt_ask)
        if not order1:
            return

        time.sleep(1)

        eth_amount = sol_amount / sol_eth_bid
        print(f"Placing order to buy {eth_amount:.3f} ETH with {sol_amount:.3f} SOL at {sol_eth_bid} SOL per ETH")

        order2 = place_limit_order('SOLETH', 'BUY', round(eth_amount, 3), sol_eth_bid)
        if not order2:
            return

        time.sleep(1)

        final_usdt = eth_amount * eth_usdt_bid
        print(f"Placing order to sell {eth_amount:.3f} ETH for {final_usdt:.3f} USDT at {eth_usdt_bid} USDT per ETH")

        order3 = place_limit_order('ETHUSDT', 'SELL', round(eth_amount, 3), eth_usdt_bid)
        if not order3:
            return

        # Monitor if the arbitrage opportunity disappears
        while True:
            # Recheck market prices periodically
            sol_usdt_ask = float(get_order_book('SOLUSDT')['asks'][0][0])
            eth_usdt_bid = float(get_order_book('ETHUSDT')['bids'][0][0])
            sol_eth_bid = float(get_order_book('SOLETH')['bids'][0][0])

            implied_sol_eth = sol_usdt_ask / eth_usdt_bid
            new_potential_profit_percentage = ((implied_sol_eth - sol_eth_bid) / sol_eth_bid) * 100

            # If the profit percentage decreases or becomes negative, cancel the orders and exit
            if new_potential_profit_percentage < 0.03:
                print("Arbitrage opportunity disappeared! Cancelling open orders.")
                cancel_all_orders('SOLUSDT')
                cancel_all_orders('SOLETH')
                cancel_all_orders('ETHUSDT')
                print("Exiting arbitrage trade.")
                break  # Exit the trade loop

            time.sleep(5)  # Recheck after 5 seconds

        # Update the last trade time after successfully executing the trade
        last_trade_time = time.time()

    else:
        print(f"No arbitrage opportunity found. Potential Profit: {potential_profit_percentage:.6f}%")

if __name__ == "__main__":
    while True:
        execute_arbitrage(200)  # Start with 200 USDT
        time.sleep(1)  # Check every 1 second
