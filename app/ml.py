from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).resolve().parent.parent / "model.pkl"

FEATURE_COLUMNS = [
    "distance_km",
    "time_of_day",
    "day_of_week",
    "ngo_accept_rate",
    "ngo_avg_response_time",
    "past_pickups",
    "recent_activity_count",
    "is_active",
    "ngo_reliability_score",
]


@dataclass
class NGOFeatureRow:
    distance_km: float
    time_of_day: int
    day_of_week: int
    ngo_accept_rate: float
    ngo_avg_response_time: float
    past_pickups: int
    recent_activity_count: int
    is_active: int
    ngo_reliability_score: float

    def to_dict(self) -> dict:
        return {
            "distance_km": self.distance_km,
            "time_of_day": self.time_of_day,
            "day_of_week": self.day_of_week,
            "ngo_accept_rate": self.ngo_accept_rate,
            "ngo_avg_response_time": self.ngo_avg_response_time,
            "past_pickups": self.past_pickups,
            "recent_activity_count": self.recent_activity_count,
            "is_active": self.is_active,
            "ngo_reliability_score": self.ngo_reliability_score,
        }


def _build_seed_dataset(size: int = 600) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    distance = rng.uniform(0.3, 20.0, size)
    time_of_day = rng.integers(0, 24, size)
    day_of_week = rng.integers(0, 7, size)
    accept_rate = rng.uniform(0.3, 0.95, size)
    avg_response = rng.uniform(5, 25, size)
    past_pickups = rng.integers(10, 300, size)
    recent_activity = rng.integers(0, 8, size)
    is_active = rng.integers(0, 2, size)
    reliability = accept_rate * (1.0 / avg_response) * np.log1p(past_pickups)

    score = (
        1.4 * accept_rate
        + 0.8 * (1.0 / (1.0 + distance))
        + 0.7 * reliability
        + 0.2 * is_active
        + 0.15 * (recent_activity / 7.0)
        - 0.5 * (avg_response / 25.0)
    )

    y = (score > np.percentile(score, 45)).astype(int)

    return pd.DataFrame(
        {
            "distance_km": distance,
            "time_of_day": time_of_day,
            "day_of_week": day_of_week,
            "ngo_accept_rate": accept_rate,
            "ngo_avg_response_time": avg_response,
            "past_pickups": past_pickups,
            "recent_activity_count": recent_activity,
            "is_active": is_active,
            "ngo_reliability_score": reliability,
            "accepted": y,
        }
    )


def train_initial_model(force: bool = False) -> None:
    if MODEL_PATH.exists() and not force:
        return
    df = _build_seed_dataset()
    model = RandomForestClassifier(n_estimators=250, random_state=42)
    model.fit(df[FEATURE_COLUMNS], df["accepted"])
    joblib.dump(model, MODEL_PATH)


def load_model() -> RandomForestClassifier:
    train_initial_model()
    return joblib.load(MODEL_PATH)


def predict_acceptance(rows: list[NGOFeatureRow]) -> list[float]:
    if not rows:
        return []
    model = load_model()
    df = pd.DataFrame([row.to_dict() for row in rows], columns=FEATURE_COLUMNS)
    probabilities = model.predict_proba(df)[:, 1]
    return probabilities.tolist()


def retrain_from_frame(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"retrained": False, "reason": "No log data available"}

    for col in FEATURE_COLUMNS:
        if col not in frame.columns:
            return {"retrained": False, "reason": f"Missing feature column: {col}"}

    if "accepted" not in frame.columns:
        return {"retrained": False, "reason": "Missing target column: accepted"}

    model = RandomForestClassifier(n_estimators=250, random_state=42)
    model.fit(frame[FEATURE_COLUMNS], frame["accepted"])
    joblib.dump(model, MODEL_PATH)
    return {"retrained": True, "rows": int(len(frame))}
