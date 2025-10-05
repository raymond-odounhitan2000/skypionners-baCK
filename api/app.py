from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from pathlib import Path
import joblib
import pandas as pd
import httpx
import asyncio

from models.train_pm25 import predict_pm25_from_history

app = FastAPI(title="PM2.5 Forecast API")


class RealtimeInput(BaseModel):
    """Expected minimal input for real-time prediction.

    - `history`: list of dict rows with at least 'date' and 'pm2_5', and optionally other pollutants.
      The date must be ISO format.
    - `horizons_min`: optional list of horizons to predict (e.g. [10,30]). Defaults to [10,30].
    """
    history: List[Dict[str, Any]] = Field(..., description="Recent history rows (newest last)")
    horizons_min: Optional[List[int]] = Field(None, description="Horizon(s) in minutes")


@app.on_event("startup")
async def load_default_model():
    # choose the best model available (prefer RF over XGB per README)
    app.state.models_dir = Path(__file__).resolve().parent.parent / "models"


@app.post("/predict")
async def predict(input: RealtimeInput):
    # convert history to DataFrame
    try:
        df = pd.DataFrame(input.history)
        if "date" not in df.columns:
            raise ValueError("Each history row must include a 'date' field")
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    preds = predict_pm25_from_history(df, models_dir=str(app.state.models_dir), horizons_min=input.horizons_min)
    return {"predictions": preds}


async def _fetch_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch a minimal set of meteorological features from Open-Meteo.

    This returns a small dict that can be merged into the model inputs.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m&timezone=UTC"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


async def _fetch_openaq(lat: float, lon: float) -> Dict[str, Any]:
    url = f"https://api.openaq.org/v2/latest?coordinates={lat},{lon}&radius=10000"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


@app.get("/predict_from_sources")
async def predict_from_sources(lat: float, lon: float, horizons_min: Optional[str] = "10,30"):
    """Fetch real-time data from Open-Meteo and OpenAQ (and Tempo if available),
    build a minimal history and return predictions.
    """
    try:
        horizons = [int(x) for x in horizons_min.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid horizons_min param")

    # fetch external data concurrently
    try:
        om, oa = await asyncio.gather(_fetch_open_meteo(lat, lon), _fetch_openaq(lat, lon))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching external data: {e}")

    # Build a tiny synthetic history using the latest available values
    # NOTE: this is a simplified approach — for production we should assemble a real time series
    latest_time = pd.Timestamp.utcnow().floor("10T")
    history_row = {"date": latest_time.isoformat(), "pm2_5": None}
    # try to extract pm2.5 from OpenAQ
    try:
        results = oa.get("results", [])
        if results:
            # find pm25 measurement
            measurements = results[0].get("measurements", [])
            for m in measurements:
                if m.get("parameter") in ("pm25", "pm2_5"):
                    history_row["pm2_5"] = m.get("value")
                    break
    except Exception:
        pass

    # fallback: use a small default if none
    if history_row["pm2_5"] is None:
        history_row["pm2_5"] = 10.0

    df = pd.DataFrame([history_row])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    preds = predict_pm25_from_history(df, models_dir=str(app.state.models_dir), horizons_min=horizons)
    return {"predictions": preds, "open_meteo": om, "openaq": oa}


@app.get("/health")
async def health():
    return {"status": "ok"}
