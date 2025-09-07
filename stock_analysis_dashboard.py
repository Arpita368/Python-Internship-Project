# 📊 Stock Analysis Dashboard
# Tools: yfinance, plotly, pandas, streamlit

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="📊 Stock Analysis Dashboard", layout="wide")

st.title("📊 Stock Analysis Dashboard")

# ---------------------------
# Sidebar Input
# ---------------------------
st.sidebar.header("Stock Input Options")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, INFY.BO):", "AAPL").upper()
start_date = st.sidebar.text_input("Start Date", "2023-01-01")
end_date = st.sidebar.text_input("End Date", "2025-09-07")

if st.sidebar.button("Fetch Data"):
    # ---------------------------
    # Fetch historical data
    # ---------------------------
    try:
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ No data found. Please check ticker or date range.")
        else:
            st.success(f"✅ Fetched {len(data)} rows of data for {ticker}")

            # ---------------------------
            # Indicators: SMA, EMA, RSI
            # ---------------------------
            data['SMA20'] = data['Close'].rolling(window=20).mean()
            data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()

            delta = data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            data['RSI'] = 100 - (100 / (1 + rs))

            # ---------------------------
            # Tabs for charts & summary
            # ---------------------------
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Candlestick", "📊 SMA & EMA", "📉 RSI", "📋 Summary"])

            # --- Candlestick ---
            with tab1:
                fig1 = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name="Candlestick"
                )])
                fig1.update_layout(title=f"{ticker} Candlestick Chart", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig1, use_container_width=True)

            # --- SMA & EMA ---
            with tab2:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
                if data['SMA20'].notna().sum() > 0:
                    fig2.add_trace(go.Scatter(x=data.index, y=data['SMA20'], mode='lines', name='SMA20'))
                if data['EMA20'].notna().sum() > 0:
                    fig2.add_trace(go.Scatter(x=data.index, y=data['EMA20'], mode='lines', name='EMA20'))
                fig2.update_layout(title=f"{ticker} Closing Price with SMA & EMA")
                st.plotly_chart(fig2, use_container_width=True)

            # --- RSI ---
            with tab3:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'))
                fig3.add_hline(y=70, line_dash="dash", line_color="red")
                fig3.add_hline(y=30, line_dash="dash", line_color="green")
                fig3.update_layout(title=f"{ticker} RSI (14-day)")
                st.plotly_chart(fig3, use_container_width=True)

            # --- Summary ---
            with tab4:
                if not data.empty and "Close" in data:
                    close_prices = data["Close"].dropna()
                    if not close_prices.empty:
                        start_price = close_prices.iloc[0]
                        end_price = close_prices.iloc[-1]
                        ret = ((end_price / start_price) - 1) * 100

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Start Price", f"{start_price:.2f}")
                        col2.metric("End Price", f"{end_price:.2f}")
                        col3.metric("Return %", f"{ret:.2f}%")
                    else:
                        st.warning("⚠️ No valid closing prices to summarize.")
                else:
                    st.warning("⚠️ No valid stock data available for summary.")

            # ---------------------------
            # CSV Export Option
            # ---------------------------
            st.download_button(
                label="💾 Download Data as CSV",
                data=data.to_csv().encode('utf-8'),
                file_name=f"{ticker}_stock_analysis.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
