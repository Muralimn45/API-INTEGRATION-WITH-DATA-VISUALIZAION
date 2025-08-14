# --- Live Weather Dashboard Web App (app.py) ---
# This Flask application serves a web page that displays a live, updating
# weather dashboard using data from the OpenWeatherMap API. The plots are
# generated using Matplotlib and served as images.

# --- Library Imports ---
# It's best practice to put all imports at the top of the file.
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
    # Use seaborn for consistent styling.
    sns.set_style("darkgrid")

    # Create a figure with four subplots.
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 20), sharex=True)
    fig.suptitle(f"Live Weather Dashboard for {city_name}", fontsize=22, weight='bold', y=0.97)

    # --- Plot 1: Temperature ---
    ax1.plot(timestamps, temperatures, color='#E94560', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax1.set_title("Temperature (°C)", fontsize=16, weight='bold')
    ax1.set_ylabel("Temp (°C)", fontsize=14)
    if temperatures:
        ax1.annotate(f"{temperatures[-1]}°C",
                     xy=(timestamps[-1], temperatures[-1]),
                     xytext=(5, 5),
                     textcoords="offset points",
                     ha='left', va='bottom',
                     fontsize=12,
                     color='#E94560',
                     weight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)

    # --- Plot 2: Humidity ---
    ax2.plot(timestamps, humidity, color='#45B8AC', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax2.set_title("Humidity (%)", fontsize=16, weight='bold')
    ax2.set_ylabel("Humidity (%)", fontsize=14)
    if humidity:
        ax2.annotate(f"{humidity[-1]}%",
                     xy=(timestamps[-1], humidity[-1]),
                     xytext=(5, 5),
                     textcoords="offset points",
                     ha='left', va='bottom',
                     fontsize=12,
                     color='#45B8AC',
                     weight='bold')
    ax2.grid(True, linestyle='--', alpha=0.6)

    # --- Plot 3: Wind Speed ---
    ax3.plot(timestamps, wind_speed, color='#6C4A8D', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax3.set_title("Wind Speed (m/s)", fontsize=16, weight='bold')
    ax3.set_ylabel("Wind Speed (m/s)", fontsize=14)
    if wind_speed:
        ax3.annotate(f"{wind_speed[-1]} m/s",
                     xy=(timestamps[-1], wind_speed[-1]),
                     xytext=(5, 5),
                     textcoords="offset points",
                     ha='left', va='bottom',
                     fontsize=12,
                     color='#6C4A8D',
                     weight='bold')
    ax3.grid(True, linestyle='--', alpha=0.6)

    # --- Plot 4: Atmospheric Pressure ---
    ax4.plot(timestamps, pressure, color='#F39C12', marker='o', linestyle='-', linewidth=2, markersize=6)
    ax4.set_title("Atmospheric Pressure (hPa)", fontsize=16, weight='bold')
    ax4.set_xlabel("Time", fontsize=14)
    ax4.set_ylabel("Pressure (hPa)", fontsize=14)
    if pressure:
        ax4.annotate(f"{pressure[-1]} hPa",
                     xy=(timestamps[-1], pressure[-1]),
                     xytext=(5, 5),
                     textcoords="offset points",
                     ha='left', va='bottom',
                     fontsize=12,
                     color='#F39C12',
                     weight='bold')
    ax4.grid(True, linestyle='--', alpha=0.6)

    # Set common x-axis properties.
    plt.xticks(rotation=45, ha='right')
    plt.autoscale(enable=True, axis='both', tight=True)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save the plot to a BytesIO object.
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
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
        session['city'] = city_name  # Store the city in the session
    else:
        # If no POST, check the session for a city.
        # If no city in session, use a default value.
        city_name = session.get('city', 'London')

    # Update data with the remembered city name.
    update_live_data(city_name)

    # Generate the plot image.
    plot_image_base64 = create_plot(city_name)

    # HTML template with an auto-refresh tag.
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Weather Dashboard</title>
        <meta http-equiv="refresh" content="15"> <!-- Auto-refresh every 15 seconds -->
        <style>
            {% raw %}
            body { font-family: 'Arial', sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; text-align: center; }
            .container { max-width: 1200px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .form-container { margin-bottom: 20px; }
            input[type="text"] { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #45a049; }
            img { max-width: 100%; height: auto; margin-top: 20px; }
            {% endraw %}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Weather Dashboard</h1>
            <div class="form-container">
                <form method="post">
                    <input type="text" name="city" placeholder="Enter city name..." value="{{ city_name }}">
                    <button type="submit">Update City</button>
                </form>
            </div>
            <img src="data:image/png;base64,{{ plot_image }}" alt="Live Weather Dashboard">
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, plot_image=plot_image_base64, city_name=city_name)


# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting Flask web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000/")
    # You can change host='0.0.0.0' to make it accessible from other devices on your network.
    app.run(debug=True, use_reloader=False)
