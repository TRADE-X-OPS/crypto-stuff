# -*- coding: utf-8 -*-
"""
Binance Triangular Arbitrage Bot using binance-connector
"""

import time
import logging
from binance.spot import Spot
from threading import Thread

# Binance API Keys (Replace with your keys)
API_KEY = ''
API_SECRET = ''

client = Spot(api_key=API_KEY, api_secret=API_SECRET)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global variables
last_trade_time = 0  
cooldown_time = 3  # Dynamic cooldown (adjustable)
MIN_PROFIT_THRESHOLD = 0.03  # Minimum profit percentage for arbitrage execution


# Function to fetch the order book
def get_order_book(pair, limit=5):
    try:
        return client.depth(pair, limit=limit)
    except Exception as e:
        logging.error(f"Error fetching order book for {pair}: {e}")
        return None


# Function to fetch the current market price
def get_market_price(pair):
    try:
        ticker = client.ticker_price(pair)
        return float(ticker['price'])
    except Exception as e:
        logging.error(f"Error fetching market price for {pair}: {e}")
        return None


# Function to cancel all open orders for a given symbol
def cancel_all_orders(symbol):
    try:
        orders = client.open_orders(symbol)
        for order in orders:
            client.cancel_order(symbol=symbol, orderId=order['orderId'])
            logging.info(f"Cancelled order: {order}")
    except Exception as e:
        logging.error(f"Error cancelling orders for {symbol}: {e}")


# Function to place limit or market orders
def place_order(symbol, side, quantity, price=None, order_type="LIMIT"):
    try:
        if order_type == "LIMIT":
            order = client.new_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce="GTC",
                quantity=quantity,
                price=f"{price:.6f}"
            )
        else:  # Market Order
            order = client.new_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )

        logging.info(f"Placed {order_type} {side} order: {order}")
        return order
    except Exception as e:
        logging.error(f"Error placing {order_type} {side} order for {symbol}: {e}")
        return None


# Function to execute triangular arbitrage
def execute_arbitrage(amount):
    global last_trade_time, cooldown_time

    # Add error handling for price checks
    try:
        # Enforce cooldown
        current_time = time.time()
        if current_time - last_trade_time < cooldown_time:
            logging.info("Cooldown active. Waiting before next trade.")
            return

        # Fetch order books with error handling
        sol_usdt_book = get_order_book('SOLUSDT')
        eth_usdt_book = get_order_book('ETHUSDT')
        sol_eth_book = get_order_book('SOLETH')

        if not all([sol_usdt_book, eth_usdt_book, sol_eth_book]):
            logging.error("Failed to fetch one or more order books. Skipping trade execution.")
            return

        # Add volume checks
        sol_usdt_volume = float(sol_usdt_book['asks'][0][1])
        eth_usdt_volume = float(eth_usdt_book['bids'][0][1])
        sol_eth_volume = float(sol_eth_book['bids'][0][1])

        # Check if there's enough volume
        if any(volume < amount for volume in [sol_usdt_volume, eth_usdt_volume, sol_eth_volume]):
            logging.warning("Insufficient volume for trade. Skipping execution.")
            return

        # Extract best available prices with additional error handling
        try:
            sol_usdt_ask = float(sol_usdt_book['asks'][0][0])
            eth_usdt_bid = float(eth_usdt_book['bids'][0][0])
            sol_eth_bid = float(sol_eth_book['bids'][0][0])
        except (IndexError, ValueError) as e:
            logging.error(f"Error parsing prices: {e}")
            return

        # Calculate implied price and potential profit
        implied_sol_eth = sol_usdt_ask / eth_usdt_bid
        profit_percentage = ((implied_sol_eth - sol_eth_bid) / sol_eth_bid) * 100

        if profit_percentage >= MIN_PROFIT_THRESHOLD:
            logging.info(f"Arbitrage opportunity detected! Potential Profit: {profit_percentage:.6f}%")

            sol_amount = amount / sol_usdt_ask

            # Step 1: Buy SOL with USDT
            logging.info(f"Buying {sol_amount:.3f} SOL at {sol_usdt_ask} USDT per SOL")
            order1 = place_order('SOLUSDT', 'BUY', round(sol_amount, 3), sol_usdt_ask)
            if not order1:
                return

            time.sleep(1)

            # Step 2: Buy ETH with SOL
            eth_amount = sol_amount / sol_eth_bid
            logging.info(f"Buying {eth_amount:.3f} ETH at {sol_eth_bid} SOL per ETH")
            order2 = place_order('SOLETH', 'BUY', round(eth_amount, 3), sol_eth_bid)
            if not order2:
                return

            time.sleep(1)

            # Step 3: Sell ETH for USDT
            final_usdt = eth_amount * eth_usdt_bid
            logging.info(f"Selling {eth_amount:.3f} ETH for {final_usdt:.3f} USDT at {eth_usdt_bid} USDT per ETH")
            order3 = place_order('ETHUSDT', 'SELL', round(eth_amount, 3), eth_usdt_bid, "MARKET")
            if not order3:
                return

            # Adjust cooldown dynamically
            cooldown_time = max(2, cooldown_time - 0.5)  # Reduce cooldown if successful
            last_trade_time = time.time()

        else:
            logging.info(f"No arbitrage opportunity. Profit: {profit_percentage:.6f}%")
            cooldown_time = min(10, cooldown_time + 1)  # Increase cooldown if no trade executed

    except Exception as e:
        logging.error(f"Unexpected error in execute_arbitrage: {e}")
        return


# Monitor market conditions in parallel
def monitor_market():
    while True:
        try:
            execute_arbitrage(200)  # Start with 200 USDT
        except Exception as e:
            logging.error(f"Error in trading loop: {e}")
        time.sleep(1)


# Run bot
if __name__ == "__main__":
    thread = Thread(target=monitor_market)
    thread.start()
