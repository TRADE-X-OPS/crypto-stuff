from binance.client import Client

# Initialize Binance Client
api_key = 'W3QtdUREzgdMYVLoYAvDLGnMc1hH0ZYjOUnBV4snxD6o7k2UVwNkaPrBSH2ne8Aj'
api_secret = 'RXS34Uut0oxGVPI46sR0ybOJyWZUEbezUrm2JwGXCMNcKbXPcZ0l6TVpy0TVnKHz'

client = Client(api_key=api_key, api_secret=api_secret)

# Function to test API by getting server time and account information
def test_api():
    try:
        # Get server time (a simple API call to check connectivity)
        server_time = client.get_server_time()
        print(f"Server time: {server_time}")

        # Get account information (this will test the account access)
        account_info = client.get_account()
        print(f"Account info: {account_info}")

        # If we get this far, the API is working
        print("API is working correctly!")
    except Exception as e:
        print(f"Error connecting to Binance API: {e}")

# Main execution
if __name__ == "__main__":
    test_api()
