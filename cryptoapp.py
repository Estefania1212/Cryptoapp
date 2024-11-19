

import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pycoingecko import CoinGeckoAPI

import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pycoingecko import CoinGeckoAPI

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

# Function to get exchange rate for selected currency using CoinGecko
def get_exchange_rate_coingecko(base_currency, target_currency):
    try:
        # Fetch exchange rate from CoinGecko between USD and the selected currency
        rates = cg.get_price(ids=target_currency.lower(), vs_currencies=base_currency.lower())
        return rates.get(target_currency.lower(), {}).get(base_currency.lower(), 1)
    except Exception as e:
        st.warning(f"Error fetching exchange rate from CoinGecko: {e}. Defaulting to 1 {target_currency} = 1 {base_currency}.")
        return 1  # Default to 1 if there's an error

# Function to load cryptocurrency data
def load_data():
    symbols = [
        "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", 
        "ADA-USD", "DOGE-USD", "DOT1-USD", "LINK-USD", "XLM-USD",
        "UNI3-USD", "AAVE-USD", "VET-USD", "ATOM1-USD", "XMR-USD",
        "TRX-USD", "EOS-USD", "FIL-USD", "XTZ-USD", "SOL1-USD"
    ]
    
  # Download data from Yahoo Finance starting from 2023
    data = yf.download(symbols, start="2023-01-01", end=pd.to_datetime('today'))
    
    # Extract adjusted close prices
    df = data["Adj Close"].reset_index()
    df = df.rename(columns={"index": "Date"})

    return df

# Portfolio management functionality
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
            # Convert portfolio value based on selected currency
            portfolio_value += transaction["Quantity"] * transaction["Price"]
    
    # Convert portfolio value to selected currency
    if currency != "USD":
        exchange_rate = get_exchange_rate_coingecko("usd", currency)  # Only use CoinGecko for exchange rate
        portfolio_value *= exchange_rate

    st.sidebar.info(f"Portfolio Value: {portfolio_value:.2f} {currency}")

    return portfolio

# Streamlit app
def main():
    st.title("Cryptocurrency Price Data")
    st.sidebar.header("Inputs")

    # Currency selection
    currency = st.sidebar.selectbox('Currency', ['USD', 'EUR', 'GBP'])

    # Load cryptocurrency data
    df = load_data()

    # Sidebar - Cryptocurrency selections
    sorted_coin = sorted(df.columns[1:])
    selected_coin = st.sidebar.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
    df_selected_coin = df[["Date"] + selected_coin]

    # Sidebar - Number of data points to display
    num_data_points = st.sidebar.slider('Display N Data Points', 10, len(df), 100)
    df_display = df_selected_coin.tail(num_data_points)

    # Convert prices to selected currency if it's not USD
    if currency != "USD":
        exchange_rate = get_exchange_rate_coingecko("usd", currency)  # Use CoinGecko only for exchange rate
        for col in df_display.columns[1:]:
            df_display[col] = df_display[col] * exchange_rate
    
    # Display price data of selected cryptocurrencies
    st.subheader(f'Price Data of Selected Cryptocurrencies in {currency}')
    st.dataframe(df_display.set_index("Date"))

    # Line plot of price data
    st.subheader(f'Line Plot of Price Data in {currency}')
    plt.figure(figsize=(10, 6))
    for column in df_display.columns[1:]:
        plt.plot(df_display["Date"], df_display[column], label=column)
    plt.xlabel("Date")
    plt.ylabel(f"Price ({currency})")
    plt.title(f"Price Data of Selected Cryptocurrencies in {currency}")
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











