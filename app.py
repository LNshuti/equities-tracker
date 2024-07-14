import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from PIL import Image
import io
from cachetools import cached, TTLCache
import cProfile
import pstats

# Global fontsize variable
FONT_SIZE = 32

# Company ticker mapping
COMPANY_TICKERS = {
    'Gitlab': 'GTLB',
    'Hubspot': 'HUBS',
    'CrowdStrike': 'CRWD',
    'Palantir': 'PLTR',
    'Cloudflare': 'NET',
    'Datadog': 'DDOG',
    'Samsara': 'IOT',
    'ServiceNow': 'NOW',
    'Snowflake': 'SNOW',
    'Palo Alto': 'PANW',
    'Zscaler': 'ZS',
    'Vertex Pharmaceuticals': 'VRTX',
    'TJX Companies': 'TJX',
    'S&P Global': 'SPGI',
    'Republic Services': 'RSG',
    'Regeneron Pharmaceuticals': 'REGN',
    'PNC Financial Services': 'PNC',
    'Philip Morris International': 'PM',
    'Morgan Stanley': 'MS',
    'Altria Group': 'MO',
    'Marsh & McLennan': 'MMC',
    'Moody\'s': 'MCO',
    'Intercontinental Exchange': 'ICE',
    'Goldman Sachs': 'GS',
    'Cintas Corporation': 'CTAS',
    'Bank of America': 'BAC',
    'Apollo Global Management': 'APO',
    'Amgen': 'AMGN',
    'Ecolab': 'ECL',
    'FedEx': 'FDX',
    'Duke Energy': 'DUK',
    'Intuitive Surgical': 'ISRG',
    'Berkshire Hathaway': 'BRK.B',
    'Honeywell International': 'HON',
    'Eli Lilly': 'LLY',
    'Motorola Solutions': 'MSI',
    'JPMorgan Chase': 'JPM',
    'Amphenol Corporation': 'APH',
    'Boston Scientific': 'BSX',
    'Colgate-Palmolive': 'CL',
    'Emerson Electric': 'EMR',
    'AT&T': 'T',
    'Oracle': 'ORCL',
    'Coca-Cola': 'KO',
    'Welltower': 'WELL',
    'American Express': 'AXP',
    'Microsoft': 'MSFT',
    'Salesforce': 'CRM',
    'SAP': 'SAP',
    'Adobe': 'ADBE',
    'Intuit': 'INTU',
    'Synopsys': 'SNPS',
    'Cadence': 'CDNS',
    'Constellation': 'CNC',
    'Workday': 'WDAY',
    'Autodesk': 'ADSK',
    'Atlassian': 'TEAM',
    'Veeva': 'VEEV',
    'WiseTech': 'WTC.AX',
    'PTC': 'PTC',
    'Tyler Tech': 'TYL',
    'Zoom': 'ZM',
    'MongoDB': 'MDB',
    'FactSet': 'FDS',
    'SS&C': 'SSNC',
    'Okta': 'OKTA',
    'Bentley Systems': 'BSY',
    'Manhattan Associates': 'MANH',
    'Dynatrace': 'DT',
    'Sage Group': 'SGE.L',
    'Xero': 'XRO.AX',
    'AspenTech': 'AZPN',
    'Toast': 'TOST',
    'Elastic': 'ESTC',
    'ZoomInfo': 'ZI',
    'Monday.com': 'MNDY',
    'Nice': 'NICE',
    'CyberArk': 'CYBR',
    'Guidewire': 'GWRE',
    'DocuSign': 'DOCU',
    'Procore': 'PCOR',
    'Twilio': 'TWLO',
    'Confluent': 'CFLT',
    'Informatica': 'INFA',
    'Amdocs': 'DOX',
    'Paycom': 'PAYC',
    'Dayforce': 'CSOD',
    'Descartes': 'DSGX',
    'Paylocity': 'PCTY',
    'OpenText': 'OTEX',
    'CCC': 'CCCS',
    'Dropbox': 'DBX',
    'UiPath': 'PATH',
    'SPS Commerce': 'SPSC',
    'HashiCorp': 'HCP',
    'Klaviyo': 'KVYO',
    'Trend Micro': '4704.T',
    'Smartsheet': 'SMAR',
    'Rubrik': 'RUBI',
    'SentinelOne': 'S',
    'Clearwater Analytics': 'CWAN',
    'Vertex': 'VRTX',
    'Darktrace': 'DARK.L',
    'Qualys': 'QLYS',
    'Pegasystems': 'PEGA',
    'Tenable': 'TENB'
}

