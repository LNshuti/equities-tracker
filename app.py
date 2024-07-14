import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from PIL import Image
import io
import streamlit as st
from cachetools import cached, TTLCache

# Global fontsize variable
FONT_SIZE = 32

# ETF ticker mapping
ETF_TICKERS = {
    'iShares Core S&P 500 ETF': 'IVV',
    'iShares Core S&P Total U.S. Stock Market ETF': 'ITOT',
    'iShares Core S&P Small-Cap ETF': 'IJR',
    'iShares Core MSCI Emerging Markets ETF': 'IEMG',
    'iShares Core MSCI EAFE ETF': 'IEFA',
    'iShares Core U.S. Aggregate Bond ETF': 'AGG',
    'iShares Core S&P Mid-Cap ETF': 'IJH',
    'iShares Core Dividend Growth ETF': 'DGRO',
    'iShares Core Total USD Bond Market ETF': 'IUSB',
    'iShares Russell 1000 ETF': 'IWB',
    'iShares Russell 2000 ETF': 'IWM'
}

ETF_FEES = {
    'iShares Core S&P 500 ETF': 0.03,
    'iShares Core S&P Total U.S. Stock Market ETF': 0.03,
    'iShares Core U.S. Aggregate Bond ETF': 0.04,
    'iShares Core S&P Mid-Cap ETF': 0.05,
    'iShares Core S&P Small-Cap ETF': 0.06,
    'iShares Core Total USD Bond Market ETF': 0.06,
    'iShares Core MSCI EAFE ETF': 0.07,
    'iShares Core Dividend Growth ETF': 0.08,
    'iShares Core MSCI Emerging Markets ETF': 0.11,
    'iShares Russell 1000 ETF': 0.15,
    'iShares Russell 2000 ETF': 0.19
}

# Cache with 1-day TTL
cache = TTLCache(maxsize=100, ttl=86400)

@cached(cache)
def fetch_historical_data(ticker, start_date, end_date):
    """Fetch historical ETF data from Yahoo Finance."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

def calculate_returns(data, years):
    """Calculate returns over a specified number of years."""
    end_price = data['Close'][-1]
    start_date = data.index[-1] - timedelta(days=365 * years)
    print("End Date:", data.index[-1])
    print("Start Date:", start_date)
    print("Data Head:\n", data.head())
    
    try:
        nearest_start_date = data.index.asof(start_date)
        start_price = data.loc[nearest_start_date, 'Close']
    except KeyError as ke:
        st.error(f"KeyError in calculate_returns: {ke}")
        raise
    except ValueError as ve:
        st.error(f"ValueError in calculate_returns: {ve}")
        raise
    except Exception as e:
        st.error(f"Unexpected error in calculate_returns: {e}")
        raise

    return (end_price - start_price) / start_price * 100

def plot_to_image(plt, title, fee, five_year_return, ten_year_return):
    """Convert plot to a PIL Image object."""
    plt.title(title, fontsize=FONT_SIZE + 1, pad=40)
    plt.suptitle(f'Expense Ratio: {fee:.2f}%', fontsize=FONT_SIZE - 5, y=0.92, weight='bold')
    plt.legend(fontsize=FONT_SIZE)
    plt.xlabel('Date', fontsize=FONT_SIZE)
    plt.ylabel('Price', fontsize=FONT_SIZE)
    plt.grid(True)
    plt.xticks(rotation=45, ha='right', fontsize=FONT_SIZE)
    plt.yticks(fontsize=FONT_SIZE)
    plt.tight_layout(rect=[0, 0, 1, 0.85])

    plt.figtext(0.5, 0.02, f'5-Year Return: {five_year_return:.2f}%', ha="center", fontsize=FONT_SIZE - 8)
    plt.figtext(0.5, 0.01, f'10-Year Return: {ten_year_return:.2f}%', ha="center", fontsize=FONT_SIZE - 8)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=400)
    plt.close()
    buf.seek(0)
    return Image.open(buf)

def plot_indicator(data, etf_name, ticker, indicator, fee):
    """Plot selected technical indicator for a single ETF."""
    plt.figure(figsize=(16, 10))
    if indicator == "SMA":
        sma_55 = data['Close'].rolling(window=55).mean()
        sma_200 = data['Close'].rolling(window=200).mean()
        plt.plot(data.index, data['Close'], label='Close')
        plt.plot(data.index, sma_55, label='55-day SMA')
        plt.plot(data.index, sma_200, label='200-day SMA')
        plt.ylabel('Price', fontsize=FONT_SIZE)
    elif indicator == "MACD":
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        plt.plot(data.index, macd, label='MACD')
        plt.plot(data.index, signal, label='Signal Line')
        plt.bar(data.index, macd - signal, label='MACD Histogram')
        plt.ylabel('MACD', fontsize=FONT_SIZE)

    five_year_return = calculate_returns(data, 5)
    ten_year_return = calculate_returns(data, 10)

    return plot_to_image(plt, f'{etf_name} ({ticker}) {indicator}', fee, five_year_return, ten_year_return)

def plot_indicators(etf_names, indicator_types):
    """Plot the selected indicators for the selected ETFs."""
    images = []
    if len(etf_names) > 5:
        st.error("You can select up to 5 ETFs at the same time.")
        return None
    if len(etf_names) > 1 and len(indicator_types) > 1:
        st.error("You can only select one indicator when selecting multiple ETFs.")
        return None

    with ThreadPoolExecutor() as executor:
        future_to_etf = {
            executor.submit(fetch_historical_data, ETF_TICKERS[etf], '2000-01-01', datetime.now().strftime('%Y-%m-%d')): (etf, indicator)
            for etf in etf_names
            for indicator in indicator_types
        }

        for future in as_completed(future_to_etf):
            etf, indicator = future_to_etf[future]
            ticker = ETF_TICKERS[etf]
            data = future.result()
            if data is None:
                continue
            images.append(plot_indicator(data, etf, ticker, indicator, ETF_FEES[etf]))

    return images

st.title("ETF Performance and Technical Indicators")

etf_choices = list(ETF_TICKERS.keys())
indicators = ["SMA", "MACD"]

selected_etfs = st.multiselect("Select ETFs", etf_choices)
selected_indicators = st.multiselect("Select Technical Indicators", indicators)

if st.button("Plot Indicators"):
    images = plot_indicators(selected_etfs, selected_indicators)
    if images:
        for img in images:
            st.image(img, use_column_width=True)
