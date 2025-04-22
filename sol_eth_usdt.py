from binance.client import Client
from binance.enums import *
import time
import math

# Initialize Binance Client
client = Client(api_key='lPtLlj6RigNbgkFGdDE6DhvSqC43CKLKXmLbfqJxLFamT66Zz50zvl6QhjA4BzOH',
                api_secret='7lzGOMHzgpsXcOpF4BLkOs9tKZKF413bwOZOA2vjhgmnJ1WJEJrrsvUaOnRKmpoQ')

# Function to fetch best ask and bid prices for a trading pair
def get_order_book_prices(pair):
    order_book = client.get_order_book(symbol=pair)
    best_ask = float(order_book['asks'][0][0])  # Lowest ask price
    best_bid = float(order_book['bids'][0][0])  # Highest bid price
    return best_ask, best_bid

# Function to get lot size rules for a trading pair
def get_lot_size_rules(pair):
    exchange_info = client.get_exchange_info()
    for symbol_info in exchange_info['symbols']:
        if symbol_info['symbol'] == pair:
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    return {
                        'minQty': float(filter['minQty']),
                        'maxQty': float(filter['maxQty']),
                        'stepSize': float(filter['stepSize'])
                    }
    raise ValueError(f"Lot size rules not found for pair: {pair}")

# Function to adjust quantity based on lot size rules
def adjust_quantity(quantity, lot_size_rules):
    step_size = lot_size_rules['stepSize']
    min_qty = lot_size_rules['minQty']
    max_qty = lot_size_rules['maxQty']

    # Round to the nearest step size
    adjusted_quantity = math.floor(quantity / step_size) * step_size

    # Ensure quantity is within min and max limits
    adjusted_quantity = max(min(adjusted_quantity, max_qty), min_qty)

    return adjusted_quantity

# Function to set leverage for a trading pair
def set_leverage(pair, leverage):
    try:
        response = client.futures_change_leverage(symbol=pair, leverage=leverage)
        print(f"Leverage set to {leverage}x for {pair}: {response}")
    except Exception as e:
        print(f"Error setting leverage for {pair}: {e}")

# Function to execute triangular arbitrage with 50x leverage
def execute_arbitrage(amount):
    # Set leverage to 50x for all pairs
    set_leverage('SOLUSDT', 50)
    set_leverage('ETHUSDT', 50)
    set_leverage('SOLETH', 50)

    # Fetch best ask/bid prices for all pairs
    sol_usdt_ask, sol_usdt_bid = get_order_book_prices('SOLUSDT')
    eth_usdt_ask, eth_usdt_bid = get_order_book_prices('ETHUSDT')
    sol_eth_ask, sol_eth_bid = get_order_book_prices('SOLETH')

    # Fetch lot size rules for all pairs
    sol_usdt_lot_size = get_lot_size_rules('SOLUSDT')
    sol_eth_lot_size = get_lot_size_rules('SOLETH')
    eth_usdt_lot_size = get_lot_size_rules('ETHUSDT')

    # Calculate implied SOL/ETH price
    implied_sol_eth = sol_usdt_ask / eth_usdt_bid

    # Calculate potential profit percentage
    potential_profit_percentage = ((implied_sol_eth - sol_eth_ask) / sol_eth_ask) * 100

    if potential_profit_percentage >= 0.030:
        print(f"Arbitrage opportunity detected! Potential Profit: {potential_profit_percentage:.6f}%")

        # Step 1: Buy SOL with USDT (Margin)
        sol_amount = amount / sol_usdt_ask
        sol_amount = adjust_quantity(sol_amount, sol_usdt_lot_size)
        print(f"Placing margin order to buy {sol_amount:.6f} SOL with {amount} USDT at {sol_usdt_ask} USDT per SOL")

        try:
            order1 = client.create_margin_order(
                symbol='SOLUSDT',
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=round(sol_amount, 6)
            )
            print("Order 1 (Buy SOL/USDT) placed:", order1)
        except Exception as e:
            print("Error placing Order 1:", e)
            return

        # Wait for Order 1 to be filled
        time.sleep(1)

        # Step 2: Buy ETH with SOL (Margin)
        eth_amount = sol_amount / sol_eth_ask
        eth_amount = adjust_quantity(eth_amount, sol_eth_lot_size)
        print(f"Placing margin order to buy {eth_amount:.6f} ETH with {sol_amount:.6f} SOL at {sol_eth_ask} SOL per ETH")

        try:
            order2 = client.create_margin_order(
                symbol='SOLETH',
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=round(eth_amount, 6)
            )
            print("Order 2 (Buy ETH/SOL) placed:", order2)
        except Exception as e:
            print("Error placing Order 2:", e)
            return

        # Wait for Order 2 to be filled
        time.sleep(1)

        # Step 3: Sell ETH for USDT (Margin)
        final_usdt = eth_amount * eth_usdt_bid
        eth_amount = adjust_quantity(eth_amount, eth_usdt_lot_size)
        print(f"Placing margin order to sell {eth_amount:.6f} ETH for {final_usdt:.6f} USDT at {eth_usdt_bid} USDT per ETH")

        try:
            order3 = client.create_margin_order(
                symbol='ETHUSDT',
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=round(eth_amount, 6)
            )
            print("Order 3 (Sell ETH/USDT) placed:", order3)
        except Exception as e:
            print("Error placing Order 3:", e)
            return

        # Calculate profit
        profit = final_usdt - amount
        print(f"Transaction Complete! Expected Profit: {profit:.6f} USDT ({(profit / amount) * 100:.6f}%)")
    else:
        print(f"No arbitrage opportunity found. Potential Profit: {potential_profit_percentage:.6f}%")

# Main loop
if __name__ == "__main__":
    while True:
        execute_arbitrage(100)  # Start with 100 USDT
        time.sleep(1)  # Check every 1 second