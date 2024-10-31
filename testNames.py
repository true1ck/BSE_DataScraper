import yfinance as yf

def get_stock_symbol(company_name):
    try:
        # Search for the company in the stock market
        stock = yf.Ticker(company_name)
        return stock.ticker
    except Exception as e:
        print(f"Error fetching symbol for '{company_name}': {e}")
        return None

def main():
    # Get user input for the company name
    company_name = input("Enter the company name: ")
    
    # Get the stock symbol
    symbol = get_stock_symbol(company_name)
    
    if symbol:
        print(f"The stock symbol for '{company_name}' is: {symbol}")
    else:
        print(f"Could not find a stock symbol for '{company_name}'.")

if __name__ == "__main__":
    main()
