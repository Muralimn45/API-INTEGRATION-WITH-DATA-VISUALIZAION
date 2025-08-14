# --- Python Script for Live Weather Data Visualization Dashboard ---
# This script fetches real-time weather data from the OpenWeatherMap API and
# creates a live, updating data visualization dashboard with multiple subplots.

# --- Library Imports ---
try:
    import requests
    import sys
    import matplotlib.pyplot as plt
    import seaborn as sns
    import time
    from datetime import datetime
except ImportError as e:
    # If a required library is missing, print an error and exit.
    print(f"ERROR: A required library could not be imported. Please install it.", file=sys.stderr)
    print(f"Missing library: {e.name}. You can install it with 'pip install {e.name}'.", file=sys.stderr)
    sys.exit(1)

# --- API Configuration ---
# IMPORTANT: This API key is used to fetch current weather data from OpenWeatherMap.
API_KEY = "018ecddd8ef7f830fb239f1edd238b9e"

# The base URL for the OpenWeatherMap Current Weather Data API endpoint.
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


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

        # Raise an exception for HTTP error codes.
        response.raise_for_status()

        # Parse the JSON response and return the data.
        return response.json()
    except requests.exceptions.RequestException as e:
        # Catch any network or HTTP-related errors and provide a clear message.
        print(f"ERROR: Failed to retrieve weather data. {e}", file=sys.stderr)
        return None


def create_live_visualization(city_name):
    """
    Creates and continuously updates a live visualization of the current weather,
    including temperature, humidity, wind speed, and atmospheric pressure.

    Args:
        city_name (str): The name of the city for the plot title.
    """
    # Enable Matplotlib's interactive mode.
    plt.ion()

    # Apply a seaborn style for better aesthetics
    sns.set_style("darkgrid")

    # Initialize lists to store data over time.
    timestamps = []
    temperatures = []
    humidity = []
    wind_speed = []
    pressure = []

    # Create a figure with four subplots (4 rows, 1 column).
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 20), sharex=True)
    fig.suptitle(f"Live Weather Dashboard for {city_name}", fontsize=22, weight='bold', y=0.97)

    print(f"Starting live weather feed for {city_name}. Press Ctrl+C to stop.")

    try:
        while True:
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

                # Clear previous plots.
                ax1.clear()
                ax2.clear()
                ax3.clear()
                ax4.clear()

                # --- Plot 1: Temperature ---
                ax1.plot(timestamps, temperatures, color='#E94560', marker='o', linestyle='-', linewidth=2, markersize=6)
                ax1.set_title("Temperature (°C)", fontsize=16, weight='bold')
                ax1.set_ylabel("Temp (°C)", fontsize=14)
                ax1.annotate(f"{current_temp}°C",
                             xy=(timestamps[-1], current_temp),
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
                ax2.annotate(f"{current_humidity}%",
                             xy=(timestamps[-1], current_humidity),
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
                ax3.annotate(f"{current_wind_speed} m/s",
                             xy=(timestamps[-1], current_wind_speed),
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
                ax4.annotate(f"{current_pressure} hPa",
                             xy=(timestamps[-1], current_pressure),
                             xytext=(5, 5),
                             textcoords="offset points",
                             ha='left', va='bottom',
                             fontsize=12,
                             color='#F39C12',
                             weight='bold')
                ax4.grid(True, linestyle='--', alpha=0.6)

                # Set common x-axis properties
                plt.xticks(rotation=45, ha='right')
                plt.autoscale(enable=True, axis='both', tight=True)
                plt.gcf().autofmt_xdate()

                # Redraw the plot and process events.
                plt.draw()
                plt.pause(1)  # Pause for 1 second before the next update.
            else:
                print("Failed to retrieve current weather data. Retrying in 1 second...", file=sys.stderr)
                time.sleep(1)

    except KeyboardInterrupt:
        # Handle the user pressing Ctrl+C to exit the loop.
        print("\nLive feed stopped by user.")
    finally:
        # Turn off interactive mode and close the plot window on exit.
        plt.ioff()
        plt.close(fig)


def main():
    """
    The main function to run the live weather dashboard.
    It now prompts the user for a city name.
    """
    # Prompt the user to enter a city name
    city_name = input("Enter the city name: ")

    # Check if the user provided an input
    if not city_name:
        print("Error: No city name was entered. Please try again.", file=sys.stderr)
        sys.exit(1)

    # Start the live visualization loop.
    create_live_visualization(city_name)


if __name__ == "__main__":
    main()
