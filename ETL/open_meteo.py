import openmeteo_requests
import os
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta

# Setup Open-Meteo client with cache + retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Coords Los Angeles
lat, lon = 34.0522, -118.2437

# Dates limitées à 30 jours max
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": [
        "pm10", "pm2_5", "sulphur_dioxide", "carbon_dioxide",
        "nitrogen_dioxide", "ozone", "aerosol_optical_depth"
    ],
    "current": [
        "pm10", "pm2_5", "sulphur_dioxide", "nitrogen_dioxide",
        "ozone", "aerosol_optical_depth", "us_aqi"
    ],
    "timezone": "America/Los_Angeles",
    "timeformat": "unixtime",
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d"),
}

# API call
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# ---- Process current ----
current = response.Current()
print("Current AQI:", current.Variables(6).Value())

# ---- Process hourly ----
hourly = response.Hourly()
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "pm10": hourly.Variables(0).ValuesAsNumpy(),
    "pm2_5": hourly.Variables(1).ValuesAsNumpy(),
    "sulphur_dioxide": hourly.Variables(2).ValuesAsNumpy(),
    "carbon_dioxide": hourly.Variables(3).ValuesAsNumpy(),
    "nitrogen_dioxide": hourly.Variables(4).ValuesAsNumpy(),
    "ozone": hourly.Variables(5).ValuesAsNumpy(),
    "aerosol_optical_depth": hourly.Variables(6).ValuesAsNumpy()
}

df = pd.DataFrame(hourly_data)
df["date"] = df["date"].dt.tz_convert("America/Los_Angeles")  # Convert timezone

# Save
os.makedirs("data/air_quality", exist_ok=True)
df.to_csv("data/air_quality/air_quality_hourly.csv", index=False)

print(f"✅ Données sauvegardées : {len(df)} lignes")
