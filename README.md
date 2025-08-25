# 🌎 Real Time Weather App  

This is an interactive **Weather Monitoring Application** built with **Python** and **Streamlit**. It fetches real-time weather data and 5-day forecasts using the **OpenWeather API** and displays them with a clean UI and charts for better visualization.  

---

## 🚀 Features  
- 🌡 **Real-time Weather Data** – temperature, humidity, sunrise, sunset, and weather condition.  
- 📅 **5-Day Forecast** – daily temperature trends with weather icons.  
- 📊 **Interactive Chart** – line graph for temperature trends.  
- 🎨 **Custom Styling** – modern UI with gradient background and weather cards.  
- 🔄 **Unit Selection** – switch between Celsius and Fahrenheit.  
- 🖼 **Weather Icons** – dynamic icons from OpenWeather for better visualization.  

---

## 🛠 Tech Stack  
- **Python** – Core language  
- **Streamlit** – Web app framework  
- **Requests** – Fetch weather data via API  
- **Matplotlib** – Plot forecast trends  
- **OpenWeather API** – Provides real-time and forecast data  

---

## 🌐 Live Demo  
We have made this project publicly accessible using **Streamlit Hosting**.  
👉 [Try it here](https://python-internship-project-lcvveo38tuahfmjdurju4f.streamlit.app/)  

---
## 📂 Project Structure  
```
📦 Weather-App
┣ 📜 app.py # Main Streamlit application
┣ 📜 README.md # Project documentation
┗ 📜 requirements.txt # Python dependencies
```

## ⚙️ Installation & Setup  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/weather-monitoring-app.git
   cd weather-monitoring-app

2. **Create virtual environment**
   ```bash
   python -m venv venv
  source venv/bin/activate     # Linux/Mac
  venv\Scripts\activate        # Windows

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Add your OpenWeather API key**
   Replace the API key inside app.py with your own from OpenWeather
   ```python
   API_KEY = "your_api_key_here"

5. **Run the app**
   ```bash
   streamlit run app.py

7. **Open the app in your browser at**
   ```
   http://localhost:8501
