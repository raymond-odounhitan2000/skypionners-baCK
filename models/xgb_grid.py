from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from xgboost import XGBRegressor
except Exception as e:
    XGBRegressor = None


def _load_and_prepare(resample_rule: str = "10T") -> pd.DataFrame:
    repo_root = Path(__file__).resolve().parent.parent
    data_file = repo_root / "data" / "air_quality" / "air_quality_hourly.csv"
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")

    df = pd.read_csv(data_file, parse_dates=["date"]).set_index("date")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.resample(resample_rule).interpolate(method="time")

    # create features similar to train_pm25
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month
    df["pm2_5_lag_1"] = df["pm2_5"].shift(1)
    df["pm2_5_lag_6"] = df["pm2_5"].shift(6)
    df = df.dropna()
    return df


def grid_search_xgb(horizons_min: list[int] | None = None, param_grid: dict | None = None, cv_splits: int = 3, n_jobs: int = -1, output_dir: str | None = None) -> dict:
    """Run GridSearch for XGBRegressor for each horizon and save final models.

    Returns a dict summarizing best params and test scores for each horizon.
    """
    if XGBRegressor is None:
        raise RuntimeError("xgboost is not installed in the environment. Please install it (pip install xgboost) and retry.")

    if horizons_min is None:
        horizons_min = [10, 30]

    if param_grid is None:
        param_grid = {
            "xgb__n_estimators": [50, 100],
            "xgb__max_depth": [3, 6],
            "xgb__learning_rate": [0.1, 0.01],
        }

    df = _load_and_prepare("10T")

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
        if col in df.columns:
            feature_cols.append(col)

    out_dir = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict = {"artifacts": {}}

    def minutes_to_steps(m: int) -> int:
        if m % 10 != 0:
            raise ValueError("Horizon must be multiple of 10 minutes")
        return m // 10

    for h in horizons_min:
        steps = minutes_to_steps(h)
        df_h = df.copy()
        df_h["target"] = df_h["pm2_5"].shift(-steps)
        df_h = df_h.dropna()

        X = df_h[feature_cols].values
        y = df_h["target"].values

        # time-aware split: first 80% train, last 20% test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("xgb", XGBRegressor(objective="reg:squarederror", verbosity=0, n_jobs=1)),
        ])

        tscv = TimeSeriesSplit(n_splits=cv_splits)
        gs = GridSearchCV(pipeline, param_grid, cv=tscv, scoring="neg_mean_absolute_error", n_jobs=n_jobs, verbose=2)
        print(f"Running GridSearch for horizon {h} min (train samples={len(X_train)})...")
        gs.fit(X_train, y_train)

        best = gs.best_estimator_
        best_params = gs.best_params_
        cv_best_score = -gs.best_score_

        preds = best.predict(X_test)
        mae_test = float(mean_absolute_error(y_test, preds))
        rmse_test = float(np.sqrt(mean_squared_error(y_test, preds)))

        # retrain final model on full dataset using best params
        # extract xgb params (they are prefixed with 'xgb__')
        xgb_params = {k.split("__", 1)[1]: v for k, v in best_params.items() if k.startswith("xgb__")}
        final_model = XGBRegressor(objective="reg:squarederror", verbosity=0, n_jobs=-1, **xgb_params)
        scaler = StandardScaler()
        X_full = np.vstack([X_train, X_test])
        y_full = np.concatenate([y_train, y_test])
        X_full_scaled = scaler.fit_transform(X_full)
        final_model.fit(X_full_scaled, y_full)

        model_path = out_dir / f"pm25_xgb_h{h}m.joblib"
        scaler_path = out_dir / f"pm25_xgb_scaler_h{h}m.joblib"
        joblib.dump(final_model, model_path)
        joblib.dump(scaler, scaler_path)

        results["artifacts"][f"h{h}m"] = {
            "best_params": best_params,
            "cv_best_mae": float(cv_best_score),
            "test_mae": mae_test,
            "test_rmse": rmse_test,
            "model_path": str(model_path),
            "scaler_path": str(scaler_path),
        }

        print(f"Horizon {h}m — CV MAE={cv_best_score:.4f}, Test MAE={mae_test:.4f}, Test RMSE={rmse_test:.4f}")
        print(f"Saved final model to {model_path}")

    # write a small JSON summary
    summary_path = out_dir / "xgb_grid_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Grid search finished. Summary saved to {summary_path}")
    return results


if __name__ == "__main__":
    try:
        res = grid_search_xgb()
        print(res)
    except Exception as e:
        print("Error:", e)
