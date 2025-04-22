import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Create a function to get stock data
def get_reliance_stock_data():
    # Define the ticker symbol for Reliance Industries (NSE)
    ticker = "RELIANCE.NS"
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Get the data
    reliance = yf.Ticker(ticker)
    df = reliance.history(start=start_date, end=end_date)
    
    # Display basic information
    print(f"Reliance Stock Price Data ({start_date.date()} to {end_date.date()})")
    print("\nLast 5 trading days:")
    print(df.tail())
    
    # Optional: Save to CSV
    df.to_csv('reliance_stock_data.csv')
    return df

# Run the function
if __name__ == "__main__":
    stock_data = get_reliance_stock_data()
