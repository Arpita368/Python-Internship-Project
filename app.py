import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Weather App", page_icon="⛅", layout="centered")

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(to bottom, #1e293b, #0f172a);
            color: #f1f5f9;
        }
        .big-font {
            font-size:20px !important;
            color: #f8fafc;
        }
        .weather-card {
            background-color: rgba(255, 255, 255, 0.1);
            color: #f8fafc; 
            padding: 15px;
            border-radius: 12px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.5);
            margin-bottom: 10px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #f8fafc;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🌎 Weather Monitoring App")

# Sidebar
st.sidebar.header("User Input")
city = st.sidebar.text_input("Enter the location:", "")
unit = st.sidebar.radio("Choose the unit", ["Celsius", "Fahrenheit"])

API_KEY = "cfc8d77b4a731bcb04aaed0e7fc78aa8"

# Functions
def get_weather(city, unit_label):
    units = "metric" if unit_label == "Celsius" else "imperial"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": units}
    return requests.get(url, params=params, timeout=10).json()

def get_forecast(city, unit_label):
    units = "metric" if unit_label == "Celsius" else "imperial"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": units}
    return requests.get(url, params=params, timeout=10).json()

def format_local_time(unix_ts, tz_offset_seconds):
    return datetime.utcfromtimestamp(unix_ts + tz_offset_seconds).strftime("%I:%M %p")

# Main Section 
if st.sidebar.button("Get Weather"):
    data = get_weather(city, unit)

    if str(data.get("cod")) != "200":
        st.error(data.get("message", "City not found!").title())
    else:
        tz_offset = data.get("timezone", 0)
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        sunrise = format_local_time(data["sys"]["sunrise"], tz_offset)
        sunset  = format_local_time(data["sys"]["sunset"], tz_offset)
        desc = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]

        # Current Weather
        st.subheader(f"Weather in {data['name']}")
        st.markdown(f"<h3>{desc}</h3>", unsafe_allow_html=True)
        st.image(f"http://openweathermap.org/img/wn/{icon}@4x.png")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='weather-card'>🌡 <b>Temperature:</b> {temp}° {unit}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='weather-card'>💧 <b>Humidity:</b> {humidity}%</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='weather-card'>🌅 <b>Sunrise:</b> {sunrise}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='weather-card'>🌇 <b>Sunset:</b> {sunset}</div>", unsafe_allow_html=True)

        # Forecast Section
        forecast = get_forecast(city, unit)
        if str(forecast.get("cod")) == "200":
            st.subheader("📅 5-Day Forecast")

            days, temps, icons = [], [], []
            for i in range(0, len(forecast["list"]), 8):  # pick one reading per day
                dt_txt = forecast["list"][i]["dt_txt"]
                day = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").strftime("%a")
                days.append(day)
                temps.append(forecast["list"][i]["main"]["temp"])
                icons.append(forecast["list"][i]["weather"][0]["icon"])

            cols = st.columns(len(days))
            for i, col in enumerate(cols):
                with col:
                    st.markdown(f"<div class='weather-card'><b>{days[i]}</b></div>", unsafe_allow_html=True)
                    st.image(f"http://openweathermap.org/img/wn/{icons[i]}.png", width=60)
                    st.write(f"{temps[i]}° {unit}")

            # Chart
            fig, ax = plt.subplots()
            ax.plot(days, temps, marker="o", color="dodgerblue", linewidth=2)
            ax.set_title("Temperature Trend (Next 5 Days)", fontsize=14, weight="bold")
            ax.set_ylabel(f"Temperature ({unit})")
            ax.grid(True, linestyle="--", alpha=0.6)
            st.pyplot(fig)

