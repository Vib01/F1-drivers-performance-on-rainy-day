import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import fastf1

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "F1 Rain & Performance Dashboard"

# App layout
app.layout = html.Div([
    html.H1("F1 Rain & Driver Performance Dashboard", style={'textAlign': 'center'}),

    # Input controls
    html.Div([
        html.Label("Year:"),
        dcc.Input(id="year-input", type="number", value=2023, min=2018, max=2023),

        html.Label("Event:"),
        dcc.Input(id="event-input", type="text", value="Berlin"),

        html.Label("Session Type:"),
        dcc.Dropdown(
            id="session-type-dropdown",
            options=[
                {'label': 'Practice', 'value': 'Practice'},
                {'label': 'Qualifying', 'value': 'Qualifying'},
                {'label': 'Race', 'value': 'Race'}
            ],
            value="Race"
        ),
    ], style={'display': 'flex', 'gap': '10px', 'marginBottom': '20px'}),

    # Driver selection
    html.Div([
        html.Label("Select Driver:"),
        dcc.Dropdown(id="driver-dropdown")
    ], style={'marginBottom': '20px'}),

    # Graphs
    dcc.Graph(id="lap-times-graph"),
    dcc.Graph(id="track-temp-graph"),
    dcc.Graph(id="performance-summary-graph")
])

# Callback to update driver options based on the selected year, event, and session type
@app.callback(
    Output("driver-dropdown", "options"),
    Output("driver-dropdown", "value"),
    Input("year-input", "value"),
    Input("event-input", "value"),
    Input("session-type-dropdown", "value")
)
def update_drivers(year, event, session_type):
    try:
        # Load session data
        print(f"Loading session for {year} - {event} - {session_type}")
        session = fastf1.get_session(year, event, session_type)
        session.load()

        # Get unique drivers and add "All Drivers" option
        drivers = session.laps['Driver'].unique()
        print(f"Found drivers: {drivers}")

        # Create driver options for the dropdown including "All Drivers"
        driver_options = [{'label': driver, 'value': driver} for driver in drivers]
        driver_options.append({'label': 'All Drivers', 'value': 'All Drivers'})

        # Set default to "All Drivers" if no selection
        return driver_options, 'All Drivers'

    except Exception as e:
        # Handle error (return empty dropdown in case of error)
        print(f"Error: {e}")
        return [], None

# Callback to generate plots based on user input
@app.callback(
    Output("lap-times-graph", "figure"),
    Output("track-temp-graph", "figure"),
    Output("performance-summary-graph", "figure"),
    Input("year-input", "value"),
    Input("event-input", "value"),
    Input("session-type-dropdown", "value"),
    Input("driver-dropdown", "value")
)
def update_graphs(year, event, session_type, driver):
    try:
        # Load session data
        print(f"Loading session data for {year} - {event} - {session_type}")
        session = fastf1.get_session(year, event, session_type)
        session.load()

        # Combine lap and weather data
        laps = session.laps
        weather = session.weather_data
        weather['SessionTime'] = pd.to_timedelta(weather['Time'].dt.total_seconds(), unit='s')
        laps['SessionTime'] = laps['LapStartTime']
        laps_weather = pd.merge_asof(
            laps.sort_values('SessionTime'),
            weather.sort_values('SessionTime'),
            on='SessionTime'
        )
        laps_weather['Rain'] = laps_weather.get('Rainfall', False)

        print(f"Combined laps and weather data: {laps_weather.head()}")

        # Filter rainy laps and select laps for the selected driver or all drivers
        if driver != 'All Drivers':
            rain_laps = laps_weather[(laps_weather['Rain']) & (laps_weather['Driver'] == driver)]
        else:
            rain_laps = laps_weather[laps_weather['Rain']]

        print(f"Filtered rain laps: {rain_laps.head()}")

        # Plot: Lap times during rain
        fig1 = px.scatter(
            rain_laps,
            x="LapNumber",
            y="LapTime",
            color="Driver",
            title="Lap Times During Rain",
            labels={"LapTime": "Lap Time (s)", "LapNumber": "Lap Number"}
        )

        # Plot: Track temperature vs. lap time during rain
        fig2 = px.scatter(
            rain_laps,
            x="TrackTemp",
            y="LapTime",
            color="Driver",
            title="Track Temperature vs. Lap Time During Rain",
            labels={"TrackTemp": "Track Temperature (°C)", "LapTime": "Lap Time (s)"}
        )

        # Plot: Driver performance summary
        rainy_summary = rain_laps.groupby('Driver').agg(
            avg_lap_time=('LapTime', lambda x: x.mean().total_seconds()),
            total_rain_laps=('LapNumber', 'count')
        ).reset_index()

        fig3 = px.bar(
            rainy_summary,
            x='Driver',
            y='avg_lap_time',
            title="Average Lap Time During Rain by Driver",
            labels={"avg_lap_time": "Average Lap Time (s)", "Driver": "Driver"}
        )

        return fig1, fig2, fig3

    except Exception as e:
        # Display error message and return empty figures in case of failure
        print(f"Error: {e}")
        return {}, {}, {}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
