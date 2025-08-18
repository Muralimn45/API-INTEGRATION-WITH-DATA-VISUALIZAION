# --- Live Weather Dashboard Web App (app.py) ---
# This Flask application serves a web page that displays a live, updating
# weather dashboard using data from the OpenWeatherMap API. The plots are
# generated using Matplotlib and served as images.

# --- Library Imports ---
from flask import Flask, render_template_string, request, session
import requests
import sys
import matplotlib

# Use the Agg backend for Matplotlib to prevent GUI errors in non-GUI environments.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
import os  # We'll use this to get a secure random key

# --- Flask App Initialization ---
app = Flask(__name__)
# Set a secret key for the application to enable sessions.
# A session is needed to remember the last searched city across page refreshes.
app.secret_key = os.urandom(24)

# --- API Configuration ---
# IMPORTANT: This API key is used to fetch current weather data from OpenWeatherMap.
# You can get your own free key from https://openweathermap.org/api.
API_KEY = "018ecddd8ef7f830fb239f1edd238b9e"
# Base URL for current weather data.
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
# Base URL for 5-day forecast data.
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Global data storage for the live graphs.
timestamps = []
temperatures = []
humidity = []
wind_speed = []
pressure = []


# --- Function Definitions ---
def get_weather_data(api_url, city_name):
    """
    Fetches weather data from a given OpenWeatherMap API endpoint.

    Args:
        api_url (str): The URL of the API endpoint.
        city_name (str): The name of the city to fetch data for.

    Returns:
        dict or None: A dictionary with the weather data or None on failure.
    """
    if API_KEY == "YOUR_VALID_API_KEY_HERE":
        print("ERROR: Please replace 'YOUR_VALID_API_KEY_HERE' with your actual API key.", file=sys.stderr)
        return None

    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"  # Request temperature in Celsius.
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to retrieve weather data from {api_url}. {e}", file=sys.stderr)
        return None


def get_weather_forecast(city_name):
    """
    Fetches and processes the 5-day weather forecast.

    Args:
        city_name (str): The name of the city for the forecast.

    Returns:
        list: A list of dictionaries, each containing forecast data for a day.
    """
    forecast_data = get_weather_data(FORECAST_URL, city_name)
    if not forecast_data:
        return []

    daily_forecasts = {}
    today = datetime.now().date()

    for item in forecast_data['list']:
        # Get the timestamp and date for each forecast item
        dt = datetime.fromtimestamp(item['dt'])
        date_key = dt.date()

        # We are only interested in a few days ahead, so we'll skip the current day.
        # We also limit to the next 4 days for the forecast cards.
        if date_key > today and len(daily_forecasts) < 4:
            if date_key not in daily_forecasts:
                # Initialize data for a new day
                daily_forecasts[date_key] = {
                    'temps': [],
                    'weather_counts': {},
                    'date': dt
                }

            # Store temperature and count weather conditions for the day
            daily_forecasts[date_key]['temps'].append(item['main']['temp'])
            weather_main = item['weather'][0]['main']
            daily_forecasts[date_key]['weather_counts'][weather_main] = \
                daily_forecasts[date_key]['weather_counts'].get(weather_main, 0) + 1

    # Process the collected daily data
    processed_forecast = []
    for date_key, data in daily_forecasts.items():
        # Get the average temperature for the day
        avg_temp = sum(data['temps']) / len(data['temps'])
        # Determine the most common weather condition for the day
        most_common_weather = max(data['weather_counts'], key=data['weather_counts'].get)

        processed_forecast.append({
            'date': data['date'].strftime("%b %d"),
            'temp': int(round(avg_temp)),
            'weather_main': most_common_weather
        })

    return processed_forecast


def get_weather_icon(weather_main):
    """
    Maps a weather condition string to a specific SVG icon.

    Args:
        weather_main (str): The main weather condition from the API (e.g., 'Clear', 'Clouds').

    Returns:
        str: An HTML string with the appropriate SVG icon.
    """
    icons = {
        "Clear": """
            <svg class="h-full w-full" fill="#fddb00" viewBox="0 0 24 24">
                <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            """,
        "Clouds": """
            <svg class="h-full w-full" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18 10h-1.26a8 8 0 1 0-16.34 0h1.26"/>
                <path d="M22 17h-1.26a8 8 0 1 0-16.34 0h1.26"/>
            </svg>
            """,
        "Rain": """
            <svg class="h-full w-full" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 8a4 4 0 014 4v2a2 2 0 01-2 2h-2a4 4 0 01-4-4h2a2 2 0 012-2v-2" />
            </svg>
            """,
        "Drizzle": """
            <svg class="h-full w-full" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm0 9a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" />
            </svg>
        """,
        "Thunderstorm": """
            <svg class="h-full w-full" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
        """,
        "Snow": """
            <svg class="h-full w-full" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 19V5M5 12h14" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 19L5 5M5 19l14-14" />
            </svg>
        """
    }
    # Return a cloud icon for any unhandled weather conditions.
    return icons.get(weather_main, icons["Clouds"])


