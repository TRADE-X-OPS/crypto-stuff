# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 00:34:26 2025

@author: OMEN
"""

import ccxt
from datetime import datetime
import csv
import time

# Initialize the exchange
exchange = ccxt.binance()

# Function to fetch data, calculate arbitrage, and save to CSV
def fetch_and_save_arbitrage():
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Fetch tickers
    btc_ticker = exchange.fetch_ticker('BTC/USDT')
    eth_ticker = exchange.fetch_ticker('ETH/USDT')
    btc_eth_ticker = exchange.fetch_ticker('ETH/BTC')
    bnb_ticker = exchange.fetch_ticker('BNB/USDT')
    bnb_eth_ticker = exchange.fetch_ticker('BNB/ETH')

    # Last prices
    btc_last_price = btc_ticker['last']
    eth_last_price = eth_ticker['last']
    btc_eth_last_price = btc_eth_ticker['last']
    bnb_last_price = bnb_ticker['last']
    bnb_eth_last_price = bnb_eth_ticker['last']

    # Implied prices
    implied_eth_btc_price = eth_last_price / btc_last_price
    implied_eth_bnb_price = eth_last_price / bnb_last_price

    # Arbitrage opportunities
    arbitrage_btc_eth = (implied_eth_btc_price - btc_eth_last_price) / btc_eth_last_price * 100
    eth_bnb_last_price = 1 / bnb_eth_last_price
    arbitrage_eth_bnb = (implied_eth_bnb_price - eth_bnb_last_price) / eth_bnb_last_price * 100

    # Print the results
    print(f"Timestamp: {timestamp}")
    print(f"Implied ETH/BTC price: {implied_eth_btc_price}")
    print(f"Last price of ETH/BTC: {btc_eth_last_price}")
    print(f"Implied ETH/BNB price: {implied_eth_bnb_price}")
    print(f"Last price of ETH/BNB: {eth_bnb_last_price}")
    print(f"Arbitrage opportunity (%): {arbitrage_btc_eth:.4f}%")
    print(f"Arbitrage opportunity (%): {arbitrage_eth_bnb:.4f}%")

    # Save the results to a CSV file
    with open('arbitrage_results.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Write header if the file is empty
        if file.tell() == 0:
            writer.writerow([
                'Timestamp',
                'Implied ETH/BTC Price', 'Last ETH/BTC Price', 'Arbitrage ETH/BTC (%)',
                'Implied ETH/BNB Price', 'Last ETH/BNB Price', 'Arbitrage ETH/BNB (%)'
            ])
        # Write the data
        writer.writerow([
            timestamp,
            implied_eth_btc_price, btc_eth_last_price, arbitrage_btc_eth,
            implied_eth_bnb_price, eth_bnb_last_price, arbitrage_eth_bnb
        ])

    print("Results saved to arbitrage_results.csv")

# Run the loop every 5 seconds
while True:
    fetch_and_save_arbitrage()
    time.sleep(5)  # Wait for 5 seconds before the next iteration