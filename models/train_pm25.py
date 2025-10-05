from __future__ import annotations
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error


def _prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-based features and lag features for pm2_5.

    Assumes df index is a DatetimeIndex at 10-minute frequency.
    """
    df = df.copy()
    # time features
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month

    # lag features (previous 1 and 6 steps -> 10min and 60min)
    df["pm2_5_lag_1"] = df["pm2_5"].shift(1)
    df["pm2_5_lag_6"] = df["pm2_5"].shift(6)

    # drop rows with NA from lagging
    df = df.dropna()
    return df


def train_pm25(output_path: str | None = None, horizons_min: list[int] | None = None) -> dict:
    """Train PM2.5 forecasting model(s) for given horizons and save artifacts.

    By default trains for 10 and 30 minutes horizons. Each horizon produces
    one RandomForest model saved under the models folder as
    `pm25_model_h{minutes}m.joblib`.

    Args:
        output_path: directory where model and scaler will be saved. If None,
            defaults to `models/` folder.
        horizons_min: list of integer horizons in minutes (e.g. [10, 30]).

    Returns:
        dict with metrics and artifact paths for each horizon.
    """
    if horizons_min is None:
        horizons_min = [10, 30]
    repo_root = Path(__file__).resolve().parent.parent
    data_file = repo_root / "data" / "air_quality" / "air_quality_hourly.csv"
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")

    df = pd.read_csv(data_file, parse_dates=["date"])  # timezone-aware strings
    # set index
    df = df.set_index("date")

    # convert to pandas datetime (keep timezone info) and sort
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Resample to 10-minute frequency using linear interpolation
    df_10 = df.resample("10T").interpolate(method="time")

    # Keep relevant columns
    if "pm2_5" not in df_10.columns:
        raise KeyError("pm2_5 column not found in data")

    # prepare features
    df_feat = _prepare_features(df_10)

    feature_cols = [
        "pm2_5",
        "pm2_5_lag_1",
        "pm2_5_lag_6",
        "hour",
        "minute",
        "dayofweek",
        "month",
        # include some other pollutant columns if present
    ]
    # add available pollutant columns
    for col in ["pm10", "sulphur_dioxide", "carbon_dioxide", "nitrogen_dioxide", "ozone", "aerosol_optical_depth"]:
        if col in df_feat.columns:
            feature_cols.append(col)

    X = df_feat[feature_cols].values
    # prepare scaler on full feature set (fit on training portion later per-horizon)
    out_dir = Path(output_path) if output_path is not None else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict = {"artifacts": {}}

    # convert horizons in minutes to steps based on 10-minute frequency
    def minutes_to_steps(m: int) -> int:
        if m % 10 != 0:
            raise ValueError("Horizon must be a multiple of 10 minutes with current sampling")
        return m // 10

    for h_min in horizons_min:
        steps = minutes_to_steps(h_min)
        # create target for this horizon
        df_h = df_feat.copy()
        df_h["target"] = df_h["pm2_5"].shift(-steps)
        df_h = df_h.dropna()

        X = df_h[feature_cols].values
        y = df_h["target"].values

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train_scaled, y_train)

        preds = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, preds)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))

        model_name = f"pm25_model_h{h_min}m.joblib"
        scaler_name = f"pm25_scaler_h{h_min}m.joblib"
        model_path = out_dir / model_name
        scaler_path = out_dir / scaler_name
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        results["artifacts"][f"h{h_min}m"] = {
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
            "mae": float(mae),
            "rmse": float(rmse),
            "trained_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
        }
        print(f"Trained horizon {h_min}m — MAE={mae:.4f} RMSE={rmse:.4f} — saved {model_path}")

    return results


def _make_features_from_history(history: pd.DataFrame) -> pd.DataFrame:
    """Build features for prediction from recent history.

    history must be a DataFrame indexed by datetime at 10-minute frequency and
    contain at least the columns used for features (pm2_5, optionally pollutants).
    The function returns a single-row DataFrame of features aligned to the last timestamp.
    """
    # ensure index sorted
    df = history.sort_index().copy()
    # resample/interpolate to 10-minute index if needed
    df.index = pd.to_datetime(df.index)
    df = df.resample("10T").interpolate(method="time")

    # need at least 7 rows to compute lag_6 and predict next step (since lags use shift)
    if len(df) < 7:
        raise ValueError("history must contain at least 7 10-minute rows (to compute lag_6)")

    # use the latest rows to compute features; reuse _prepare_features then take last row
    df_feat = _prepare_features(df)
    return df_feat.iloc[[-1]]


def predict_pm25_from_history(history: pd.DataFrame, models_dir: str | None = None, horizons_min: list[int] | None = None) -> dict:
    """Given recent history, predict PM2.5 for requested horizons.

    Args:
        history: pandas DataFrame with datetime index and columns including 'pm2_5'.
        models_dir: directory where saved models/scalers live (defaults to models/).
        horizons_min: list of horizons in minutes to predict (defaults to [10,30]).

    Returns:
        dict mapping horizon to predicted value (float) and used artifact paths.
    """
    if horizons_min is None:
        horizons_min = [10, 30]
    out_dir = Path(models_dir) if models_dir is not None else Path(__file__).resolve().parent

    feat_row = _make_features_from_history(history)

    # determine feature columns from training code
    feature_cols = [
        "pm2_5",
        "pm2_5_lag_1",
        "pm2_5_lag_6",
        "hour",
        "minute",
        "dayofweek",
        "month",
    ]
    for col in ["pm10", "sulphur_dioxide", "carbon_dioxide", "nitrogen_dioxide", "ozone", "aerosol_optical_depth"]:
        if col in feat_row.columns:
            feature_cols.append(col)

    X_row = feat_row[feature_cols].values

    preds: dict = {}
    for h in horizons_min:
        model_path = out_dir / f"pm25_model_h{h}m.joblib"
        scaler_path = out_dir / f"pm25_scaler_h{h}m.joblib"
        if not model_path.exists() or not scaler_path.exists():
            preds[f"h{h}m"] = {"error": "model/scaler not found", "model_path": str(model_path), "scaler_path": str(scaler_path)}
            continue
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        Xs = scaler.transform(X_row)
        val = float(model.predict(Xs)[0])
        preds[f"h{h}m"] = {"prediction": val, "model_path": str(model_path), "scaler_path": str(scaler_path)}

    return preds


if __name__ == "__main__":
    out = train_pm25()
    print(out)
