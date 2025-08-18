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
from datetime import datetime
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
# The base URL for the OpenWeatherMap Current Weather Data API endpoint.
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Global data storage for the live graphs.
timestamps = []
temperatures = []
humidity = []
wind_speed = []
pressure = []


# --- Function Definitions ---
def get_current_weather_data(city_name):
    """
    Fetches real-time weather data from the OpenWeatherMap API.

    Args:
        city_name (str): The name of the city to fetch data for.

    Returns:
        dict or None: A dictionary containing the weather data if the request is
                      successful, otherwise None.
    """
    if API_KEY == "YOUR_VALID_API_KEY_HERE":
        print("ERROR: Please replace 'YOUR_VALID_API_KEY_HERE' with your actual API key.", file=sys.stderr)
        return None

    # Construct the parameters for the API request.
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"  # Request temperature in Celsius.
    }

    try:
        # Send a GET request to the API.
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to retrieve weather data. {e}", file=sys.stderr)
        return None


def update_live_data(city_name):
    """
    Fetches new data and appends it to the global lists for live visualization.
    """
    data = get_current_weather_data(city_name)
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
    else:
        city_name = session.get('city', 'Dnipro, Ukraine')

    # Update data with the remembered city name.
    update_live_data(city_name)
    current_weather_data = get_current_weather_data(city_name)

    # Extract data with safe access
    if current_weather_data:
        current_temp = current_weather_data['main']['temp']
        current_humidity = current_weather_data['main']['humidity']
        current_wind_speed = current_weather_data['wind']['speed']
        current_pressure = current_weather_data['main']['pressure']
        current_weather_description = current_weather_data['weather'][0]['description']
        location_display = f"{current_weather_data['name']}, {current_weather_data['sys']['country']}"
    else:
        # Fallback values if API call fails
        current_temp = 'N/A'
        current_humidity = 'N/A'
        current_wind_speed = 'N/A'
        current_pressure = 'N/A'
        current_weather_description = 'N/A'
        location_display = city_name

    current_date = datetime.now().strftime("%B %d")
    current_day = datetime.now().strftime("%A")

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
            .icon-main {
                width: 180px;
                height: 180px;
                background-color: #a4b0d8;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            }
            .sun-icon {
                background-color: #fddb00;
                width: 100px;
                height: 100px;
                border-radius: 50%;
                box-shadow: 0 0 20px #fddb00, 0 0 40px rgba(253, 219, 0, 0.5);
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

            <div class="flex flex-col sm:flex-row items-center justify-between gap-6">
                <!-- Left Section: Current Weather Details -->
                <div class="flex flex-col w-full sm:w-auto">
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
                <div class="flex flex-col items-center justify-center sm:w-auto">
                    <div class="w-24 h-24 relative">
                        <div class="icon-main">
                            <!-- A simple cloud and sun SVG combo for visual representation -->
                            <svg class="h-full w-full opacity-60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M18 10h-1.26a8 8 0 1 0-16.34 0h1.26"/>
                                <path d="M22 17h-1.26a8 8 0 1 0-16.34 0h1.26"/>
                            </svg>
                        </div>
                        <div class="sun-icon absolute top-1/2 left-1/2 transform -translate-x-1/4 -translate-y-1/2"></div>
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

            <!-- Forecast Cards (Mock Data) -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
                <div class="icon-box">
                    <p class="text-sm">Today</p>
                    <div class="mt-2">
                         <svg class="h-10 w-10 mx-auto text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                             <path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4zm7-6a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4z" />
                         </svg>
                    </div>
                    <p class="text-lg font-bold mt-1">-3°C</p>
                </div>
                <div class="icon-box">
                    <p class="text-sm">Jan 9</p>
                    <div class="mt-2">
                         <svg class="h-10 w-10 mx-auto text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                         </svg>
                    </div>
                    <p class="text-lg font-bold mt-1">-1°C</p>
                </div>
                <div class="icon-box">
                    <p class="text-sm">Jan 10</p>
                    <div class="mt-2">
                         <svg class="h-10 w-10 mx-auto text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4zm7-6a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4z" />
                         </svg>
                    </div>
                    <p class="text-lg font-bold mt-1">+2°C</p>
                </div>
                <div class="icon-box">
                    <p class="text-sm">Jan 11</p>
                    <div class="mt-2">
                         <svg class="h-10 w-10 mx-auto text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4zm7-6a4 4 0 014-4h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a4 4 0 01-4-4z" />
                         </svg>
                    </div>
                    <p class="text-lg font-bold mt-1">+6°C</p>
                </div>
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
                                  location_display=location_display,
                                  current_date=current_date,
                                  current_day=current_day)


# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting Flask web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)