# Remove duplicates by converting to a set and back to a dictionary
COMPANY_TICKERS = dict(sorted(set(COMPANY_TICKERS.items())))

# Cache with 1-day TTL
cache = TTLCache(maxsize=100, ttl=86400)

@cached(cache)
def fetch_historical_data(ticker, start_date, end_date):
    """Fetch historical stock data and market cap from Yahoo Finance."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        info = yf.Ticker(ticker).info
        market_cap = info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = market_cap / 1e9  # Convert to billions
        return data, market_cap
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None, 'N/A'

def calculate_trailing_annual_returns(data):
    """Calculate trailing annual returns from stock data using log returns."""
    data['Daily Return'] = data['Close'].pct_change()
    data['Log Return'] = np.log1p(data['Daily Return'])
    data['Annual Log Return'] = data['Log Return'].rolling(window=252).sum()
    data['Annual Return'] = np.expm1(data['Annual Log Return'])
    return data['Annual Return']

def plot_to_image(plt, title, market_cap):
    """Convert plot to a PIL Image object."""
    plt.title(title, fontsize=FONT_SIZE + 1, pad=40)
    plt.suptitle(f'Market Cap: ${market_cap:.2f} Billion', fontsize=FONT_SIZE - 5, y=0.92, weight='bold')
    plt.legend(fontsize=FONT_SIZE)
    plt.xlabel('Date', fontsize=FONT_SIZE)
    plt.ylabel('', fontsize=FONT_SIZE)
    plt.grid(True)
    plt.xticks(rotation=45, ha='right', fontsize=FONT_SIZE)
    plt.yticks(fontsize=FONT_SIZE)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=400)
    plt.close()
    buf.seek(0)
    return Image.open(buf)

def plot_indicator(data, company_name, ticker, indicator, market_cap):
    """Plot selected technical indicator for a single company."""
    plt.figure(figsize=(16, 10))
    if indicator == "Trailing Annual Returns":
        annual_returns = calculate_trailing_annual_returns(data)
        plt.plot(annual_returns.index, annual_returns, label='Trailing Annual Return', alpha=0.8, linewidth=1.5)
        plt.ylabel('Trailing Annual Return', fontsize=FONT_SIZE)
        plt.ylim(annual_returns.min(), annual_returns.max())
    elif indicator == "SMA":
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

    return plot_to_image(plt, f'{company_name} ({ticker}) {indicator}', market_cap)

def plot_indicators(company_names, indicator_types):
    """Plot the selected indicators for the selected companies."""
    images = []
    if len(company_names) > 1 and len(indicator_types) > 1:
        return None, "You can only select one indicator when selecting multiple companies."

    with ThreadPoolExecutor() as executor:
        future_to_company = {
            executor.submit(fetch_historical_data, COMPANY_TICKERS[company], '2000-01-01', datetime.now().strftime('%Y-%m-%d')): (company, indicator)
            for company in company_names
            for indicator in indicator_types
        }

        for future in as_completed(future_to_company):
            company, indicator = future_to_company[future]
            ticker = COMPANY_TICKERS[company]
            data, market_cap = future.result()
            if data is None:
                continue
            images.append(plot_indicator(data, company, ticker, indicator, market_cap))

    return images, ""

def select_all_indicators(select_all):
    """Select or deselect all indicators based on the select_all flag."""
    indicators = ["SMA", "MACD", "Trailing Annual Returns"]
    return indicators if select_all else []

def main():
    """Main function to launch the Streamlit app."""
    st.title("Stock Analysis and Visualization")

    company_choices = list(COMPANY_TICKERS.keys())
    indicators = ["SMA", "MACD", "Trailing Annual Returns"]

    selected_companies = st.multiselect("Select Companies", company_choices)
    select_all = st.checkbox("Select All Indicators")
    if select_all:
        selected_indicators = indicators
    else:
        selected_indicators = st.multiselect("Select Technical Indicators", indicators)

    if st.button("Plot Indicators"):
        if not selected_companies or not selected_indicators:
            st.error("Please select at least one company and one indicator.")
        else:
            images, error_message = plot_indicators(selected_companies, selected_indicators)
            if error_message:
                st.error(error_message)
            else:
                for img in images:
                    st.image(img)

if __name__ == "__main__":
    main()
