import yfinance as yf
import streamlit as st
from forex_python.converter import CurrencyRates
import matplotlib.pyplot as plt
import time
import pandas as pd
import requests

import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import time
import pandas as pd
import requests

# Function to fetch exchange rate from Free Forex API with retries
def get_exchange_rate_with_retries(base_currency, target_currency, retries=3, delay=5):
    attempt = 0
    api_url = f"https://www.freeforexapi.com/api/live"
    params = {
        'pairs': f"{base_currency}{target_currency}"
    }
    
    # Try fetching exchange rate with retries
    while attempt < retries:
        try:
            # Send request to Free Forex API
            response = requests.get(api_url, params=params)
            data = response.json()
            
            # Check if the request was successful
            if data['response']['status'] == 'success':
                rate = data['response']['rates'][f"{base_currency}{target_currency}"]['rate']
                return rate
            else:
                raise Exception("Error in API response")
        except Exception as e:
            # Handle exceptions, display a warning, and retry
            attempt += 1
            error_message = str(e)
            st.warning(f"Error fetching exchange rate (Attempt {attempt}): {error_message}. Retrying in {delay} seconds...")
        
        # Wait before retrying
        time.sleep(delay)

    # If the function fails after all retries, log an error and return a fallback rate (1)
    st.error(f"Failed to fetch exchange rate after {retries} attempts. Defaulting to 1 {target_currency} = 1 {base_currency}.")
    return 1  # Default to 1 if fetching fails (you can set this to another default value if needed)

# Function to load cryptocurrency data and convert to selected currency
def load_data(currency):
    symbols = [
        "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", 
        "ADA-USD", "DOGE-USD", "DOT1-USD", "LINK-USD", "XLM-USD",
        "UNI3-USD", "AAVE-USD", "VET-USD", "ATOM1-USD", "XMR-USD",
        "TRX-USD", "EOS-USD", "FIL-USD", "XTZ-USD", "SOL1-USD"
    ]
    
    # Download data from Yahoo Finance
    data = yf.download(symbols, start="2020-01-01", end=pd.Timestamp.today())

    # Extract adjusted close prices
    df = data["Adj Close"].reset_index()
    df = df.rename(columns={"index": "Date"})

    # Fetch exchange rate with retries for the selected currency
    rate = get_exchange_rate_with_retries("USD", currency)
    if rate is None:
        st.warning(f"Could not fetch rate for {currency}. Defaulting to 1 USD = 1 {currency}.")
        rate = 1  # Default to 1 if conversion fails

    # Convert prices to the desired currency
    for symbol in symbols:
        try:
            df[symbol] = df[symbol] * rate
        except Exception as e:
            st.warning(f"Error converting {symbol} to {currency}: {e}")
            # Keep original values if conversion fails
            df[symbol] = df[symbol]
            
    return df

# Portfolio management functionality (unchanged)
def portfolio_management(df, portfolio, currency):
    st.sidebar.subheader("Portfolio Management")

    # Add transaction
    st.sidebar.subheader("Add Transaction")
    coin = st.sidebar.selectbox('Cryptocurrency', df.columns[1:])
    date = st.sidebar.date_input("Date")
    quantity = st.sidebar.number_input("Quantity", min_value=0.0)
    price = st.sidebar.number_input("Price", min_value=0.0)
    transaction_type = st.sidebar.radio("Transaction Type", ["Buy", "Sell"])

    if st.sidebar.button("Add Transaction"):
        if transaction_type == "Buy":
            portfolio[coin].append({"Date": date, "Quantity": quantity, "Price": price})
            st.sidebar.success("Transaction added successfully!")
        elif transaction_type == "Sell":
            if coin in portfolio and len(portfolio[coin]) > 0:
                for transaction in portfolio[coin]:
                    if transaction["Quantity"] >= quantity:
                        transaction["Quantity"] -= quantity
                        if transaction["Quantity"] == 0:
                            portfolio[coin].remove(transaction)
                        st.sidebar.success("Transaction added successfully!")
                        break
                else:
                    st.sidebar.error("Insufficient quantity in portfolio for selling.")
            else:
                st.sidebar.error("No holdings in portfolio for selling.")

    # Calculate portfolio value
    st.sidebar.subheader("Portfolio Value")
    portfolio_value = 0
    for coin in portfolio:
        for transaction in portfolio[coin]:
            price_in_currency = transaction["Price"] * get_exchange_rate_with_retries("USD", currency)
            portfolio_value += transaction["Quantity"] * price_in_currency

    st.sidebar.info(f"Portfolio Value: {portfolio_value} {currency}")

    return portfolio

# Streamlit app (unchanged)
def main():
    st.title("Cryptocurrency Price Data")
    st.sidebar.header("Inputs")

    # Currency selection
    currency = st.sidebar.selectbox('Currency', ['USD', 'EUR', 'GBP'])  # Add more currencies as needed

    # Load cryptocurrency data
    df = load_data(currency)

    # Sidebar - Cryptocurrency selections
    sorted_coin = sorted(df.columns[1:])
    selected_coin = st.sidebar.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
    df_selected_coin = df[["Date"] + selected_coin]

    # Sidebar - Number of data points to display
    num_data_points = st.sidebar.slider('Display N Data Points', 10, len(df), 100)
    df_display = df_selected_coin.tail(num_data_points)

    # Display price data of selected cryptocurrencies
    st.subheader('Price Data of Selected Cryptocurrencies')
    st.dataframe(df_display.set_index("Date"))

    # Line plot of price data
    st.subheader('Line Plot of Price Data')
    plt.figure(figsize=(10, 6))
    for column in df_display.columns[1:]:
        plt.plot(df_display["Date"], df_display[column], label=column)
    plt.xlabel("Date")
    plt.ylabel(f"Price ({currency})")
    plt.title("Price Data of Selected Cryptocurrencies")
    plt.legend()
    st.pyplot(plt)

    # Initialize portfolio
    portfolio = {}
    for coin in selected_coin:
        portfolio[coin] = []

    # Add portfolio management functionality
    portfolio = portfolio_management(df_display, portfolio, currency)

# Run the Streamlit app
if __name__ == "__main__":
    main()
