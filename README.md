<img width="1795" height="1008" alt="Screenshot 2025-10-22 113554" src="https://github.com/user-attachments/assets/76fecf17-91c5-40b7-a878-0ead38360676" />
# F1 Driver Performance Analysis in Rainy Conditions

This interactive dashboard visualizes Formula 1 driver performance during rainy conditions. It uses FastF1 to fetch and analyze race data, providing insights into how different drivers perform in wet weather.

## Features

- Interactive visualization of lap times during rain
- Track temperature vs. lap time analysis
- Driver performance comparison
- Responsive design for all devices
<img width="1808" height="913" alt="Screenshot 2025-10-22 113619" src="https://github.com/user-attachments/assets/dae5322d-82f8-43eb-b50f-2d702e608cbc" />

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Vib01F1-drivers-performance-on-rainy-day.git
   cd Vib01F1-drivers-performance-on-rainy-day
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   python Fast1\ data.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:8050/`

## Dependencies

- Python 3.7+
- FastF1
- Dash
- Plotly
- Pandas
- Statsmodels (optional, for trendlines)

## Usage

1. Select the year, event, and session type
2. Choose a driver or keep "All Drivers" selected
3. Explore the interactive visualizations

## Data Source

Race data is provided by the [FastF1](https://github.com/theOehrly/Fast-F1) library.
