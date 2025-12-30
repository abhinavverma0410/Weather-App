import dash
from dash import dcc, html, Input, Output, State, ctx
import requests
import os

app = dash.Dash(__name__)
app.title = "Weather App"

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
if not WEATHERAPI_KEY:
    raise RuntimeError("❌ WEATHERAPI_KEY environment variable not set")

BASE_URL = "https://api.weatherapi.com/v1"

app.layout = html.Div([
    html.Div([
        html.Div(className="background"),

        html.Div([
            html.H1("Weather App", style={
                'textAlign': 'center',
                'color': 'white',
                'marginBottom': '30px',
                'fontFamily': 'Arial, sans-serif',
                'fontWeight': 'bold'
            }),

            html.Div([
                dcc.Input(
                    id='city-input',
                    type='text',
                    placeholder='Enter city name...',
                    style={
                        'width': '96.5%',
                        'padding': '12px',
                        'fontSize': '16px',
                        'border': 'none',
                        'borderRadius': '5px',
                        'marginBottom': '15px'
                    }
                ),

                html.Div([
                    html.Button(
                        'Current Weather',
                        id='current-weather-btn',
                        n_clicks=0,
                        className='weather-btn',
                        style={
                            'flex': '1',
                            'margin': '5px',
                            'padding': '12px',
                            'backgroundColor': '#4CAF50',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }
                    ),
                    html.Button(
                        '24 Hours Forecast',
                        id='hourly-forecast-btn',
                        n_clicks=0,
                        className='weather-btn',
                        style={
                            'flex': '1',
                            'margin': '5px',
                            'padding': '12px',
                            'backgroundColor': '#2196F3',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }
                    ),
                    html.Button(
                        'Next 7 Days Forecast',
                        id='future-forecast-btn',
                        n_clicks=0,
                        className='weather-btn',
                        style={
                            'flex': '1',
                            'margin': '5px',
                            'padding': '12px',
                            'backgroundColor': '#FF9800',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'cursor': 'pointer',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'display': 'flex', 'gap': '10px'})
            ], style={
                'backgroundColor': 'rgba(128, 193, 255, 0.9)',
                'padding': '20px',
                'borderRadius': '10px',
                'marginBottom': '20px'
            }),

            html.Div(
                id='weather-results',
                style={
                    'color': 'white',
                    'fontFamily': 'Arial, sans-serif',
                    'minHeight': '400px',
                    'padding': '20px',
                    'backgroundColor': 'rgba(128, 193, 255, 0.9)',
                    'borderRadius': '10px',
                    'overflowY': 'auto',
                    'maxHeight': '500px'
                }
            )
        ], style={
            'maxWidth': '700px',
            'margin': '0 auto',
            'padding': '20px'
        })
    ])
])

@app.callback(
    Output('weather-results', 'children'),
    Input('current-weather-btn', 'n_clicks'),
    Input('hourly-forecast-btn', 'n_clicks'),
    Input('future-forecast-btn', 'n_clicks'),
    State('city-input', 'value')
)
def update_weather(c, h, f, city):

    if not ctx.triggered_id:
        return "Enter a city name and click one of the buttons."

    if not city or not city.strip():
        return "❌ Please enter a city name."

    city = city.strip()

    if ctx.triggered_id == 'current-weather-btn':
        return current_weather(city)
    elif ctx.triggered_id == 'hourly-forecast-btn':
        return hourly_forecast(city)
    elif ctx.triggered_id == 'future-forecast-btn':
        return daily_forecast(city)

def current_weather(city):
    url = f"{BASE_URL}/current.json"
    r = requests.get(url, params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "aqi": "yes"
    }, timeout=10)

    data = r.json()
    if "error" in data:
        return f"❌ {data['error']['message']}"

    return html.Div([
        html.H2(f"Current Weather in {data['location']['name']}"),
        html.P(f"🌡 Temperature: {data['current']['temp_c']} °C"),
        html.P(f"🌥 Condition: {data['current']['condition']['text']}"),
        html.P(f"💧 Humidity: {data['current']['humidity']}%"),
        html.P(f"🌬 Wind Speed: {data['current']['wind_kph']} kph"),
        html.P(f"🌫 Air Quality (PM2.5): {round(data['current']['air_quality']['pm2_5'], 2)}")
    ])

def hourly_forecast(city):
    url = f"{BASE_URL}/forecast.json"
    r = requests.get(url, params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "hours": 24
    }, timeout=10)

    data = r.json()
    if "error" in data:
        return f"❌ {data['error']['message']}"

    hours = data['forecast']['forecastday'][0]['hour'][:24]

    return html.Div([
        html.H2(f"24-Hour Forecast for {data['location']['name']}"),
        *[
            html.Div([
                html.P(h['time']),
                html.P(f"{h['temp_c']} °C — {h['condition']['text']}"),
                html.Hr()
            ]) for h in hours
        ]
    ])

def daily_forecast(city):
    url = f"{BASE_URL}/forecast.json"
    r = requests.get(url, params={
        "key": WEATHERAPI_KEY,
        "q": city,
        "days": 7
    }, timeout=10)

    data = r.json()
    if "error" in data:
        return f"❌ {data['error']['message']}"

    return html.Div([
        html.H2(f"7-Day Forecast for {data['location']['name']}"),
        *[
            html.P(
                f"{d['date']}: "
                f"{d['day']['mintemp_c']}°C → {d['day']['maxtemp_c']}°C "
                f"({d['day']['condition']['text']})"
            )
            for d in data['forecast']['forecastday']
        ]
    ])

if __name__ == "__main__":
    app.run(debug=False)
