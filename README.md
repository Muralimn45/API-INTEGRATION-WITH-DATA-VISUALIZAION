"COMPANY": CODETECT IT SOLUTIONS

"NAME": MURALI N

"INTERN ID": CT04DY169

"DOMAIN": PYTHON PROGRAMMING.

"DURATION": 4 WEEKS

"MENTOR":NEELA SANTHOSH KUMAR

# API-INTEGRATION-AND-DATA-VISUALIZATION
using python to fetch data from public API and creating visuals using matplotlib and displaying the live data visuals in webpage
"DESCRPTION":
The first step in creating live data visuals is fetching the data itself. Python's requests library is the standard for making HTTP requests to APIs. You would typically use a GET request to retrieve data from a public API endpoint. Once the data is received, it usually comes in a JSON format. The requests library automatically handles parsing this into a Python dictionary, making it easy to extract the relevant information you need for your visualization.

For data visualization, matplotlib is a powerful and flexible library. It allows you to create a wide variety of static, animated, and interactive plots. The core concept involves creating a figure (plt.figure()) and one or more axes (fig.add_subplot()) to plot your data. You can then use methods like plt.plot() for line charts or plt.bar() for bar charts to represent your data visually. Customizing your plot with titles, labels, colors, and styles is straightforward and allows you to create professional-looking charts.

To display these visuals on a webpage, a simple Python script alone isn't enough to make the visuals "live." A web server is required to serve the webpage and dynamically update the plot. A common approach is to have a server-side script (e.g., using a framework like Flask or Django) that periodically fetches new data, generates a new plot image, and saves it to a specific file on the server. The webpage, which is served by the same server, contains an <img> tag pointing to that image file. To make it feel "live," you can use a small amount of JavaScript to periodically refresh the image without reloading the entire page.

The immersive documents below provide a working Python script and a corresponding HTML file. The Python script demonstrates how to fetch data from a public API, process it, and create a matplotlib plot saved as a PNG file. The HTML file shows how to embed this image on a simple webpage. This is a foundational approach that you can build upon. You could schedule the Python script to run every few minutes to create a new plot, and the webpage would automatically display the updated visual. This method is effective for displaying data that doesn't need to be updated in real-time but rather on a consistent schedule.

This setup provides a great starting point for building more complex dashboards and data-driven applications. You can extend this by exploring different types of plots in matplotlib, using other visualization libraries like Seaborn or Plotly, and integrating your Python script with a full-fledged web framework for more advanced functionality.

"MY PROJECT":
A weather data project requires a slightly different approach to data retrieval and visualization, as the data is typically organized around a specific location. The first step, as before, is to select a public API. The OpenWeatherMap API is a popular choice, providing a wealth of information about current conditions and forecasts for cities worldwide. You will need to obtain a free API key from their website to make authenticated requests.

Once you have your API key, you can use Python's requests library to fetch the data. The request will include your API key and the name of the city you want to query. The API will respond with a JSON object containing detailed weather information, such as temperature, humidity, wind speed, and a textual description of the weather. This JSON data is then easily parsed into a Python dictionary, allowing you to access specific values.

For visualization, we will again use matplotlib. Instead of plotting a single metric over time, a good starting point for a single location is to create a bar chart or a small set of line charts to represent key metrics. For example, a bar chart can effectively compare the current temperature, humidity percentage, and wind speed, giving a quick overview of the conditions. Customizing the plot with appropriate labels and colors for a weather theme (e.g., cool blues for temperature, vibrant colors for wind) can make the visual more engaging.

To display these visuals on a webpage, you'll use the same foundational approach. A Python script will fetch the latest weather data, generate a plot, and save it as an image file (e.g., weather_plot.png). A simple HTML page, using an <img> tag that points to this file, will then be used to display the visual. To make the data feel "live," a small JavaScript function on the webpage can be set to periodically refresh the image source. This forces the browser to fetch the latest version of the image from the server, which is updated whenever your Python script runs.

This method is highly scalable. You can expand the project to include more advanced visualizations, such as displaying a forecast for the next 24 hours, or fetching and plotting data for multiple cities at once. The core logic of fetching, plotting, and serving the image remains the same, providing a solid foundation for your data-driven project.

#OUTPUT: <img width="1124" height="558" alt="Image" src="https://github.com/user-attachments/assets/d86f01ce-bd9d-4dd1-886a-a23171e4e668" />
<img width="1111" height="759" alt="Image" src="https://github.com/user-attachments/assets/85e09078-1a56-4744-94d3-2f3ba3ad4598" />
<img width="1123" height="251" alt="Image" src="https://github.com/user-attachments/assets/07d0ccdb-5088-4a21-8de6-3676c7eb261b" />
