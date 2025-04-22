# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 10:35:42 2025

@author: OMEN
"""
import ccxt
from datetime import datetime
import csv
import time

# Initialize the exchange
exchange = ccxt.binance()

# Set the minimum arbitrage threshold (0.025%)
MIN_ARB_THRESHOLD = 0.03


STOP_LOSS = 0.2  # Close the trade if loss exceeds 0.2%

# Flag to track if a trade has been executed
trade_executed = False
last_trade_time = None

# Variables to track open positions
open_position = None  # Stores the type of arbitrage trade (e.g., 'ETH/BTC' or 'ETH/BNB')
entry_price = None  # Stores the entry price of the trade

# Function to fetch data, calculate arbitrage, and save to CSV
def fetch_and_save_arbitrage():
    global trade_executed, last_trade_time, open_position, entry_price

    try:
        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Fetch tickers
        btc_ticker = exchange.fetch_ticker('BTC/USDT')
        eth_ticker = exchange.fetch_ticker('ETH/USDT')
        btc_eth_ticker = exchange.fetch_ticker('ETH/BTC')
        bnb_ticker = exchange.fetch_ticker('BNB/USDT')
        bnb_eth_ticker = exchange.fetch_ticker('BNB/ETH')

        # Last prices, ask, and bid prices
        btc_last_price = btc_ticker['last']
        eth_last_price = eth_ticker['last']
        btc_eth_last_price = btc_eth_ticker['last']
        btc_eth_ask_price = btc_eth_ticker['ask']
        btc_eth_bid_price = btc_eth_ticker['bid']
        bnb_last_price = bnb_ticker['last']
        bnb_eth_last_price = bnb_eth_ticker['last']
        bnb_eth_ask_price = bnb_eth_ticker['ask']
        bnb_eth_bid_price = bnb_eth_ticker['bid']
        
        # Implied prices
        implied_eth_btc_price = eth_last_price / btc_last_price
        implied_eth_bnb_price = eth_last_price / bnb_last_price

        # Arbitrage opportunities
        arbitrage_btc_eth = (implied_eth_btc_price - btc_eth_last_price) / btc_eth_last_price * 100
        eth_bnb_last_price = 1 / bnb_eth_last_price
        arbitrage_eth_bnb = (implied_eth_bnb_price - eth_bnb_last_price) / eth_bnb_last_price * 100

        # Check if we have an open position and manage exit
        if open_position:
            current_price = btc_eth_last_price if open_position == 'ETH/BTC' else bnb_eth_last_price
            profit_loss = ((current_price - entry_price) / entry_price) * 100       

            # Check for stop loss
            if profit_loss <= -STOP_LOSS:
                print(f"Timestamp: {timestamp} - Stop loss triggered. Closing {open_position} trade.")
                open_position = None
                entry_price = None
                trade_executed = True
                last_trade_time = time.time()
                return

            # Check if arbitrage opportunity has disappeared
            current_arb = arbitrage_btc_eth if open_position == 'ETH/BTC' else arbitrage_eth_bnb
            if current_arb < MIN_ARB_THRESHOLD:
                print(f"Timestamp: {timestamp} - Arbitrage opportunity disappeared. Closing {open_position} trade.")
                open_position = None
                entry_price = None
                trade_executed = True
                last_trade_time = time.time()
                return

        # Only look for new arbitrage opportunities if no position is open
        if not open_position:
            # Print the results only if arbitrage exceeds the threshold
            if arbitrage_btc_eth > MIN_ARB_THRESHOLD or arbitrage_eth_bnb > MIN_ARB_THRESHOLD:
                print(f"Timestamp: {timestamp}")
                if arbitrage_btc_eth > MIN_ARB_THRESHOLD:
                    print(f"Arbitrage opportunity ETH/BTC (%): {arbitrage_btc_eth:.4f}%")
                    print(f"ETH/BTC Ask Price: {btc_eth_ask_price}, Bid Price: {btc_eth_bid_price}")
                    open_position = 'ETH/BTC'
                    entry_price = btc_eth_last_price
                if arbitrage_eth_bnb > MIN_ARB_THRESHOLD:
                    print(f"Arbitrage opportunity ETH/BNB (%): {arbitrage_eth_bnb:.4f}%")
                    print(f"ETH/BNB Ask Price: {bnb_eth_ask_price}, Bid Price: {bnb_eth_bid_price}")
                    open_position = 'ETH/BNB'
                    entry_price = bnb_eth_last_price

                # Simulate a trade (replace this with your actual trading logic)
                print(f"Executing {open_position} trade...")
                trade_executed = True
                last_trade_time = time.time()

                # Save the results to a CSV file
                with open('arbitrage_opportunitie.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    # Write header if the file is empty
                    if file.tell() == 0:
                        writer.writerow([
                            'Timestamp',
                            'Arbitrage ETH/BTC (%)',
                            'ETH/BTC Ask Price',
                            'ETH/BTC Bid Price',
                            'Arbitrage ETH/BNB (%)',
                            'ETH/BNB Ask Price',
                            'ETH/BNB Bid Price'
                        ])
                    # Write the data
                    writer.writerow([
                        timestamp,
                        arbitrage_btc_eth if arbitrage_btc_eth > MIN_ARB_THRESHOLD else None,
                        btc_eth_ask_price if arbitrage_btc_eth > MIN_ARB_THRESHOLD else None,
                        btc_eth_bid_price if arbitrage_btc_eth > MIN_ARB_THRESHOLD else None,
                        arbitrage_eth_bnb if arbitrage_eth_bnb > MIN_ARB_THRESHOLD else None,
                        bnb_eth_ask_price if arbitrage_eth_bnb > MIN_ARB_THRESHOLD else None,
                        bnb_eth_bid_price if arbitrage_eth_bnb > MIN_ARB_THRESHOLD else None
                    ])

                print("Arbitrage opportunities saved to arbitrage_opportunitie.csv")
            else:
                print(f"Timestamp: {timestamp} - No arbitrage opportunities above {MIN_ARB_THRESHOLD}%.")

    except ccxt.NetworkError as e:
        print(f"Network error: {e}. Retrying in 1 second...")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}. Retrying in 1 second...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Retrying in 1 second...")

# Run the loop every 1 second
while True:
    fetch_and_save_arbitrage()
    time.sleep(1)  # Wait for 1 second before the next iteration