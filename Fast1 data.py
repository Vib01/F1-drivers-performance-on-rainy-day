import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import pandas as pd
import fastf1
import time
from dash.dependencies import ALL, MATCH
from dash.exceptions import PreventUpdate
from functools import lru_cache
import os

# Try to import statsmodels, but make it optional
try:
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Note: statsmodels not available. Trendlines will be disabled.")

# Create cache directory if it doesn't exist
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)

# Enable cache for FastF1 data
fastf1.Cache.enable_cache(cache_dir)

# Initialize Dash app with external stylesheets for better theming
external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "F1 Rain & Performance Dashboard"
server = app.server  # For deployment

# Custom CSS styles
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("🏎️ F1 Rain & Performance Dashboard", className="header-title"),
            html.P("Analyze driver performance in wet conditions across different F1 seasons", 
                  className="header-description")
        ], className="header")
    ]),
    
    # Main content
    html.Div([
        # Left sidebar - Controls
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Session Settings", className="control-title"),
                    html.Div([
                        html.Label("Year", className="control-label"),
                        dcc.Input(
                            id="year-input",
                            type="number",
                            value=2023,
                            min=2018,
                            max=2023,
                            className="control-input"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Event", className="control-label"),
                        dcc.Input(
                            id="event-input",
                            type="text",
                            value="Monza",
                            className="control-input"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Session Type", className="control-label"),
                        dcc.Dropdown(
                            id="session-type-dropdown",
                            options=[
                                {'label': 'Practice', 'value': 'Practice'},
                                {'label': 'Qualifying', 'value': 'Qualifying'},
                                {'label': 'Race', 'value': 'Race'}
                            ],
                            value="Race",
                            clearable=False,
                            className="control-dropdown"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Select Driver", className="control-label"),
                        dcc.Dropdown(
                            id="driver-dropdown",
                            placeholder="Select a driver...",
                            className="control-dropdown"
                        )
                    ], className="control-group"),
                    
                    html.Div(id="session-info", className="session-info")
                ], className="control-panel")
            ], className="card")
        ], className="sidebar"),
        
        # Main content area - Graphs
        html.Div([
            # Loading component for better UX
            dcc.Loading(
                id="loading-1",
                type="circle",
                children=[
                    html.Div([
                        html.Div([
                            dcc.Graph(id="lap-times-graph", className="graph-card")
                        ], className="card"),
                        
                        html.Div([
                            dcc.Graph(id="track-temp-graph", className="graph-card")
                        ], className="card"),
                        
                        html.Div([
                            dcc.Graph(id="performance-summary-graph", className="graph-card")
                        ], className="card")
                    ])
                ]
            )
        ], className="main-content")
    ], className="container"),
    
    # Footer
    html.Footer([
        html.P("F1 Data provided by FastF1 | Dashboard created with Dash", className="footer-text")
    ], className="footer")
])

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #e10600;
                --secondary-color: #15151e;
                --background-color: #f8f9fa;
                --card-bg: #ffffff;
                --text-color: #333333;
                --text-muted: #6c757d;
                --border-radius: 8px;
                --box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Roboto', sans-serif;
            }
            
            body {
                background-color: var(--background-color);
                color: var(--text-color);
                line-height: 1.6;
            }
            
            .header {
                background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
                color: white;
                padding: 2rem 2rem 3rem;
                margin-bottom: -1.5rem;
                text-align: center;
            }
            
            .header-title {
                font-size: 2.2rem;
                margin-bottom: 0.5rem;
                font-weight: 700;
            }
            
            .header-description {
                font-size: 1.1rem;
                opacity: 0.9;
                max-width: 800px;
                margin: 0 auto;
            }
            
            .container {
                display: flex;
                max-width: 1600px;
                margin: 0 auto;
                padding: 2rem;
                gap: 2rem;
            }
            
            .sidebar {
                flex: 0 0 300px;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2rem;
            }
            
            .card {
                background: var(--card-bg);
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                padding: 1.5rem;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            
            .control-panel {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }
            
            .control-title {
                color: var(--primary-color);
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .control-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .control-label {
                font-weight: 500;
                color: var(--text-color);
                font-size: 0.95rem;
            }
            
            .control-input, .control-dropdown {
                padding: 0.7rem 1rem;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 0.95rem;
                width: 100%;
                transition: border-color 0.2s, box-shadow 0.2s;
            }
            
            .control-input:focus, .control-dropdown:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 0.2rem rgba(225, 6, 0, 0.25);
                outline: none;
            }
            
            .graph-card {
                width: 100%;
                height: 400px;
                border-radius: var(--border-radius);
                overflow: hidden;
            }
            
            .session-info {
                margin-top: 1rem;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-size: 0.9rem;
                color: var(--text-muted);
            }
            
            .footer {
                text-align: center;
                padding: 2rem;
                color: var(--text-muted);
                font-size: 0.9rem;
                margin-top: 2rem;
                border-top: 1px solid #e9ecef;
            }
            
            /* Responsive design */
            @media (max-width: 1200px) {
                .container {
                    flex-direction: column;
                    padding: 1rem;
                }
                
                .sidebar {
                    flex: 0 0 auto;
                    margin-bottom: 2rem;
                }
                
                .header {
                    padding: 1.5rem 1rem 2.5rem;
                }
                
                .header-title {
                    font-size: 1.8rem;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Function to get session data with caching
@lru_cache(maxsize=32)
def get_session_data(year, event, session_type):
    try:
        print(f"Loading session for {year} - {event} - {session_type}")
        session = fastf1.get_session(year, event, session_type)
        session.load(laps=True, weather=True, telemetry=False)
        return session
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

# Callback to update driver options based on the selected year, event, and session type
@app.callback(
    Output("driver-dropdown", "options"),
    Output("driver-dropdown", "value"),
    Output("session-info", "children"),
    Input("year-input", "value"),
    Input("event-input", "value"),
    Input("session-type-dropdown", "value"),
    prevent_initial_call=True
)
def update_drivers(year, event, session_type):
    if not all([year, event, session_type]):
        return [], None, "Please select all session parameters"
        
    try:
        session = get_session_data(year, event, session_type)
        if session is None:
            return [], None, "❌ Failed to load session data. Please check your inputs and try again."

        # Get unique drivers
        drivers = session.laps['Driver'].unique()
        
        # Create driver options for the dropdown including "All Drivers"
        driver_options = [{'label': driver, 'value': driver} for driver in drivers]
        driver_options.append({'label': 'All Drivers', 'value': 'All Drivers'})
        
        # Session info text
        session_info = f"✅ Loaded: {event} {year} - {session_type}"
        
        return driver_options, 'All Drivers', session_info

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return [], None, error_msg

# Callback to generate plots based on user input
@app.callback(
    Output("lap-times-graph", "figure"),
    Output("track-temp-graph", "figure"),
    Output("performance-summary-graph", "figure"),
    Input("driver-dropdown", "value"),
    State("year-input", "value"),
    State("event-input", "value"),
    State("session-type-dropdown", "value"),
    prevent_initial_call=True
)
def update_graphs(driver, year, event, session_type):
    if not all([year, event, session_type, driver]):
        # Return empty figures if any input is missing
        empty_fig = {}
        return empty_fig, empty_fig, empty_fig
    
    try:
        # Get cached session data
        session = get_session_data(year, event, session_type)
        if session is None:
            raise Exception("Failed to load session data")
            
        # Get laps and weather data
        laps = session.laps.pick_quicklaps()  # Only get quicklaps for better performance
        weather = session.weather_data
        
        if laps.empty or weather is None:
            raise Exception("No valid lap or weather data available")
        
        # Process data - create copies to avoid SettingWithCopyWarning
        weather_data = weather.copy()
        laps_data = laps.copy()
        
        # Convert time columns
        weather_data['SessionTime'] = pd.to_timedelta(weather_data['Time'].dt.total_seconds(), unit='s')
        laps_data = laps_data.assign(SessionTime=laps_data['LapStartTime'])
        
        # Merge laps and weather data
        laps_weather = pd.merge_asof(
            laps_data.sort_values('SessionTime'),
            weather_data[['SessionTime', 'Rainfall', 'TrackTemp', 'AirTemp', 'Humidity']].sort_values('SessionTime'),
            on='SessionTime',
            direction='nearest'
        )
        
        # Handle rain data
        laps_weather = laps_weather.assign(
            Rain=laps_weather.get('Rainfall', pd.Series(False)).fillna(False)
        )
        
        # Filter data based on selection - create a copy to avoid chained assignment
        if driver != 'All Drivers':
            rain_laps = laps_weather[laps_weather['Driver'] == driver].copy()
            if rain_laps.empty:
                raise Exception(f"No data available for driver {driver}")
        else:
            rain_laps = laps_weather.copy()
            
        # Convert LapTime to seconds for calculations
        rain_laps = rain_laps.assign(
            LapTime_seconds=rain_laps['LapTime'].dt.total_seconds()
        )
        
        # Create plots
        if rain_laps.empty:
            # Return empty plots with message if no data
            no_data_fig = px.scatter(title="No data available for the selected criteria")
            return no_data_fig, no_data_fig, no_data_fig
            
        # Plot 1: Lap times
        fig1 = px.scatter(
            rain_laps,
            x="LapNumber",
            y="LapTime_seconds",
            color="Driver",
            title=f"Lap Times - {event} {year} {session_type}",
            labels={
                "LapTime_seconds": "Lap Time (s)",
                "LapNumber": "Lap Number"
            },
            hover_data={
                'LapTime_seconds': ':.3f',
                'TrackTemp': ':.1f',
                'AirTemp': ':.1f',
                'Humidity': ':.1f%',
                'Driver': True,
                'LapNumber': True
            }
        )
        fig1.update_layout(yaxis_title="Lap Time (s)")
        
        # Plot 2: Track temperature vs lap time
        if 'TrackTemp' in rain_laps.columns and not rain_laps['TrackTemp'].isna().all():
            fig2 = px.scatter(
                rain_laps,
                x="TrackTemp",
                y="LapTime_seconds",
                color="Driver",
                title=f"Track Temperature vs Lap Time - {event} {year} {session_type}",
                labels={
                    "TrackTemp": "Track Temperature (°C)",
                    "LapTime_seconds": "Lap Time (s)"
                },
                trendline="lowess" if STATSMODELS_AVAILABLE else None,
                hover_data={
                    'LapTime_seconds': ':.3f',
                    'TrackTemp': ':.1f',
                    'LapNumber': True
                }
            )
            fig2.update_layout(yaxis_title="Lap Time (s)")
        else:
            fig2 = px.scatter(title="No temperature data available")
        
        # Plot 3: Performance summary
        try:
            # Calculate mean and count, ensuring we handle any potential NaNs
            summary = rain_laps.groupby('Driver').agg(
                avg_lap_time=('LapTime_seconds', 'mean'),
                lap_count=('LapTime_seconds', 'count')
            ).reset_index()
            
            if not summary.empty and not summary['avg_lap_time'].isna().all():
                summary = summary.dropna()
                fig3 = px.bar(
                    summary.sort_values('avg_lap_time'),
                    x='Driver',
                    y='avg_lap_time',
                    title=f"Average Lap Time by Driver - {event} {year} {session_type}",
                    labels={
                        "avg_lap_time": "Average Lap Time (s)",
                        "Driver": "Driver",
                        "lap_count": "Lap Count"
                    },
                    hover_data={
                        'avg_lap_time': ':.3f',
                        'lap_count': True
                    },
                    color='avg_lap_time',
                    color_continuous_scale='Viridis'
                )
                fig3.update_layout(
                    yaxis_title="Average Lap Time (s)",
                    coloraxis_showscale=False,
                    xaxis={'categoryorder': 'total ascending'},
                    hovermode='x'
                )
            else:
                fig3 = px.scatter(title="No valid lap time data available for summary")
            
        except Exception as e:
            print(f"Error creating summary plot: {e}")
            fig3 = px.scatter(title="Could not generate performance summary")
        
        return fig1, fig2, fig3
        
    except Exception as e:
        print(f"Error in update_graphs: {e}")
        error_fig = px.scatter(title=f"Error: {str(e)[:100]}")
        return error_fig, error_fig, error_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
