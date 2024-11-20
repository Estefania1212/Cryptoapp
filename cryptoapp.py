import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pycoingecko import CoinGeckoAPI

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

# Function to get real-time cryptocurrency prices from CoinGecko
def get_real_time_prices(currency):
    try:
        prices = cg.get_price(
            ids=['bitcoin', 'ethereum', 'ripple', 'cardano', 'dogecoin', 'solana'],
            vs_currencies=[currency.lower()]
        )
        st.write(f"Real-time prices in {currency}:", prices)  # Debugging output
        return prices
    except Exception as e:
        st.warning(f"Error fetching real-time prices from CoinGecko: {e}")
        return {}

# Function to prepare the price data for display
def load_real_time_data(currency):
    # Fetch real-time prices
    prices = get_real_time_prices(currency)
    
    # Convert to DataFrame
    if prices:
        df = pd.DataFrame(prices).T.reset_index()
        df.columns = ["Cryptocurrency", "Price"]
        df["Date"] = pd.Timestamp.now()  # Add current timestamp
        return df
    else:
        return pd.DataFrame(columns=["Cryptocurrency", "Price", "Date"])

# Streamlit app
def main():
    st.title("Real-Time Cryptocurrency Prices")
    st.sidebar.header("Inputs")

    # Currency selection
    currency = st.sidebar.selectbox('Currency', ['USD', 'EUR', 'GBP'])

    # Load real-time cryptocurrency data
    df = load_real_time_data(currency)
    if df.empty:
        st.error("No data available. Please try again later.")
        st.stop()

    # Display price data
    st.subheader(f'Real-Time Prices of Selected Cryptocurrencies in {currency}')
    st.dataframe(df.set_index("Cryptocurrency"))

    # Bar chart of price data
    st.subheader(f'Price Visualization in {currency}')
    plt.figure(figsize=(10, 6))
    plt.bar(df["Cryptocurrency"], df["Price"], color='skyblue')
    plt.xlabel("Cryptocurrency")
    plt.ylabel(f"Price ({currency})")
    plt.title(f"Real-Time Prices in {currency}")
    st.pyplot(plt)

    # Price Alerts Section
    st.sidebar.subheader("Set Price Alert")
    alert_coin = st.sidebar.selectbox("Select Cryptocurrency for Price Alert", df["Cryptocurrency"])
    alert_price = st.sidebar.number_input(f"Set alert price for {alert_coin} ({currency})", min_value=0.0)

    # Check price alert condition
    if alert_price > 0:
        latest_price = df[df["Cryptocurrency"] == alert_coin]["Price"].iloc[0]
        if latest_price >= alert_price:
            st.sidebar.success(f"Alert! {alert_coin} price is above {alert_price} {currency}. Current price: {latest_price:.2f} {currency}.")
        else:
            st.sidebar.info(f"Current {alert_coin} price is {latest_price:.2f} {currency}. Keep an eye on it.")

# Run the Streamlit app
if __name__ == "__main__":
    main()




















