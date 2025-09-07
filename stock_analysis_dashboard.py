# 📊 Stock Analysis Dashboard
# Tools: yfinance, plotly, pandas, streamlit

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="📊 Stock Analysis Dashboard", layout="wide")
st.title("📊 Stock Analysis Dashboard")

# ---------------------------
# Sidebar Input
# ---------------------------
st.sidebar.header("Stock Input Options")

# Predefined popular tickers
popular_tickers = {
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Infosys (INFY.BO)": "INFY.BO"
}

selected_tickers = st.sidebar.multiselect(
    "Select Companies to Analyze:",
    options=list(popular_tickers.keys()),
    default=["Apple (AAPL)"]
)

start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

if st.sidebar.button("Fetch Data"):
    try:
        tickers = [popular_tickers[name] for name in selected_tickers]

        # ---------------------------
        # Multi-stock comparison (only if >1 stock selected)
        # ---------------------------
        if len(tickers) > 1:
            st.subheader("📊 Multi-Stock Comparison")
            data_all = yf.download(tickers, start=start_date, end=end_date)["Close"]

            if data_all.empty:
                st.error("⚠️ No data found. Please check ticker(s) or date range.")
            else:
                fig_comp = go.Figure()
                for t in data_all.columns:
                    fig_comp.add_trace(go.Scatter(x=data_all.index, y=data_all[t], mode="lines", name=t))
                fig_comp.update_layout(title="Closing Prices Comparison", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig_comp, use_container_width=True)

                st.subheader("📋 Performance Summary")
                summary = {}
                for t in data_all.columns:
                    start_price = float(data_all[t].dropna().iloc[0])
                    end_price = float(data_all[t].dropna().iloc[-1])
                    ret = ((end_price / start_price) - 1) * 100
                    summary[t] = {"Start Price": start_price, "End Price": end_price, "Return %": ret}

                df_summary = pd.DataFrame(summary).T
                st.dataframe(df_summary.style.format({"Start Price": "{:.2f}", "End Price": "{:.2f}", "Return %": "{:.2f}%"}))

        # ---------------------------
        # Single-stock detailed analysis
        # ---------------------------
        if len(tickers) == 1:
            ticker = tickers[0]
            st.subheader(f"🔍 Detailed Analysis for {ticker}")
            data = yf.download(ticker, start=start_date, end=end_date)

            if data.empty:
                st.error("⚠️ No data found for this stock.")
            else:
                # Indicators
                data['SMA20'] = data['Close'].rolling(window=20).mean()
                data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(14).mean()
                avg_loss = loss.rolling(14).mean()
                rs = avg_gain / avg_loss
                data['RSI'] = 100 - (100 / (1 + rs))
                data['RSI'].fillna(50, inplace=True)

                # Tabs
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
                    fig2.add_trace(go.Scatter(x=data.index, y=data['SMA20'], mode='lines', name='SMA20'))
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
                    close_prices = data["Close"].dropna()
                    if not close_prices.empty:
                        start_price = float(close_prices.iloc[0])
                        end_price = float(close_prices.iloc[-1])
                        ret = ((end_price / start_price) - 1) * 100

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Start Price", f"{start_price:.2f}")
                        col2.metric("End Price", f"{end_price:.2f}")
                        col3.metric("Return %", f"{ret:.2f}%")

                # CSV export
                st.download_button(
                    label="💾 Download Data as CSV",
                    data=data.to_csv().encode('utf-8'),
                    file_name=f"{ticker}_stock_analysis.csv",
                    mime="text/csv",
                )

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
