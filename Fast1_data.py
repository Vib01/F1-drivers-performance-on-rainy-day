import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import fastf1
from functools import lru_cache
import os

# -----------------------------
# Setup & caching
# -----------------------------
cache_dir = "f1_cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

app = dash.Dash(__name__)
server = app.server
app.title = "F1 Weather & Performance Analysis"

# Add external stylesheets
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a1a 100%);
                font-family: 'Rajdhani', sans-serif;
                color: #fff;
                overflow-x: hidden;
                min-height: 100vh;
            }
            
            /* Animated background grid */
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(rgba(255, 0, 0, 0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 0, 0, 0.05) 1px, transparent 1px);
                background-size: 50px 50px;
                animation: gridScroll 20s linear infinite;
                pointer-events: none;
                z-index: 0;
            }
            
            @keyframes gridScroll {
                0% { transform: translateY(0); }
                100% { transform: translateY(50px); }
            }
            
            /* Racing stripes */
            .racing-stripe {
                position: fixed;
                top: 0;
                height: 3px;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    #ff0000 25%, 
                    #ffffff 50%, 
                    #ff0000 75%, 
                    transparent 100%);
                animation: stripe-move 3s linear infinite;
                z-index: 1000;
                width: 200%;
            }
            
            @keyframes stripe-move {
                0% { transform: translateX(-50%); }
                100% { transform: translateX(0%); }
            }
            
            /* Main container */
            #react-entry-point > div {
                position: relative;
                z-index: 1;
            }
            
            .main-container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Header styling */
            .f1-header {
                text-align: center;
                padding: 40px 20px;
                background: linear-gradient(135deg, rgba(220, 0, 0, 0.2), rgba(0, 0, 0, 0.6));
                border-radius: 20px;
                margin-bottom: 90px;
                border: 2px solid rgba(255, 0, 0, 0.3);
                box-shadow: 
                    0 0 40px rgba(255, 0, 0, 0.4),
                    inset 0 0 60px rgba(255, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .f1-header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(
                    45deg,
                    transparent 30%,
                    rgba(255, 255, 255, 0.05) 50%,
                    transparent 70%
                );
                animation: shine 4s infinite;
            }
            
            @keyframes shine {
                0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
            }
            
            .f1-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 3.5em;
                font-weight: 900;
                background: linear-gradient(135deg, #ff0000, #ffffff, #ff0000);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: 4px;
                position: relative;
                animation: pulse 2s ease-in-out infinite;
                margin: 0;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
            
            .subtitle {
                font-size: 1.2em;
                color: #ff4444;
                margin-top: 10px;
                letter-spacing: 3px;
                text-transform: uppercase;
            }
            
            /* Control panel */
            .control-panel {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 90px;
                padding: 25px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 15px;
                border: 1px solid rgba(255, 0, 0, 0.2);
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            }
            
            .control-item {
                position: relative;
            }
            
            .control-item::before {
                content: '';
                position: absolute;
                top: -5px;
                left: -5px;
                right: -5px;
                bottom: -5px;
                background: linear-gradient(45deg, #ff0000, #ff4444);
                border-radius: 10px;
                opacity: 0;
                transition: opacity 0.3s;
                z-index: -1;
            }
            
            .control-item:hover::before {
                opacity: 0.3;
            }
            
            /* Event selector scrollbar */
            .event-selector {
                background: rgba(10, 10, 10, 0.7);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 105px;
                border: 1px solid rgba(255, 0, 0, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
                position: relative;
                z-index: 10;
            }
            
            .event-selector-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.5em;
                color: #ff0000;
                margin-bottom: 15px;
                text-align: center;
                letter-spacing: 2px;
            }
            
            .event-scroll-container {
                display: flex;
                gap: 15px;
                overflow-x: auto;
                overflow-y: visible;
                padding: 45px 15px 75px 15px;
                scroll-behavior: smooth;
                position: relative;
                z-index: 11;
            }
            
            .event-scroll-container::-webkit-scrollbar {
                height: 12px;
            }
            
            .event-scroll-container::-webkit-scrollbar-track {
                background: rgba(20, 20, 20, 0.8);
                border-radius: 10px;
                border: 1px solid rgba(255, 0, 0, 0.2);
            }
            
            .event-scroll-container::-webkit-scrollbar-thumb {
                background: linear-gradient(90deg, #ff0000, #ff4444);
                border-radius: 10px;
                transition: background 0.3s;
                border: 2px solid rgba(0, 0, 0, 0.3);
            }
            
            .event-scroll-container::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(90deg, #ff4444, #ff0000);
                box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
            }
            
            .event-card {
                min-width: 220px;
                padding: 20px;
                background: rgba(20, 20, 20, 0.9);
                border: 2px solid rgba(255, 0, 0, 0.3);
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
                position: relative;
                overflow: hidden;
                z-index: 12;
            }
            
            .event-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.2), transparent);
                transition: left 0.5s;
            }
            
            .event-card:hover {
                transform: translateY(-8px) scale(1.05);
                border-color: #ff0000;
                box-shadow: 0 15px 40px rgba(255, 0, 0, 0.6);
                z-index: 13;
            }
            
            .event-card:hover::before {
                left: 100%;
            }
            
            .event-card.selected {
                background: rgba(255, 0, 0, 0.25);
                border-color: #ff0000;
                box-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
                border-width: 3px;
                z-index: 13;
            }
            
            .event-card-round {
                font-family: 'Orbitron', sans-serif;
                font-size: 0.9em;
                color: #ff4444;
                margin-bottom: 5px;
            }
            
            .event-card-name {
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.1em;
                font-weight: 700;
                color: #fff;
                margin-bottom: 8px;
            }
            
            .event-card-location {
                font-size: 0.85em;
                color: #aaa;
                margin-bottom: 5px;
            }
            
            .event-card-date {
                font-size: 0.8em;
                color: #888;
            }
            
            /* Input styling */
            input[type="number"], input[type="text"] {
                width: 100%;
                padding: 12px;
                background: rgba(20, 20, 20, 0.8) !important;
                border: 2px solid rgba(255, 0, 0, 0.3) !important;
                border-radius: 8px;
                color: #fff !important;
                font-family: 'Orbitron', sans-serif;
                font-size: 16px;
                transition: all 0.3s;
            }
            
            input[type="number"]:focus, input[type="text"]:focus {
                outline: none;
                border-color: #ff0000 !important;
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
                transform: translateY(-2px);
            }
            
            /* Dropdown styling */
            .Select-control {
                background: rgba(20, 20, 20, 0.8) !important;
                border: 2px solid rgba(255, 0, 0, 0.3) !important;
                border-radius: 8px !important;
                transition: all 0.3s !important;
            }
            
            .Select-control:hover {
                border-color: #ff0000 !important;
            }
            
            .Select-menu-outer {
                background: rgba(20, 20, 20, 0.95) !important;
                border: 2px solid rgba(255, 0, 0, 0.3) !important;
                border-radius: 8px !important;
            }
            
            .Select-option {
                background: transparent !important;
                color: #fff !important;
                transition: all 0.2s !important;
            }
            
            .Select-option:hover, .Select-option.is-focused {
                background: rgba(255, 0, 0, 0.2) !important;
            }
            
            .Select-value-label {
                color: #fff !important;
            }
            
            .Select-placeholder {
                color: #aaa !important;
            }
            
            /* Graph containers */
            .graph-container {
                background: rgba(10, 10, 10, 0.7);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 75px;
                border: 1px solid rgba(255, 0, 0, 0.2);
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.5),
                    inset 0 0 20px rgba(255, 0, 0, 0.05);
                transition: all 0.4s;
                position: relative;
                overflow: hidden;
                z-index: 1;
            }
            
            .graph-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 0, 0, 0.1),
                    transparent
                );
                transition: left 0.5s;
            }
            
            .graph-container:hover {
                transform: translateY(-5px);
                border-color: rgba(255, 0, 0, 0.5);
                box-shadow: 
                    0 12px 48px rgba(255, 0, 0, 0.3),
                    inset 0 0 30px rgba(255, 0, 0, 0.1);
            }
            
            .graph-container:hover::before {
                left: 100%;
            }
            
            /* F1 Car Animation Controls */
            .animation-controls {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
                margin: 60px 0;
                padding: 20px;
                background: rgba(20, 20, 20, 0.8);
                border-radius: 10px;
                border: 2px solid rgba(255, 0, 0, 0.3);
            }
            
            .animation-btn {
                padding: 12px 24px;
                background: linear-gradient(135deg, #ff0000, #cc0000);
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Orbitron', sans-serif;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
            }
            
            .animation-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 0, 0, 0.6);
                background: linear-gradient(135deg, #ff3333, #ff0000);
            }
            
            .animation-btn:active {
                transform: translateY(0);
            }
            
            .speed-slider {
                width: 200px;
                height: 8px;
                background: rgba(255, 0, 0, 0.2);
                border-radius: 5px;
                outline: none;
                -webkit-appearance: none;
            }
            
            .speed-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 20px;
                height: 20px;
                background: #ff0000;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
            }
            
            .speed-slider::-webkit-slider-thumb:hover {
                background: #ff3333;
                box-shadow: 0 0 15px rgba(255, 0, 0, 1);
            }
            
            .animation-label {
                font-family: 'Orbitron', sans-serif;
                color: #ff4444;
                font-size: 14px;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .f1-title {
                    font-size: 2em;
                }
                
                .control-panel {
                    grid-template-columns: 1fr;
                }
                
                .event-card {
                    min-width: 160px;
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

# -----------------------------
# Helper functions
# -----------------------------
def classify_track_condition(row):
    if row["Rainfall"] > 0:
        return "Wet"
    if row["Humidity"] > 80 and row["TrackTemp"] < 30:
        return "Damp"
    return "Dry"

@lru_cache(maxsize=8)
def get_event_schedule(year):
    """Get all events for a given year"""
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule
    except Exception as e:
        print(f"Error loading schedule: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=16)
def load_processed_data(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(laps=True, weather=True)

    laps = session.laps.pick_quicklaps().copy()
    weather = session.weather_data.copy()

    weather["SessionTime"] = pd.to_timedelta(weather["Time"].dt.total_seconds(), unit="s")
    laps["SessionTime"] = laps["LapStartTime"]

    merged = pd.merge_asof(
        laps.sort_values("SessionTime"),
        weather.sort_values("SessionTime"),
        on="SessionTime",
        tolerance=pd.Timedelta("2min"),
        direction="nearest"
    )

    merged = merged.dropna(subset=["LapTime"])
    merged["LapTime_seconds"] = merged["LapTime"].dt.total_seconds()

    merged["TrackCondition"] = merged.apply(classify_track_condition, axis=1)

    # Normalize lap times within condition
    merged["LapZ"] = (
        merged["LapTime_seconds"]
        - merged.groupby("TrackCondition")["LapTime_seconds"].transform("mean")
    ) / merged.groupby("TrackCondition")["LapTime_seconds"].transform("std")

    return merged

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div([
    # Racing stripe
    html.Div(className="racing-stripe"),
    
    # Main container
    html.Div([
        # Header
        html.Div([
            html.H1("F1 TELEMETRY", className="f1-title"),
            html.Div("Weather & Performance Analysis Dashboard", className="subtitle")
        ], className="f1-header"),
        
        # Year selector
        html.Div([
            html.Div([
                dcc.Input(id="year", type="number", value=2025, min=2018, max=2025, placeholder="Year")
            ], className="control-item", style={"maxWidth": "200px", "margin": "0 auto"})
        ], className="control-panel"),
        
        # Event selector with scrollbar
        html.Div([
            html.Div("🏁 SELECT GRAND PRIX", className="event-selector-title"),
            html.Div(id="event-selector-container", className="event-scroll-container")
        ], className="event-selector"),
        
        # Hidden store for selected event
        dcc.Store(id="selected-event", data="Monza"),
        
        # Session and filter controls
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id="session",
                    options=[
                        {"label": "🏁 Practice", "value": "Practice"},
                        {"label": "⚡ Qualifying", "value": "Qualifying"},
                        {"label": "🏆 Race", "value": "Race"},
                    ],
                    value="Race",
                    clearable=False
                )
            ], className="control-item"),
            html.Div([
                dcc.Dropdown(id="driver", placeholder="🏎️ Select Driver")
            ], className="control-item"),
            html.Div([
                dcc.Dropdown(
                    id="condition",
                    options=[
                        {"label": "☀️ Dry", "value": "Dry"},
                        {"label": "🌧️ Damp", "value": "Damp"},
                        {"label": "💧 Wet", "value": "Wet"},
                    ],
                    value="Dry",
                    clearable=False
                )
            ], className="control-item"),
            html.Div([
                dcc.Dropdown(
                    id="analytics-view",
                    options=[
                        {"label": "📊 Standard View", "value": "standard"},
                        {"label": "🏎️ Track Position", "value": "track"},
                        {"label": "⚡ Speed Analysis", "value": "speed"},
                        {"label": "🔥 Tire Degradation", "value": "tire"},
                        {"label": "📈 Sector Performance", "value": "sector"},
                    ],
                    value="standard",
                    clearable=False
                )
            ], className="control-item"),
            html.Div([
                dcc.Dropdown(
                    id="lap-selector",
                    placeholder="🔢 Select Lap Number",
                    clearable=True
                )
            ], className="control-item")
        ], className="control-panel"),
        
        # Interactive Track Map (conditionally shown)
        html.Div([
            # Animation controls
            html.Div([
                html.Button("▶️ Play", id="play-btn", className="animation-btn", n_clicks=0),
                html.Button("⏸️ Pause", id="pause-btn", className="animation-btn", n_clicks=0),
                html.Button("🔄 Restart", id="restart-btn", className="animation-btn", n_clicks=0),
                html.Span("Animation Speed:", className="animation-label"),
                dcc.Slider(
                    id="animation-speed",
                    min=1,
                    max=10,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(1, 11)},
                    className="speed-slider"
                )
            ], className="animation-controls", id="animation-controls", style={"display": "none"}),
            
            dcc.Graph(id="track-map"),
            dcc.Interval(id="animation-interval", interval=100, n_intervals=0, disabled=True),
            dcc.Store(id="animation-state", data={"frame": 0, "max_frames": 0, "playing": False})
        ], id="track-map-container", className="graph-container", style={"display": "none"}),
        
        # Graphs
        html.Div([
            dcc.Graph(id="lap-times")
        ], className="graph-container"),
        
        html.Div([
            dcc.Graph(id="temp-vs-lap")
        ], className="graph-container"),
        
        html.Div([
            dcc.Graph(id="summary")
        ], className="graph-container"),
        
        # Advanced Analytics Container
        html.Div([
            dcc.Graph(id="advanced-analytics")
        ], id="analytics-container", className="graph-container", style={"display": "none"})
        
    ], className="main-container")
])

# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("event-selector-container", "children"),
    Input("year", "value"),
    Input("selected-event", "data")
)
def update_event_selector(year, selected_event):
    """Create scrollable event cards"""
    schedule = get_event_schedule(year)
    
    if schedule.empty:
        return html.Div("No events found for this year", style={"color": "#ff4444"})
    
    event_cards = []
    for idx, row in schedule.iterrows():
        event_name = row.get("EventName", "Unknown")
        location = row.get("Location", "")
        country = row.get("Country", "")
        round_num = row.get("RoundNumber", idx + 1)
        
        # Format date
        event_date = ""
        if "EventDate" in row:
            try:
                event_date = pd.to_datetime(row["EventDate"]).strftime("%b %d, %Y")
            except:
                event_date = str(row["EventDate"])
        
        # Determine if this card is selected
        is_selected = event_name == selected_event
        card_class = "event-card selected" if is_selected else "event-card"
        
        card = html.Div([
            html.Div(f"ROUND {round_num}", className="event-card-round"),
            html.Div(event_name, className="event-card-name"),
            html.Div(f"📍 {location}, {country}", className="event-card-location"),
            html.Div(event_date, className="event-card-date")
        ], 
        id={"type": "event-card", "index": event_name},
        className=card_class,
        n_clicks=0
        )
        
        event_cards.append(card)
    
    return event_cards

