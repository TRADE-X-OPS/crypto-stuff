# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:40:50 2025

@author: OMEN
"""

import requests
import time

# Replace with your API key and secret
API_KEY = 'lPtLlj6RigNbgkFGdDE6DhvSqC43CKLKXmLbfqJxLFamT66Zz50zvl6QhjA4BzOH'
API_SECRET = '7lzGOMHzgpsXcOpF4BLkOs9tKZKF413bwOZOA2vjhgmnJ1WJEJrrsvUaOnRKmpoQ'

# Base URL for the Binance API
BASE_URL = 'https://api.binance.com/api/v3'

# Function to get the latest price for a trading pair
def get_price(pair):
    url = f"{BASE_URL}/ticker/price"
    params = {'symbol': pair}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return float(data['price'])
    else:
        print(f"Error fetching data for {pair}: {response.status_code}")
        return None

# Function to check for triangular arbitrage opportunity
def check_arbitrage():
    # Get prices for the three pairs
    btc_usdt = get_price('BTCUSDT')
    eth_usdt = get_price('ETHUSDT')
    eth_btc = get_price('ETHBTC')

    if btc_usdt and eth_usdt and eth_btc:
        # Calculate the implied price of ETH/BTC through BTC/USDT and ETH/USDT
        implied_eth_btc = eth_usdt / btc_usdt

        # Check if there's an arbitrage opportunity
        if implied_eth_btc > eth_btc:
            print(f"Arbitrage Opportunity Detected!")
            print(f"Implied ETH/BTC: {implied_eth_btc}")
            print(f"Actual ETH/BTC: {eth_btc}")
            print(f"Profit Margin: {(implied_eth_btc - eth_btc) / eth_btc * 100:.2f}%")
        else:
            print("No arbitrage opportunity found.")
    else:
        print("Failed to fetch prices for all pairs.")

# Main loop to continuously check for arbitrage opportunities
if __name__ == "__main__":
    while True:
        check_arbitrage()
        time.sleep(10)  # Check every 10 seconds