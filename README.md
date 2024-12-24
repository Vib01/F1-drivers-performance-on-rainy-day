<<<<<<< HEAD
﻿# F1 Rain & Driver Performance Dashboard 

This interactive dashboard provides insights into Formula 1 driver performance during rainy sessions. It uses FastF1 to fetch lap and weather data and visualizes lap times, track temperature effects, and driver summaries using Dash and Plotly.

![F1 Rain Dashboard](https://github.com/user-attachments/assets/1d45e299-b05b-44e8-8260-49b50035baa5)

## Features

- Interactive visualization of lap times during rain
- Track temperature vs. lap time analysis
- Driver performance comparison (average lap time during rain)
- Responsive dashboard built with Dash

## Setup

1. Clone the repository:

```powershell
git clone https://github.com/Vib01/F1-drivers-performance-on-rainy-day.git
cd F1-drivers-performance-on-rainy-day
```

2. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Install requirements:

```powershell
pip install -r requirements.txt
```

4. Run the dashboard (note the space in the filename  quote it):

```powershell
python "Fast1 data.py"
```

5. Open your browser at http://127.0.0.1:8050/

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

>>>>>>> a4721e5 (Update README.md)