@app.callback(
    Output("lap-selector", "options"),
    Output("lap-selector", "value"),
    Input("year", "value"),
    Input("selected-event", "data"),
    Input("session", "value")
)
def update_lap_selector(year, event, session_type):
    """Populate lap selector with available laps"""
    try:
        df = load_processed_data(year, event, session_type)
        laps = sorted(df["LapNumber"].unique())
        opts = [{"label": f"Lap {lap}", "value": lap} for lap in laps]
        return opts, None
    except:
        return [], None

@app.callback(
    Output("selected-event", "data"),
    Input({"type": "event-card", "index": dash.dependencies.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def select_event(n_clicks):
    """Handle event card selection"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return "Monza"
    
    # Get the event name from the triggered component
    triggered_id = ctx.triggered[0]["prop_id"]
    if "event-card" in triggered_id:
        import json
        event_data = json.loads(triggered_id.split(".")[0])
        return event_data["index"]
    
    return "Monza"

@app.callback(
    Output("driver", "options"),
    Output("driver", "value"),
    Input("year", "value"),
    Input("selected-event", "data"),
    Input("session", "value")
)
def update_drivers(year, event, session_type):
    df = load_processed_data(year, event, session_type)
    drivers = sorted(df["Driver"].unique())
    opts = [{"label": f"🏎️ {d}", "value": d} for d in drivers]
    opts.append({"label": "🌐 All Drivers", "value": "ALL"})
    return opts, "ALL"

@app.callback(
    Output("animation-interval", "disabled"),
    Output("animation-state", "data"),
    Input("play-btn", "n_clicks"),
    Input("pause-btn", "n_clicks"),
    Input("restart-btn", "n_clicks"),
    Input("animation-interval", "n_intervals"),
    Input("lap-selector", "value"),
    dash.dependencies.State("animation-state", "data"),
    prevent_initial_call=True
)
def control_animation(play_clicks, pause_clicks, restart_clicks, n_intervals, selected_lap, state):
    """Control the F1 car animation"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return True, state
    
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger == "play-btn":
        state["playing"] = True
        return False, state
    
    elif trigger == "pause-btn":
        state["playing"] = False
        return True, state
    
    elif trigger == "restart-btn":
        state["frame"] = 0
        state["playing"] = True
        return False, state
    
    elif trigger == "animation-interval" and state.get("playing", False):
        state["frame"] = (state["frame"] + 1) % max(state.get("max_frames", 100), 1)
        return False, state
    
    elif trigger == "lap-selector":
        state["frame"] = 0
        return True, state
    
    return True, state

@app.callback(
    Output("animation-interval", "interval"),
    Input("animation-speed", "value")
)
def update_animation_speed(speed):
    """Update animation speed based on slider"""
    # Speed 1 = 200ms, Speed 10 = 20ms
    return max(20, 220 - (speed * 20))

@app.callback(
    Output("lap-times", "figure"),
    Output("temp-vs-lap", "figure"),
    Output("summary", "figure"),
    Output("track-map", "figure"),
    Output("advanced-analytics", "figure"),
    Output("track-map-container", "style"),
    Output("analytics-container", "style"),
    Output("animation-controls", "style"),
    Input("driver", "value"),
    Input("condition", "value"),
    Input("year", "value"),
    Input("selected-event", "data"),
    Input("session", "value"),
    Input("analytics-view", "value"),
    Input("lap-selector", "value"),
    Input("animation-state", "data")
)
def update_graphs(driver, condition, year, event, session_type, analytics_view, selected_lap, animation_state):
    df = load_processed_data(year, event, session_type)
    df = df[df["TrackCondition"] == condition]

    if driver != "ALL":
        df = df[df["Driver"] == driver]

    # Define racing color scheme
    colors = ['#ff0000', '#00ff00', '#0088ff', '#ffff00', '#ff00ff', '#00ffff', '#ff8800', '#8800ff']
    
    # Enhanced graph template
    template = {
        'layout': {
            'plot_bgcolor': 'rgba(0,0,0,0.3)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#ffffff', 'family': 'Rajdhani'},
            'xaxis': {
                'gridcolor': 'rgba(255,0,0,0.1)',
                'showgrid': True,
                'zeroline': False
            },
            'yaxis': {
                'gridcolor': 'rgba(255,0,0,0.1)',
                'showgrid': True,
                'zeroline': False
            }
        }
    }

    # Lap time progression with enhanced styling
    fig1 = px.scatter(
        df,
        x="LapNumber",
        y="LapTime_seconds",
        color="Driver",
        title=f"⚡ LAP TIME PROGRESSION - {condition.upper()} CONDITIONS",
        labels={"LapTime_seconds": "Lap Time (s)", "LapNumber": "Lap Number"},
        color_discrete_sequence=colors
    )
    fig1.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig1.update_layout(
        template=template,
        title_font=dict(size=24, family='Orbitron', color='#ff0000'),
        hovermode='closest',
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='rgba(255,0,0,0.3)',
            borderwidth=1
        )
    )

    # Track temp vs lap time with enhanced styling
    fig2 = px.scatter(
        df,
        x="TrackTemp",
        y="LapTime_seconds",
        color="Driver",
        title="🌡️ TRACK TEMPERATURE VS LAP TIME ANALYSIS",
        labels={"TrackTemp": "Track Temperature (°C)", "LapTime_seconds": "Lap Time (s)"},
        color_discrete_sequence=colors,
        trendline="lowess"
    )
    fig2.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig2.update_layout(
        template=template,
        title_font=dict(size=24, family='Orbitron', color='#ff0000'),
        hovermode='closest',
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='rgba(255,0,0,0.3)',
            borderwidth=1
        )
    )

    # Robust summary with enhanced bar chart
    summary = df.groupby("Driver").agg(
        median_lap=("LapTime_seconds", "median"),
        iqr=("LapTime_seconds", lambda x: x.quantile(0.75) - x.quantile(0.25)),
        laps=("LapTime_seconds", "count")
    ).reset_index()

    fig3 = go.Figure(data=[
        go.Bar(
            x=summary.sort_values("median_lap")["Driver"],
            y=summary.sort_values("median_lap")["median_lap"],
            marker=dict(
                color=summary.sort_values("median_lap")["median_lap"],
                colorscale=[[0, '#00ff00'], [0.5, '#ffff00'], [1, '#ff0000']],
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Median: %{y:.3f}s<extra></extra>'
        )
    ])
    
    fig3.update_layout(
        title="🏆 DRIVER PERFORMANCE - MEDIAN LAP TIMES",
        xaxis_title="Driver",
        yaxis_title="Median Lap Time (s)",
        template=template,
        title_font=dict(size=24, family='Orbitron', color='#ff0000'),
        showlegend=False
    )

    # Track Map Figure (shown when analytics_view == "track")
    fig_track = go.Figure()
    
    # Advanced Analytics Figure
    fig_analytics = go.Figure()
    
    # Control visibility based on analytics view
    track_style = {"display": "block"} if analytics_view == "track" else {"display": "none"}
    analytics_style = {"display": "block"} if analytics_view in ["speed", "tire", "sector"] else {"display": "none"}
    animation_controls_style = {"display": "flex"} if analytics_view == "track" and selected_lap else {"display": "none"}
    
    # Get current animation frame
    current_frame = animation_state.get("frame", 0)
    
    # Generate Track Map if view is "track"
    if analytics_view == "track" and selected_lap:
        try:
            session = fastf1.get_session(year, event, session_type)
            session.load(telemetry=True, laps=True)
            
            if driver != "ALL":
                lap_data = session.laps.pick_driver(driver).pick_lap(selected_lap)
                telemetry = lap_data.get_telemetry()
                
                # Update max frames in state
                animation_state["max_frames"] = len(telemetry)
                
                # Calculate current position for animation
                if current_frame >= len(telemetry):
                    current_frame = 0
                
                fig_track = go.Figure()
                
                # Draw the full track (gray)
                fig_track.add_trace(go.Scatter(
                    x=telemetry['X'],
                    y=telemetry['Y'],
                    mode='lines',
                    line=dict(color='#333', width=12),
                    name='Track',
                    hoverinfo='skip',
                    showlegend=False
                ))
                
                # Draw the path traveled so far (colored by speed)
                traveled_telemetry = telemetry.iloc[:current_frame+1]
                if len(traveled_telemetry) > 0:
                    fig_track.add_trace(go.Scatter(
                        x=traveled_telemetry['X'],
                        y=traveled_telemetry['Y'],
                        mode='lines',
                        line=dict(
                            color=traveled_telemetry['Speed'],
                            colorscale='Jet',
                            width=6,
                            showscale=True,
                            colorbar=dict(
                                title="Speed<br>(km/h)",
                                x=1.15,
                                thickness=20,
                                len=0.7
                            )
                        ),
                        name='Path',
                        hovertemplate='Speed: %{line.color:.1f} km/h<extra></extra>',
                        showlegend=False
                    ))
                
                # Add F1 car as an icon at current position
                if current_frame < len(telemetry):
                    current_pos = telemetry.iloc[current_frame]
                    
                    # Create F1 car shape using SVG path
                    fig_track.add_trace(go.Scatter(
                        x=[current_pos['X']],
                        y=[current_pos['Y']],
                        mode='markers+text',
                        marker=dict(
                            size=30,
                            color='#ff0000',
                            symbol='diamond',
                            line=dict(width=3, color='white')
                        ),
                        text='🏎️',
                        textfont=dict(size=30),
                        textposition='middle center',
                        name=f'{driver}',
                        hovertemplate=f'<b>{driver}</b><br>' +
                                    f'Speed: {current_pos["Speed"]:.1f} km/h<br>' +
                                    f'Position: ({current_pos["X"]:.0f}, {current_pos["Y"]:.0f})<br>' +
                                    f'Frame: {current_frame}/{len(telemetry)}<extra></extra>',
                        showlegend=True
                    ))
                    
                    # Add speed indicator text
                    fig_track.add_annotation(
                        x=current_pos['X'],
                        y=current_pos['Y'] + 50,
                        text=f"{current_pos['Speed']:.0f} km/h",
                        showarrow=False,
                        font=dict(size=16, color='#ff0000', family='Orbitron'),
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='#ff0000',
                        borderwidth=2,
                        borderpad=5
                    )
                
                fig_track.update_layout(
                    title=f"🏎️ ANIMATED TRACK MAP - {driver} LAP {selected_lap} ({current_frame}/{len(telemetry)} frames)",
                    template=template,
                    title_font=dict(size=24, family='Orbitron', color='#ff0000'),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
                    showlegend=True,
                    height=700,
                    legend=dict(
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='rgba(255,0,0,0.3)',
                        borderwidth=1,
                        x=0.02,
                        y=0.98
                    )
                )
            else:
                # Show multiple drivers on track (static comparison)
                lap_df = session.laps[session.laps['LapNumber'] == selected_lap]
                fig_track = go.Figure()
                
                for idx, (driver_name, driver_laps) in enumerate(lap_df.groupby('Driver')):
                    try:
                        lap = driver_laps.iloc[0]
                        telemetry = lap.get_telemetry()
                        
                        # Track line
                        fig_track.add_trace(go.Scatter(
                            x=telemetry['X'],
                            y=telemetry['Y'],
                            mode='lines',
                            line=dict(width=4, color=colors[idx % len(colors)]),
                            name=driver_name,
                            hovertemplate=f'{driver_name}<br>Position: (%{{x:.0f}}, %{{y:.0f}})<extra></extra>'
                        ))
                        
                        # Add car icon at start position
                        start_pos = telemetry.iloc[0]
                        fig_track.add_trace(go.Scatter(
                            x=[start_pos['X']],
                            y=[start_pos['Y']],
                            mode='markers+text',
                            marker=dict(
                                size=20,
                                color=colors[idx % len(colors)],
                                symbol='diamond',
                                line=dict(width=2, color='white')
                            ),
                            text='🏎️',
                            textfont=dict(size=20),
                            name=f'{driver_name} Car',
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    except:
                        continue
                
                fig_track.update_layout(
                    title=f"🏎️ TRACK MAP - LAP {selected_lap} (ALL DRIVERS COMPARISON)",
                    template=template,
                    title_font=dict(size=24, family='Orbitron', color='#ff0000'),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
                    showlegend=True,
                    height=700,
                    legend=dict(
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='rgba(255,0,0,0.3)',
                        borderwidth=1
                    )
                )
        except Exception as e:
            print(f"Error creating track map: {e}")
            fig_track.update_layout(
                title="⚠️ TRACK MAP - Data not available",
                template=template,
                annotations=[dict(text="Telemetry data not available for this session", 
                                 showarrow=False, font=dict(size=16, color='#ff4444'))]
            )
    
    # Generate Advanced Analytics based on view
    if analytics_view == "speed" and driver != "ALL":
        try:
            speed_data = df.groupby("LapNumber").agg({
                "Speed": "mean" if "Speed" in df.columns else "count"
            }).reset_index()
            
            fig_analytics = px.line(
                speed_data,
                x="LapNumber",
                y="Speed",
                title=f"⚡ AVERAGE SPEED ANALYSIS - {driver}",
                labels={"Speed": "Avg Speed (km/h)", "LapNumber": "Lap Number"}
            )
            fig_analytics.update_traces(line=dict(color='#ff0000', width=3))
            fig_analytics.update_layout(
                template=template,
                title_font=dict(size=24, family='Orbitron', color='#ff0000')
            )
        except:
            pass
    
    elif analytics_view == "sector":
        try:
            sector_cols = [c for c in df.columns if "Sector" in c and "Time" in c]
            if sector_cols:
                sector_data = df[["Driver", "LapNumber"] + sector_cols].copy()
                
                fig_analytics = go.Figure()
                for col in sector_cols:
                    sector_data[col] = pd.to_timedelta(sector_data[col]).dt.total_seconds()
                    fig_analytics.add_trace(go.Box(
                        y=sector_data[col],
                        name=col.replace("Time", ""),
                        marker_color=colors[sector_cols.index(col)]
                    ))
                
                fig_analytics.update_layout(
                    title="📈 SECTOR PERFORMANCE DISTRIBUTION",
                    template=template,
                    title_font=dict(size=24, family='Orbitron', color='#ff0000'),
                    yaxis_title="Time (seconds)"
                )
        except:
            pass

    return fig1, fig2, fig3, fig_track, fig_analytics, track_style, analytics_style, animation_controls_style

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
