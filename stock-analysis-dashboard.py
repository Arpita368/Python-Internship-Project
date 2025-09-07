import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
from datetime import date

st.set_page_config(page_title="📈 Stock Analysis Dashboard", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #e0f7fa, #e3f2fd, #ede7f6);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3a7bd5, #3a6073);
        color: white;
    }
    section[data-testid="stSidebar"] .stSelectbox label, 
    section[data-testid="stSidebar"] .stDateInput label,
    section[data-testid="stSidebar"] .stButton button {
        color: white !important;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #5DADE2 !important;
        color: white !important;
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #3498DB !important;
    }
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
        color: #2C3E50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color: #148f77;'>📊 Stock Analysis Dashboard</h1>",
    unsafe_allow_html=True,
)

# Sidebar inputs
st.sidebar.header("⚙️ Input Options")
popular_tickers = {
    # US Tech
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "NVIDIA (NVDA)": "NVDA",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    # US Finance
    "JPMorgan (JPM)": "JPM",
    "Goldman Sachs (GS)": "GS",
    "Bank of America (BAC)": "BAC",
    "Wells Fargo (WFC)": "WFC",
    # Global
    "Toyota (TM)": "TM",
    "Samsung (SMSN.L)": "SMSN.L",  # London listing
    "Sony (SONY)": "SONY",
    "Alibaba (BABA)": "BABA",
    "Tencent (TCEHY)": "TCEHY",
    "Nestle (NSRGY)": "NSRGY",
    "Unilever (UL)": "UL",
    "Volkswagen (VWAGY)": "VWAGY",
    "BMW (BMWYY)": "BMWYY",
    # India
    "Reliance (RELIANCE.BSE)": "RELIANCE.BSE",
    "Infosys (INFY.BSE)": "INFY.BSE",
    "TCS (TCS.BSE)": "TCS.BSE",
    "HDFC Bank (HDFCBANK.BSE)": "HDFCBANK.BSE",
    "ICICI Bank (ICICIBANK.BSE)": "ICICIBANK.BSE",
    "State Bank of India (SBIN.BSE)": "SBIN.BSE",
    "Wipro (WIPRO.BSE)": "WIPRO.BSE",
    "HCL Tech (HCLTECH.BSE)": "HCLTECH.BSE",
    # Energy & others
    "ExxonMobil (XOM)": "XOM",
    "Chevron (CVX)": "CVX",
    "Shell (SHEL)": "SHEL",
    "BP (BP)": "BP",
    "TotalEnergies (TTE)": "TTE",
    "Pfizer (PFE)": "PFE",
    "Johnson & Johnson (JNJ)": "JNJ",
    "Procter & Gamble (PG)": "PG",
    "Coca-Cola (KO)": "KO",
    "PepsiCo (PEP)": "PEP",
    "McDonald's (MCD)": "MCD",
    "Disney (DIS)": "DIS",
    "Intel (INTC)": "INTC",
    "AMD (AMD)": "AMD",
    "Oracle (ORCL)": "ORCL",
    "IBM (IBM)": "IBM",
    "Qualcomm (QCOM)": "QCOM",
    "PayPal (PYPL)": "PYPL",
    "Salesforce (CRM)": "CRM",
    "Adobe (ADBE)": "ADBE",
    "Uber (UBER)": "UBER",
    "Zoom (ZM)": "ZM",
}

selected_ticker = st.sidebar.selectbox("Choose a Company:", list(popular_tickers.keys()))
start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())
fetch_btn = st.sidebar.button("🚀 Fetch Data")

API_KEY = "B6BAS1WJ9NKWU756"
ts = TimeSeries(key=API_KEY, output_format="pandas")

custom_template = dict(
    layout=go.Layout(
        font=dict(family="Arial", size=14, color="#2C3E50"),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        title=dict(font=dict(size=20, color="#148f77")),
        xaxis=dict(showgrid=True, gridcolor="#D6DBDF"),
        yaxis=dict(showgrid=True, gridcolor="#D6DBDF"),
    )
)

if not fetch_btn:
    st.info("👋 Welcome! Please select a stock and click **Fetch Data** from the sidebar.")
else:
    try:
        ticker = popular_tickers[selected_ticker]
        data, meta = ts.get_daily(symbol=ticker, outputsize="full")

        data = data.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        df = data.loc[start_date:end_date].copy()

        if df.empty:
            st.error("⚠️ No data available for selected dates.")
        else:
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()
            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))
            df["RSI"].fillna(50, inplace=True)

            tab1, tab2, tab3, tab4 = st.tabs(
                ["📉 Candlestick", "📈 Line Chart", "📊 RSI", "📑 Summary"]
            )

            with tab1:
                st.subheader(f"{ticker} Candlestick Chart")
                fig_candle = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df.index,
                            open=df["Open"],
                            high=df["High"],
                            low=df["Low"],
                            close=df["Close"],
                            increasing_line_color="#2ECC71",
                            decreasing_line_color="#E74C3C",
                        )
                    ]
                )
                fig_candle.update_layout(
                    xaxis_rangeslider_visible=False, template=custom_template
                )
                st.plotly_chart(fig_candle, use_container_width=True)

            with tab2:
                st.subheader(f"{ticker} Closing Price Line Chart")
                fig_line = go.Figure()
                fig_line.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["Close"],
                        mode="lines",
                        name="Close",
                        line=dict(color="#2980B9", width=2),
                    )
                )
                fig_line.update_layout(
                    xaxis_title="Date", yaxis_title="Price", template=custom_template
                )
                st.plotly_chart(fig_line, use_container_width=True)

            with tab3:
                st.subheader(f"{ticker} RSI (14-day)")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(
                    go.Scatter(
                        x=df.index, y=df["RSI"], mode="lines", line=dict(color="#8E44AD", width=2)
                    )
                )
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(
                    xaxis_title="Date", yaxis_title="RSI", template=custom_template
                )
                st.plotly_chart(fig_rsi, use_container_width=True)

            with tab4:
                st.subheader("📌 Performance Summary")
                start_price = float(df["Close"].iloc[0])
                end_price = float(df["Close"].iloc[-1])
                ret = ((end_price / start_price) - 1) * 100
                col1, col2, col3 = st.columns(3)
                col1.metric("Start Price", f"${start_price:.2f}")
                col2.metric("End Price", f"${end_price:.2f}")
                col3.metric("Return %", f"{ret:.2f}%")

            st.download_button(
                label="💾 Download Data as CSV",
                data=df.to_csv().encode("utf-8"),
                file_name=f"{ticker}_stock_data.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
