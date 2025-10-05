"""Models package for PM2.5 forecasting.

This package contains tools to train and save a scikit-learn model that
predicts PM2.5 at 10-minute intervals using the CSV files under
`data/air_quality`.

"""

from .train_pm25 import train_pm25, predict_pm25_from_history

__all__ = ["train_pm25", "predict_pm25_from_history"]
