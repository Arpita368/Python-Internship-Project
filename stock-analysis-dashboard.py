import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("Stock Analysis Dashboard")

ticker = st.text_input("Enter Stock Ticker", "AAPL")
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2023-06-30"))

if st.button("Fetch Data"):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False, threads=False)

    if data.empty:
        st.error("No data found. Adjust ticker or dates.")
    else:
        data.reset_index(inplace=True)

        # RSI calculation replacement for SMA/EMA
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # Line chart for Close price
        fig_close = px.line(data, x='Date', y='Close', title=f"{ticker} Closing Price Trend")
        st.plotly_chart(fig_close, use_container_width=True)

        # RSI line chart
        fig_rsi = px.line(data, x='Date', y='RSI', title=f"{ticker} RSI (Relative Strength Index)")
        st.plotly_chart(fig_rsi, use_container_width=True)

        # Performance summary
        perf = {
            "Start Price": data['Close'].iloc[0],
            "End Price": data['Close'].iloc[-1],
            "Change": data['Close'].iloc[-1] - data['Close'].iloc[0],
            "Return %": ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        }
        st.write("Performance Summary", perf)

        # CSV export
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, file_name=f"{ticker}_data.csv", mime="text/csv")
