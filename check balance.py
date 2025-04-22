# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 23:30:21 2025

@author: OMEN
"""

from binance.client import Client

# Initialize Binance Client
client = Client(api_key='W3QtdUREzgdMYVLoYAvDLGnMc1hH0ZYjOUnBV4snxD6o7k2UVwNkaPrBSH2ne8Aj', api_secret='RXS34Uut0oxGVPI46sR0ybOJyWZUEbezUrm2JwGXCMNcKbXPcZ0l6TVpy0TVnKHz')

# Function to check Binance balance
def check_balance():
    try:
        # Get account information
        account_info = client.get_account()

        # Print balance information for each asset
        for asset in account_info['balances']:
            asset_name = asset['asset']
            free_balance = asset['free']  # Available balance
            locked_balance = asset['locked']  # Locked balance (not available for trading)
            
            if float(free_balance) > 0:  # Print only assets with free balance greater than 0
                print(f"{asset_name}: Free = {free_balance}, Locked = {locked_balance}")

    except Exception as e:
        print(f"Error fetching account balance: {e}")

# Call the function to check balance
if __name__ == "__main__":
    check_balance()
