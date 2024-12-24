
![download](https://github.com/user-attachments/assets/1d45e299-b05b-44e8-8260-49b50035baa5)
## F1 Rain & Driver Performance Dashboard 🏎🏎

## Overview

This interactive dashboard provides real-time insights into Formula 1 driver performance during rainy sessions. Built with Python, Dash, Plotly, and FastF1, the dashboard allows users to explore data on lap times, track temperature, and driver performance under various weather conditions.

The application integrates data from the FastF1 library, which retrieves detailed lap, weather, and session information for each F1 race. Users can select the year, event, and session type to view visualizations for lap times, track temperature, and driver performance summary during rainy conditions.

## Features🔮🔮

- **Interactive Visualizations**: 
  - Lap times during rainy conditions, displayed by driver and lap number.
  - Track temperature vs. lap time to understand how weather impacts performance.
  - Driver performance summary showing average lap time and number of rain laps for each driver.
  
- **Customizable Input**: 
  - Select the year (2018-2023), event (e.g., "Berlin"), and session type (Practice, Qualifying, or Race).
  - Option to view performance for individual drivers or for all drivers combined.

## Technologies

- **Dash**: For creating the interactive web application.
- **Plotly**: For generating dynamic and visually appealing graphs.
- **FastF1**: For retrieving and processing Formula 1 race data, including lap times, weather, and driver information.
- **Pandas**: For data manipulation and merging of lap and weather data.

Open your browser and visit `http://127.0.0.1:8050/` to view the dashboard.

## Usage

- Select the year, event, and session type to filter data.
- The dashboard will update the graphs to display lap times, track temperature, and performance summary for the selected criteria.
- Hover over the graphs to see additional details on lap times and driver performance.

