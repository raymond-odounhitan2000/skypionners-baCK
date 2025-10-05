FastAPI app for PM2.5 forecasting

Files:
- app.py: FastAPI application exposing endpoints:
  - POST /predict : accepts JSON {"history": [{"date": iso, "pm2_5": float, ...}], "horizons_min": [10,30]}
  - GET /predict_from_sources?lat={lat}&lon={lon} : fetches Open-Meteo and OpenAQ and returns preds
  - GET /health : health check

Run (in project venv):

```bash
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Notes:
- Requires packages `fastapi`, `uvicorn`, `httpx`, `joblib`, `pandas`.
- The model loader uses the `models/` directory; the RandomForest model is the default.
- The `/predict_from_sources` endpoint builds a very small synthetic history from external APIs — in production you'll want a real time-series buffer.

Flutter integration:
- The Flutter app should POST to `/predict` with the recent history (array of rows) in the same format used to train the model.
- The response contains `predictions` mapping horizon to predicted value and used artifact paths.
