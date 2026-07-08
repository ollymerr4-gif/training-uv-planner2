from dotenv import load_dotenv
import os
import datetime 
import requests


load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

# 1. Choose a location (you can change this later)
location = "Adelaide"

# 2. Build the API URL
url = (
    "http://api.weatherapi.com/v1/forecast.json"
    f"?key={API_KEY}"
    f"&q={location}"
    "&hours=2"
)




def fetch_uv_interpolated(dt, forecast_data):
    hour = dt.hour
    minute = dt.minute

    # UV at the lower hour
    uv_lower = forecast_data["forecast"]["forecastday"][0]["hour"][hour]["uv"]

    # If exactly on the hour, no interpolation needed
    if minute == 0:
        return uv_lower

    # UV at the next hour
    uv_upper = forecast_data["forecast"]["forecastday"][0]["hour"][hour + 1]["uv"]

    # Fraction of the hour passed
    fraction = minute / 60

    # Linear interpolation
    uv_estimate = uv_lower * (1 - fraction) + uv_upper * fraction
    return uv_estimate


def classify_uv(uv):
    if uv < 3:
        return "Low"
    if uv < 6:
        return "Moderate"
    if uv < 8:
        return "High"
    if uv < 11:
        return "Very High"
    return "Extreme"


def get_uv_for_training(start_dt, end_dt, location="Adelaide"):
    url = (
        "http://api.weatherapi.com/v1/forecast.json"
        f"?key={API_KEY}"
        f"&q={location}"
        f"&dt={start_dt.strftime('%Y-%m-%d')}"
        "&hours=24"
    )

    response = requests.get(url)
    forecast_data = response.json()

    uv_start = fetch_uv_interpolated(start_dt, forecast_data)
    uv_end = fetch_uv_interpolated(end_dt, forecast_data)

    return {
        "uv_start": uv_start,
        "uv_end": uv_end,
        "risk_start": classify_uv(uv_start),
        "risk_end": classify_uv(uv_end)
    }


if __name__ == "__main__":
    from datetime import datetime

    # Test times for Adelaide
    start_dt = datetime(2026, 1, 12, 13, 30)   # 1:30pm
    end_dt   = datetime(2026, 1, 12, 15, 0)   # 3:00pm

    uv = get_uv_for_training(start_dt, end_dt, location="Adelaide")

    print("UV Test for Adelaide 1pm–3pm:")
    print(f"Start UV: {uv['uv_start']} ({uv['risk_start']})")
    print(f"End UV:   {uv['uv_end']} ({uv['risk_end']})")

     


     



