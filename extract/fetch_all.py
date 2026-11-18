import json
import time
from datetime import datetime
from pathlib import Path

import requests

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
CONFIG_PATH = Path("config/cities.json")
RAW_DIR = Path("data/raw")


def load_cities():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def fetch_city(city):
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone",
        "timezone": "Africa/Lagos",
        "past_days": 1,
        "forecast_days": 1,
    }
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw(city_name, data):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{city_name.lower().replace(' ', '_')}_{stamp}.json"
    path = RAW_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for city in load_cities():
        try:
            data = fetch_city(city)
            path = save_raw(city["name"], data)
            print(f"OK     {city['name']} -> {path}")
        except requests.RequestException as error:
            print(f"FAILED {city['name']}: {error}")
        time.sleep(1)  # be polite to the free API


if __name__ == "__main__":
    main()
