# 📊 Stock Analysis Dashboard (Streamlit + Plotly Graph Objects)

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import streamlit as st

# Streamlit Page Config
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")
st.title("📈 Stock Analysis Dashboard")

# Sidebar Inputs
st.sidebar.header("Stock Input Options")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, INFY.BO):", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Fetch Data
if st.sidebar.button("Fetch Data"):
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        st.error("❌ No data found. Please check ticker symbol or date range.")
    else:
        st.success(f"✅ Fetched {len(data)} rows of data for {ticker}")

        # ---------------------------
        # Technical Indicators
        # ---------------------------
        data["SMA20"] = data["Close"].rolling(window=20).mean()
        data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()

        # RSI
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # ---------------------------
        # Tabs for Visualization
        # ---------------------------
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Candlestick", "📉 SMA & EMA", "📈 RSI", "📑 Summary"])

        # Candlestick Chart
        with tab1:
            fig1 = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick"
            )])
            fig1.update_layout(title=f"{ticker} Candlestick Chart",
                               xaxis_rangeslider_visible=False,
                               template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

        # SMA & EMA Chart
        with tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=data.index, y=data['Close'],
                                      mode='lines', name='Close'))
            fig2.add_trace(go.Scatter(x=data.index, y=data['SMA20'],
                                      mode='lines', name='SMA20'))
            fig2.add_trace(go.Scatter(x=data.index, y=data['EMA20'],
                                      mode='lines', name='EMA20'))
            fig2.update_layout(title=f"{ticker} Closing Price with SMA & EMA",
                               template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        # RSI Chart
        with tab3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=data.index, y=data['RSI'],
                                      mode='lines', name='RSI'))
            fig3.add_hline(y=70, line_dash="dash", line_color="red")
            fig3.add_hline(y=30, line_dash="dash", line_color="green")
            fig3.update_layout(title=f"{ticker} RSI (14-day)", template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

        # Performance Summary
        with tab4:
            st.subheader("📑 Performance Summary")
            st.metric("Start Price", f"{data['Close'].iloc[0]:.2f}")
            st.metric("End Price", f"{data['Close'].iloc[-1]:.2f}")
            st.metric("Return (%)", f"{((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100:.2f}")
            st.metric("Latest RSI", f"{data['RSI'].iloc[-1]:.2f}")

        # ---------------------------
        # CSV Export
        # ---------------------------
        csv = data.to_csv().encode("utf-8")
        st.download_button("📥 Download Data as CSV", csv,
                           f"{ticker}_data.csv", "text/csv")
