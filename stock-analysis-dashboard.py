import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
from datetime import date

# Page config
st.set_page_config(page_title="📈 Stock Analysis Dashboard", layout="wide")

st.markdown("""
    <style>
        /* Background Gradient */
        body {
            background: linear-gradient(135deg, #d9f2ff, #ffffff);
            color: #111111; /* Dark text */
        }
        
        /* Sidebar background */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #e6f0ff, #ffffff);
            color: #111111;
        }
        
        /* Sidebar labels, headers, etc. */
        .sidebar .sidebar-content h2,
        .sidebar .sidebar-content label,
        .sidebar .sidebar-content span,
        .sidebar .sidebar-content div {
            color: #111111 !important;
            font-weight: bold;
        }

        /* App title */
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #111111 !important;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(to right, #06beb6, #48b1bf);
            color: #111111;
            border-radius: 12px;
            padding: 0.6em 1.2em;
            font-weight: bold;
            border: 1px solid #333333;
        }
    </style>
""", unsafe_allow_html=True)


# Title
st.markdown("<h1 style='text-align: center; color: #ffffff;'>📊 Stock Analysis Dashboard</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Input Options")

popular_tickers = {
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Intel (INTC)": "INTC",
    "Adobe (ADBE)": "ADBE",
    "PayPal (PYPL)": "PYPL",
    "Salesforce (CRM)": "CRM",
    "IBM (IBM)": "IBM",
    "Qualcomm (QCOM)": "QCOM",
    "Oracle (ORCL)": "ORCL",
    "Coca-Cola (KO)": "KO",
    "PepsiCo (PEP)": "PEP",
    "McDonald's (MCD)": "MCD",
    "Walmart (WMT)": "WMT",
    "Nike (NKE)": "NKE",
    "Starbucks (SBUX)": "SBUX",
    "Disney (DIS)": "DIS",
    "Ford (F)": "F",
    "General Motors (GM)": "GM",
    "Boeing (BA)": "BA",
    "ExxonMobil (XOM)": "XOM",
    "Chevron (CVX)": "CVX",
    "Pfizer (PFE)": "PFE",
    "Johnson & Johnson (JNJ)": "JNJ",
    "Reliance (RELIANCE.NS)": "RELIANCE.NS",
    "TCS (TCS.NS)": "TCS.NS",
    "Infosys (INFY.NS)": "INFY.NS",
    "HDFC Bank (HDFCBANK.NS)": "HDFCBANK.NS",
    "ICICI Bank (ICICIBANK.NS)": "ICICIBANK.NS",
    "State Bank of India (SBIN.NS)": "SBIN.NS",
    "Bharti Airtel (BHARTIARTL.NS)": "BHARTIARTL.NS",
    "Hindustan Unilever (HINDUNILVR.NS)": "HINDUNILVR.NS",
    "Adani Enterprises (ADANIENT.NS)": "ADANIENT.NS",
    "Wipro (WIPRO.NS)": "WIPRO.NS",
    "Bajaj Finance (BAJFINANCE.NS)": "BAJFINANCE.NS",
    "Toyota (TM)": "TM",
    "Samsung Electronics (SMSN.IL)": "SMSN.IL",
    "Sony (SONY)": "SONY",
    "Alibaba (BABA)": "BABA",
    "Taiwan Semiconductor (TSM)": "TSM",
    "Roche (RHHBY)": "RHHBY",
    "Nestle (NSRGY)": "NSRGY",
    "HSBC (HSBC)": "HSBC",
    "Barclays (BCS)": "BCS",
}

selected_ticker = st.sidebar.selectbox("Choose a Company:", ["-- Select a Stock --"] + list(popular_tickers.keys()))

start_date = st.sidebar.date_input(
    "Start Date",
    value=None,
    min_value=date(2000, 1, 1),
    max_value=date.today(),
    help="Select start date (YYYY-MM-DD)"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=None,
    min_value=date(2000, 1, 1),
    max_value=date.today(),
    help="Select end date (YYYY-MM-DD)"
)

fetch_btn = st.sidebar.button("🚀 Fetch Data")

# API
API_KEY = "B6BAS1WJ9NKWU756"  # Replace with your Alpha Vantage API key
ts = TimeSeries(key=API_KEY, output_format='pandas')

# Main content
if fetch_btn and selected_ticker != "-- Select a Stock --":
    try:
        ticker = popular_tickers[selected_ticker]
        data, meta = ts.get_daily(symbol=ticker, outputsize='full')

        data = data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })

        data.index = pd.to_datetime(data.index)
        data = data.sort_index()

        if start_date and end_date:
            df = data.loc[str(start_date):str(end_date)].copy()
        else:
            df = data.copy()

        if df.empty:
            st.error("⚠️ No data available for selected dates.")
        else:
            # RSI calculation
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            df['RSI'].fillna(50, inplace=True)

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📉 Candlestick", "📈 Line Chart", "📊 RSI", "📑 Summary"])

            with tab1:
                st.subheader(f"{ticker} Candlestick Chart")
                fig_candle = go.Figure(data=[go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close']
                )])
                fig_candle.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
                st.plotly_chart(fig_candle, use_container_width=True)

            with tab2:
                st.subheader(f"{ticker} Closing Price Line Chart")
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(color="cyan")))
                fig_line.update_layout(xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
                st.plotly_chart(fig_line, use_container_width=True)

            with tab3:
                st.subheader(f"{ticker} RSI (14-day)")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', line=dict(color="violet")))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(xaxis_title="Date", yaxis_title="RSI", template="plotly_dark")
                st.plotly_chart(fig_rsi, use_container_width=True)

            with tab4:
                st.subheader("📌 Performance Summary")
                start_price = float(df['Close'].iloc[0])
                end_price = float(df['Close'].iloc[-1])
                ret = ((end_price / start_price) - 1) * 100
                col1, col2, col3 = st.columns(3)
                col1.metric("Start Price", f"${start_price:.2f}")
                col2.metric("End Price", f"${end_price:.2f}")
                col3.metric("Return %", f"{ret:.2f}%")

            st.download_button(
                label="💾 Download Data as CSV",
                data=df.to_csv().encode('utf-8'),
                file_name=f"{ticker}_stock_data.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")

else:
    st.info("👋 Welcome! Please select a stock and date range from the sidebar to view analysis.")
