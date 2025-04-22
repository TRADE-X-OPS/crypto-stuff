# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 03:17:05 2025

@author: OMEN
"""

import ccxt
from datetime import datetime
import csv
import time

# Initialize Binance Futures
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future',  # Use futures trading
    },
})

# CSV file to save spread data
CSV_FILE = 'spread_data.csv'

# Function to fetch order book and calculate spread
def fetch_spread():
    try:
        # Fetch order book for BTC/USDT futures
        order_book = exchange.fetch_order_book('BTC/USDT')

        # Calculate spread
        bid_price = order_book['bids'][0][0]  # Highest bid price
        ask_price = order_book['asks'][0][0]  # Lowest ask price
        spread = ask_price - bid_price

        # Get the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return timestamp, bid_price, ask_price, spread
    except Exception as e:
        print(f"Error fetching spread: {e}")
        return None, None, None, None

# Function to save spread data to CSV
def save_to_csv(timestamp, bid_price, ask_price, spread):
    try:
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            # Write header if the file is empty
            if file.tell() == 0:
                writer.writerow(['Timestamp', 'Bid Price', 'Ask Price', 'Spread'])
            # Write the datak
            writer.writerow([timestamp, bid_price, ask_price, spread])
        print(f"Spread data saved to {CSV_FILE}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# Main loop to fetch and save spread data every 1 second
while True:
    timestamp, bid_price, ask_price, spread = fetch_spread()
    if timestamp:  # Only save data if fetch was successful
        print(f"Timestamp: {timestamp}")
        print(f"Bid Price: {bid_price}")
        print(f"Ask Price: {ask_price}")
        print(f"Spread: {spread} USDT")
        save_to_csv(timestamp, bid_price, ask_price, spread)
    time.sleep(1)  # Wait for 1 second before the next iteration