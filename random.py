# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 18:59:21 2025

@author: OMEN
"""

from binance.client import Client
import time

# Initialize Binance Client
client = Client(api_key='lPtLlj6RigNbgkFGdDE6DhvSqC43CKLKXmLbfqJxLFamT66Zz50zvl6QhjA4BzOH',
                api_secret='7lzGOMHzgpsXcOpF4BLkOs9tKZKF413bwOZOA2vjhgmnJ1WJEJrrsvUaOnRKmpoQ')

# Function to fetch the current market price for a trading pair
def get_market_price(pair):
    ticker = client.get_symbol_ticker(symbol=pair)
    return float(ticker['price'])

# Function to execute triangular arbitrage with normal limit orders
def execute_arbitrage(amount):
    # Fetch current market prices for all pairs
    bnb_usdt_price = get_market_price('BNBUSDT')
    eth_usdt_price = get_market_price('ETHUSDT')
    bnb_eth_price = get_market_price('BNBETH')

    # Calculate implied BNB/ETH price
    implied_bnb_eth = bnb_usdt_price / eth_usdt_price

    # Calculate potential profit percentage
    potential_profit_percentage = ((implied_bnb_eth - bnb_eth_price) / bnb_eth_price) * 100

    if potential_profit_percentage >= 0.020:
        print(f"Arbitrage opportunity detected! Potential Profit: {potential_profit_percentage:.6f}%")

        # Step 1: Buy BNB with USDT
        bnb_amount = amount / bnb_usdt_price
        print(f"Placing order to buy {bnb_amount} BNB with {amount} USDT at {bnb_usdt_price} USDT per BNB")

        try:
            order1 = client.order_limit_buy(
                symbol='BNBUSDT',
                quantity=round(bnb_amount, 3),  # Round to appropriate decimal places
                price=f"{bnb_usdt_price:.6f}"
            )
            print("Order 1 (Buy BNB/USDT) placed:", order1)
        except Exception as e:
            print("Error placing Order 1:", e)
            return

        # Wait for Order 1 to be filled
        time.sleep(1)

        # Step 2: Buy ETH with BNB
        eth_amount = bnb_amount / bnb_eth_price
        print(f"Placing order to buy {eth_amount} ETH with {bnb_amount} BNB at {bnb_eth_price} BNB per ETH")

        try:
            order2 = client.order_limit_buy(
                symbol='BNBETH',
                quantity=round(eth_amount, 3),
                price=f"{bnb_eth_price:.6f}"
            )
            print("Order 2 (Buy ETH/BNB) placed:", order2)
        except Exception as e:
            print("Error placing Order 2:", e)
            return

        # Wait for Order 2 to be filled
        time.sleep(1)

        # Step 3: Sell ETH for USDT
        final_usdt = eth_amount * eth_usdt_price
        print(f"Placing order to sell {eth_amount} ETH for {final_usdt} USDT at {eth_usdt_price} USDT per ETH")

        try:
            order3 = client.order_limit_sell(
                symbol='ETHUSDT',
                quantity=round(eth_amount, 3),
                price=f"{eth_usdt_price:.6f}"
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