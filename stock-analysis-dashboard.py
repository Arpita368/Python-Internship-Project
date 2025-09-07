import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")
st.title("Stock Analysis Dashboard")

st.sidebar.header("Stock Input Options")
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

        if len(tickers) == 1:
            ticker = tickers[0]
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, threads=False)
            if data.empty:
                st.error("No data found for this stock.")
            else:
                data.index = pd.to_datetime(data.index)

                # RSI calculation
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(14).mean()
                avg_loss = loss.rolling(14).mean()
                rs = avg_gain / avg_loss
                data['RSI'] = 100 - (100 / (1 + rs))
                data['RSI'].fillna(50, inplace=True)

                tab1, tab2, tab3, tab4 = st.tabs(["Closing Price", "Volume", "RSI", "Summary"])

                # Closing price line chart
                with tab1:
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
                    fig1.update_layout(title=f"{ticker} Closing Price Trend")
                    st.plotly_chart(fig1, use_container_width=True)

                # Volume chart
                with tab2:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=data.index, y=data['Volume'], name="Volume"))
                    fig2.update_layout(title=f"{ticker} Trading Volume")
                    st.plotly_chart(fig2, use_container_width=True)

                # RSI chart
                with tab3:
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'))
                    fig3.add_hline(y=70, line_dash="dash", line_color="red")
                    fig3.add_hline(y=30, line_dash="dash", line_color="green")
                    fig3.update_layout(title=f"{ticker} RSI (14-day)")
                    st.plotly_chart(fig3, use_container_width=True)

                # Summary
                with tab4:
                    close_prices = data['Close'].dropna()
                    start_price = float(close_prices.iloc[0])
                    end_price = float(close_prices.iloc[-1])
                    ret = ((end_price / start_price) - 1) * 100
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Start Price", f"{start_price:.2f}")
                    col2.metric("End Price", f"{end_price:.2f}")
                    col3.metric("Return %", f"{ret:.2f}%")

                # CSV export
                st.download_button(
                    label="Download Data as CSV",
                    data=data.to_csv().encode('utf-8'),
                    file_name=f"{ticker}_stock_analysis.csv",
                    mime="text/csv",
                )

        elif len(tickers) > 1:
            st.subheader("Multi-Stock Comparison")
            data_all = yf.download(tickers, start=start_date, end=end_date, progress=False, threads=False)['Close']
            if not data_all.empty:
                fig_comp = go.Figure()
                for t in data_all.columns:
                    fig_comp.add_trace(go.Scatter(x=data_all.index, y=data_all[t], mode='lines', name=t))
                fig_comp.update_layout(title="Closing Prices Comparison", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig_comp, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
