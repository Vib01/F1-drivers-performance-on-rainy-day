
﻿# F1 Rain & Driver Performance Dashboard 

This interactive dashboard provides insights into Formula 1 driver performance during rainy sessions. It uses FastF1 to fetch lap and weather data and visualizes lap times, track temperature effects, and driver summaries using Dash and Plotly.

- Just tried out hugging face too , check it out here
<iframe
	src="https://vib001-f1-weather.hf.space"
	frameborder="0"
	width="850"
	height="450"
></iframe>



## Features

- Interactive visualization of lap times during rain
- Track temperature 
- Driver performance comparison (average lap time during rain)
- Responsive dashboard built with Dash


## Dependencies

- Python 3.8+
- FastF1
- Dash
- Plotly
- Pandas
- NumPy
- Statsmodels (optional; used to enable LOWESS trendlines if installed)

Statsmodels is optional  the code will run without it, but trendlines require it. The repository's `requirements.txt` already lists `statsmodels>=0.13.0`.

## Usage

1. Select the year, event, and session type in the sidebar.
2. Choose a driver or select "All Drivers".
3. Explore lap-time scatter plots, temperature correlations, and driver summaries.
4. you can all check out lap in map

## Data source

Race data is provided by the FastF1 library: https://github.com/theOehrly/Fast-F1

---
=======
# F1 Rain & Driver Performance Dashboard 🏎🏎

## Overview

This interactive dashboard provides real-time insights into Formula 1 driver performance during rainy sessions. Built with Python, Dash, Plotly, and FastF1, the dashboard allows users to explore data on lap times, track temperature, and driver performance under various weather conditions.

The application integrates data from the FastF1 library, which retrieves detailed lap, weather, and session information for each F1 race. Users can select the year, event, and session type to view visualizations for lap times, track temperature, and driver performance summary during rainy conditions.

## Features🔮🔮

- **Interactive Visualizations**: 
  - Driver performance summary showing average lap time and number of rain laps for each driver.
  - also added laps
  
- **Customizable Input**: 
  - Select the year (2018-2023), event (e.g., "Berlin"), and session type (Practice, Qualifying, or Race).
  - Option to view performance for individual drivers or for all drivers combined.

## Technologies

- **Dash**: For creating the interactive web application.
- **Plotly**: For generating dynamic and visually appealing graphs.
- **FastF1**: For retrieving and processing Formula 1 race data, including lap times, weather, and driver information.
- **Pandas**: For data manipulation and merging of lap and weather data.
- **Css**
- **hugging face** for demo deployment


- Select the year, event, and session type to filter data.
- The dashboard will update the graphs to display lap times, track temperature, and performance summary for the selected criteria.
- Hover over the graphs to see additional details on lap times and driver performance.

I personally advice to run it locally for better user experience. cause I am using free tier on hugging face, its not that good.<img width="1920" height="1200" alt="Screenshot (4)" src="https://github.com/user-attachments/assets/e21956c9-2f9e-477c-a7bc-2b86b278f6f1" />
<img width="1920" height="1200" alt="Screenshot (3)" src="https://github.com/user-attachments/assets/3e44ca4b-119b-48e3-bc3a-b2612723b2bb" />
<img width="1920" height="1200" alt="Screenshot (2)" src="https://github.com/user-attachments/assets/e316342c-c45a-4639-a810-152e171567e3" />
<img width="1920" height="1200" alt="Screenshot (1)" src="https://github.com/user-attachments/assets/5fc1fe23-5d92-4cc8-8f5a-df34889c8422" />
