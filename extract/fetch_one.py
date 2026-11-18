import requests
import json
from datetime import datetime

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

params = {
    "latitude": 9.0765,      # Abuja
    "longitude": 7.3986,
    "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone",
    "timezone": "Africa/Lagos",
    "past_days": 1,
    "forecast_days": 1,
}

response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()   # stops with an error if the request failed
data = response.json()        # turns the reply into a Python dictionary

print("Top-level keys:", list(data.keys()))
print("First 3 times:", data["hourly"]["time"][:3])
print("First 3 PM2.5 values:", data["hourly"]["pm2_5"][:3])
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
path = f"data/raw/abuja_{stamp}.json"

with open(path, "w") as f:
    json.dump(data, f)

print("Saved to", path)