def update_live_data(city_name):
    """
    Fetches new data and appends it to the global lists for live visualization.
    """
    data = get_weather_data(CURRENT_WEATHER_URL, city_name)
    if data and 'main' in data and 'wind' in data:
        current_temp = data['main']['temp']
        current_humidity = data['main']['humidity']
        current_wind_speed = data['wind']['speed']
        current_pressure = data['main']['pressure']
        current_time = datetime.now()

        # Append new data points.
        timestamps.append(current_time)
        temperatures.append(current_temp)
        humidity.append(current_humidity)
        wind_speed.append(current_wind_speed)
        pressure.append(current_pressure)

        # Keep only the last 60 data points for better visibility.
        if len(timestamps) > 60:
            timestamps.pop(0)
            temperatures.pop(0)
            humidity.pop(0)
            wind_speed.pop(0)
            pressure.pop(0)
    else:
        print("Failed to retrieve current weather data. Keeping existing data.", file=sys.stderr)


def create_plot(city_name):
    """
    Creates the weather dashboard plot and returns it as a base64-encoded string.
    """
    # Use a modern, light seaborn style that fits the glassmorphism theme
    sns.set_style("whitegrid")

    # Create a figure with four subplots.
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"Live Weather Data for {city_name}", fontsize=24, weight='bold', y=0.95, color='#4a5568')

    # --- Plot 1: Temperature ---
    ax1.plot(timestamps, temperatures, color='#f56565', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax1.set_title("Temperature (°C)", fontsize=16, weight='bold', color='#4a5568')
    ax1.set_ylabel("Temp (°C)", fontsize=14, color='#718096')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.tick_params(colors='#718096')

    # --- Plot 2: Humidity ---
    ax2.plot(timestamps, humidity, color='#48bb78', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax2.set_title("Humidity (%)", fontsize=16, weight='bold', color='#4a5568')
    ax2.set_ylabel("Humidity (%)", fontsize=14, color='#718096')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.tick_params(colors='#718096')

    # --- Plot 3: Wind Speed ---
    ax3.plot(timestamps, wind_speed, color='#667eea', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax3.set_title("Wind Speed (m/s)", fontsize=16, weight='bold', color='#4a5568')
    ax3.set_ylabel("Wind Speed (m/s)", fontsize=14, color='#718096')
    ax3.set_xlabel("Time", fontsize=14, color='#718096')
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.tick_params(colors='#718096')
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')

    # --- Plot 4: Atmospheric Pressure ---
    ax4.plot(timestamps, pressure, color='#f6ad55', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax4.set_title("Atmospheric Pressure (hPa)", fontsize=16, weight='bold', color='#4a5568')
    ax4.set_ylabel("Pressure (hPa)", fontsize=14, color='#718096')
    ax4.set_xlabel("Time", fontsize=14, color='#718096')
    ax4.grid(True, linestyle='--', alpha=0.6)
    ax4.tick_params(colors='#718096')
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')

    # General figure and layout adjustments
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the plot to a BytesIO object.
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', transparent=True)
    plt.close(fig)  # Close the figure to free up memory.
    img_stream.seek(0)

    # Encode the image data to base64.
    return base64.b64encode(img_stream.getvalue()).decode('utf-8')


# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route to display the weather dashboard.
    """
    global timestamps, temperatures, humidity, wind_speed, pressure

    # Check if a city was submitted via the form
    if request.method == "POST":
        city_name = request.form.get("city")
        session['city'] = city_name
        # Clear data on new city search to prevent mixed graphs
        timestamps.clear()
        temperatures.clear()
        humidity.clear()
        wind_speed.clear()
        pressure.clear()
    else:
        city_name = session.get('city', 'Dnipro, Ukraine')

    # Update data with the remembered city name.
    update_live_data(city_name)
    current_weather_data = get_weather_data(CURRENT_WEATHER_URL, city_name)

    # Extract data with safe access
    if current_weather_data:
        current_temp = current_weather_data['main']['temp']
        current_humidity = current_weather_data['main']['humidity']
        current_wind_speed = current_weather_data['wind']['speed']
        current_pressure = current_weather_data['main']['pressure']
        current_weather_description = current_weather_data['weather'][0]['description']
        current_weather_main = current_weather_data['weather'][0]['main']
        location_display = f"{current_weather_data['name']}, {current_weather_data['sys']['country']}"
    else:
        # Fallback values if API call fails
        current_temp = 'N/A'
        current_humidity = 'N/A'
        current_wind_speed = 'N/A'
        current_pressure = 'N/A'
        current_weather_description = 'N/A'
        current_weather_main = 'N/A'
        location_display = city_name

    current_date = datetime.now().strftime("%B %d")
    current_day = datetime.now().strftime("%A")
    current_icon_svg = get_weather_icon(current_weather_main)

    forecast_list = get_weather_forecast(city_name)

    # Generate the plot image.
    plot_image_base64 = create_plot(city_name)

    # The HTML template with the new glassmorphism visual design.
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Dashboard</title>
        <meta http-equiv="refresh" content="15"> <!-- Auto-refresh every 15 seconds -->
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background-color: #e0e7ff;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #555;
            }
            .glass-container {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
                padding: 3rem;
                display: flex;
                flex-direction: column;
                gap: 2rem;
                max-width: 900px;
                width: 90%;
            }
            .icon-box {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
                padding: 1rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
            .glass-input {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
                padding: 0.75rem 1.5rem;
                color: #555;
                font-size: 1rem;
                outline: none;
                width: 100%;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
                transition: box-shadow 0.2s;
            }
            .glass-input:focus {
                box-shadow: 0 0 0 2px rgba(255,255,255,0.5), inset 0 2px 4px rgba(0,0,0,0.15);
            }
            .icon-main-container {
                width: 180px;
                height: 180px;
                background-color: #a4b0d8;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            }
            .main-icon-svg {
                width: 100px;
                height: 100px;
            }
            .main-temp {
                font-size: 4rem;
                font-weight: 300;
                display: flex;
                align-items: flex-start;
                line-height: 1;
            }
            .main-temp .celsius-deg {
                font-size: 2rem;
            }
            .details-list li {
                display: flex;
                justify-content: space-between;
                font-size: 0.9rem;
                padding: 0.25rem 0;
            }
            .glass-chart {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
                padding: 1rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
            .graph-image {
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
        </style>
    </head>
    <body class="bg-gray-200">
        <div class="glass-container">
            <div class="flex justify-center mb-4">
                <form id="city-form" method="post" class="w-full">
                    <input type="text" id="city-input" name="city" value="{{ city_name }}" placeholder="Search city..." class="glass-input">
                </form>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 items-center">
                <!-- Left Section: Current Weather Details -->
                <div class="flex flex-col">
                    <div class="flex items-center mb-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-1 text-gray-700" viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm0 9a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" clip-rule="evenodd" />
                        </svg>
                        <h2 class="text-xl font-semibold">{{ location_display }}</h2>
                    </div>
                    <div class="text-sm font-medium">{{ current_date }}</div>
                    <div class="text-sm font-medium">{{ current_day }}</div>
                    <div class="flex items-start mt-4">
                        <div class="main-temp">{{ "%.0f"|format(current_temp) if current_temp != 'N/A' else 'N/A' }}</div>
                        <div class="main-temp text-3xl font-normal ml-2">°C</div>
                    </div>
                </div>

                <!-- Right Section: Icon and Details -->
                <div class="flex flex-col items-center justify-center">
                    <div class="icon-main-container mb-4">
                        {{ current_icon_svg|safe }}
                    </div>
                     <div class="mt-4 text-center">
                        <p class="text-sm font-medium">Pressure: {{ "%.0f"|format(current_pressure) if current_pressure != 'N/A' else 'N/A' }} hPa</p>
                        <p class="text-sm font-medium">Humidity: {{ "%.0f"|format(current_humidity) if current_humidity != 'N/A' else 'N/A' }}%</p>
                        <p class="text-sm font-medium">Wind: {{ "%.1f"|format(current_wind_speed) if current_wind_speed != 'N/A' else 'N/A' }} m/s</p>
                    </div>
                </div>
            </div>

            <!-- Graph Section -->
            <div class="w-full glass-chart mt-6">
                <img src="data:image/png;base64,{{ plot_image }}" alt="Live Weather Graphs" class="graph-image">
            </div>

            <!-- Forecast Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
                {% for forecast in forecast_list %}
                <div class="icon-box">
                    <p class="text-sm">{{ forecast['date'] }}</p>
                    <div class="mt-2 text-gray-600 w-10 h-10 mx-auto">
                        {{ get_weather_icon(forecast['weather_main'])|safe }}
                    </div>
                    <p class="text-lg font-bold mt-1">{{ forecast['temp'] }}°C</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, plot_image=plot_image_base64, city_name=city_name,
                                  current_temp=current_temp, current_humidity=current_humidity,
                                  current_wind_speed=current_wind_speed,
                                  current_pressure=current_pressure,
                                  current_weather_description=current_weather_description,
                                  current_weather_main=current_weather_main,
                                  current_icon_svg=current_icon_svg,
                                  get_weather_icon=get_weather_icon,
                                  location_display=location_display,
                                  current_date=current_date,
                                  current_day=current_day,
                                  forecast_list=forecast_list)


# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting Flask web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)
