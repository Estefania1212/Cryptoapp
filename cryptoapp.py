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
        rates = cg.get_exchange_rates()
        base_rate = rates["rates"][base_currency.lower()]["value"]
        target_rate = rates["rates"][target_currency.lower()]["value"]
        exchange_rate = target_rate / base_rate
        st.write(f"Exchange Rate (1 {base_currency} = {exchange_rate:.4f} {target_currency})")
        return exchange_rate
    except Exception as e:
        st.warning(f"Error fetching exchange rate from CoinGecko: {e}. Defaulting to 1 {base_currency} = 1 {target_currency}.")
        return 1  # Default to 1 if there's an error

# Function to load cryptocurrency data from Yahoo Finance
def load_data():
    symbols = ["BTC-USD", "ETH-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "SOL-USD"]
    try:
        data = yf.download(symbols, start="2022-01-01", end=pd.Timestamp.today())
        df = data["Adj Close"].reset_index()
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Error fetching data from Yahoo Finance: {e}")
        return pd.DataFrame()

# Function to get real-time cryptocurrency prices from CoinGecko
def get_real_time_prices(target_currency):
    try:
        prices = cg.get_price(
            ids=['bitcoin', 'ethereum', 'ripple', 'cardano', 'dogecoin', 'solana'],
            vs_currencies=[target_currency.lower()]
        )
        st.write(f"Real-time prices in {target_currency}:", prices)
        return prices
    except Exception as e:
        st.warning(f"Error fetching real-time prices from CoinGecko: {e}")
        return {}

# Streamlit app
def main():
    st.title("Cryptocurrency Price Data")
    st.sidebar.header("Inputs")

    # Currency selection
    currency = st.sidebar.selectbox('Currency', ['USD', 'EUR', 'GBP'])

    # Load cryptocurrency data
    df = load_data()
    if df.empty:
        st.stop()

    # Sidebar - Cryptocurrency selections
    sorted_coin = sorted(df.columns[1:])
    selected_coin = st.sidebar.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
    df_selected_coin = df[["Date"] + selected_coin]

    # Sidebar - Number of data points to display
    num_data_points = st.sidebar.slider('Display N Data Points', 10, len(df), 100)

    # Select the last 'num_data_points' rows from the dataframe
    df_display = df_selected_coin.tail(num_data_points)

    # Sort the data in descending order based on the 'Date' column
    df_display = df_display.sort_values(by="Date", ascending=False).reset_index(drop=True)

    # Convert prices to selected currency if it's not USD
    if currency != "USD":
        exchange_rate = get_exchange_rate_coingecko("usd", currency)
        for col in df_display.columns[1:]:
            df_display[col] = df_display[col] * exchange_rate
    else:
        exchange_rate = 1  # Default for USD

    # Debug: Check conversion logic
    st.write(f"Debugging conversion logic: Exchange rate = {exchange_rate}")
    st.write(f"First row of data after conversion: {df_display.head(1)}")

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

    # Price Alerts Section
    st.sidebar.subheader("Set Price Alert")
    alert_coin = st.sidebar.selectbox("Select Cryptocurrency for Price Alert", selected_coin)
    alert_price = st.sidebar.number_input(f"Set alert price for {alert_coin}", min_value=0.0)

    # Check price alert condition
    if alert_price > 0:
        latest_price = df_display[alert_coin].iloc[0]
        if latest_price >= alert_price:
            st.sidebar.success(f"Alert! {alert_coin} price is above {alert_price} {currency}. Current price: {latest_price:.2f} {currency}.")
        else:
            st.sidebar.info(f"Current {alert_coin} price is {latest_price:.2f} {currency}. Keep an eye on it.")

    # Real-time prices for cross-checking
    st.subheader("Real-time Cryptocurrency Prices (via CoinGecko)")
    real_time_prices = get_real_time_prices(currency)

# Run the Streamlit app
if __name__ == "__main__":
    main()



















