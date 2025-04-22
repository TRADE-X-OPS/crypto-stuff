# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 20:32:33 2025

@author: OMEN
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
file_path = 'arbitrage_opportunitie.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Convert 'Timestamp' to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Fill NaN values with 0 for cumulative sum calculation
df['Arbitrage ETH/BTC (%)'] = df['Arbitrage ETH/BTC (%)'].fillna(0)
df['Arbitrage ETH/BNB (%)'] = df['Arbitrage ETH/BNB (%)'].fillna(0)

# Calculate cumulative sums
df['Cumulative ETH/BTC'] = df['Arbitrage ETH/BTC (%)'].cumsum()
df['Cumulative ETH/BNB'] = df['Arbitrage ETH/BNB (%)'].cumsum()

# Plot the cumulative data
plt.figure(figsize=(12, 6))
plt.plot(df['Timestamp'], df['Cumulative ETH/BTC'], marker='o', linestyle='-', color='b', label='Cumulative ETH/BTC (%)')
plt.plot(df['Timestamp'], df['Cumulative ETH/BNB'], marker='o', linestyle='-', color='r', label='Cumulative ETH/BNB (%)')

# Add labels and title
plt.xlabel('Timestamp')
plt.ylabel('Cumulative Arbitrage (%)')
plt.title('Cumulative Arbitrage Opportunities Over Time')
plt.legend()
plt.grid(True)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()