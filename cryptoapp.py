import yfinance as yf 
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np 
from bs4 import BeautifulSoup
import requests
import json 
import time 
from urllib.request import urlopen
from datetime import date 



from forex_python.converter import CurrencyRates
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf  # Ensure you import yfinance

# Fetch cryptocurrency data from Yahoo Finance
def load_data(currency):
    symbols = [
        "BTC-USD", "ETH-USD", "XRP-USD", "LTC-USD", "BCH-USD", 
        "ADA-USD", "DOGE-USD", "DOT1-USD", "LINK-USD", "XLM-USD",
        "UNI3-USD", "AAVE-USD", "VET-USD", "ATOM1-USD", "XMR-USD",
        "TRX-USD", "EOS-USD", "FIL-USD", "XTZ-USD", "SOL1-USD"
    ]  # Add more symbols as needed
    data = yf.download(symbols, start="2020-01-01", end=pd.Timestamp.today())

    # Filter necessary columns
    df = data["Adj Close"].reset_index()
    df = df.rename(columns={"index": "Date"})

    # Convert prices to the desired currency
    c = CurrencyRates()
    for symbol in symbols:
        try:
            rate = c.get_rate("USD", currency)
            df[symbol] = df[symbol] * rate
        except Exception as e:
            st.warning(f"Error fetching rate for {symbol} with currency {currency}: {e}")
            # Optionally, you can set the value to NaN or keep the original value if conversion fails
            df[symbol] = df[symbol]  # This will just keep the original USD values if conversion fails

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
    c = CurrencyRates()
    for coin in portfolio:
        for transaction in portfolio[coin]:
            price_in_currency = transaction["Price"] * c.get_rate("USD", currency)
            portfolio_value += transaction["Quantity"] * price_in_currency

    st.sidebar.info(f"Portfolio Value: {portfolio_value} {currency}")

    return portfolio

# Streamlit app
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
