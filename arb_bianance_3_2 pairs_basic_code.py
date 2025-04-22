# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 01:01:59 2025

@author: OMEN
"""

import ccxt
from datetime import datetime

exchange = ccxt.binance()
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Fetch 
btc_ticker = exchange.fetch_ticker('BTC/USDT')
eth_ticker = exchange.fetch_ticker('ETH/USDT')
btc_eth_ticker = exchange.fetch_ticker('ETH/BTC')
bnb_ticker = exchange.fetch_ticker('BNB/USDT')
bnb_eth_ticker = exchange.fetch_ticker('BNB/ETH')

# Lp
btc_last_price = btc_ticker['last']
eth_last_price = eth_ticker['last']
btc_eth_last_price = btc_eth_ticker['last']
bnb_last_price = bnb_ticker['last']
bnb_eth_last_price = bnb_eth_ticker['last']

# implied
implied_eth_btc_price = eth_last_price / btc_last_price
implied_eth_bnb_price = eth_last_price / bnb_last_price

#arb
arbitrage_btc_eth = (implied_eth_btc_price - btc_eth_last_price) / btc_eth_last_price * 100
eth_bnb_last_price = 1 / bnb_eth_last_price
arbitrage_eth_bnb = (implied_eth_bnb_price - eth_bnb_last_price) / eth_bnb_last_price * 100

#saxsox
print(f"Timestamp: {timestamp}")
print(f"Implied ETH/BTC price: {implied_eth_btc_price}")
print(f"Last price of ETH/BTC: {btc_eth_last_price}")
print(f"Implied ETH/BNB price: {implied_eth_bnb_price}")
print(f"Last price of ETH/BNB: {eth_bnb_last_price}")
print(f"Arbitrage opportunity (%): {arbitrage_btc_eth:.4f}%")
print(f"Arbitrage opportunity (%): {arbitrage_eth_bnb:.4f}%")