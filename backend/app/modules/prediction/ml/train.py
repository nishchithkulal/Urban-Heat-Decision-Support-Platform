"""Train the heat-index regression model served by ``strategies.ml.MLHeatRiskStrategy``.

Run manually from ``backend/``:

    python -m app.modules.prediction.ml.train

**On the training data.** There is no licensed historical weather dataset with
ground-truth "how hot did this actually feel" labels bundled with this project, so
this trains on synthetically generated data instead of real observations. The label
is not arbitrary, though: it is the exact NWS heat-index formula
(``heat_index.heat_index_celsius``) plus a bounded, explicitly-synthetic wind-cooling
adjustment (``_wind_cooling_c``) representing evaporative cooling at higher wind
speeds -- a real physical effect, but one the closed-form NWS formula does not model
at all. That gives the model something genuine to learn beyond re-deriving a formula
it could just call directly, and gives the ML strategy a real reason to differ from
the baseline strategy rather than being a slower way to compute the same number.

This is intentionally the smallest honest version of the full MLOps loop (generate
data -> train -> evaluate -> serialize -> load -> serve) that Phase 7 exists to
establish. Swapping in real historical weather + outcome data later changes this file
and the feature list in ``strategies.ml``, not the serving path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from app.modules.prediction.heat_index import heat_index_celsius

MODEL_VERSION = "gradient-boosting-v1"
FEATURE_NAMES = ("temperature_c", "humidity_percent", "wind_speed_kph")

_DEFAULT_SAMPLE_COUNT = 5000
_DEFAULT_SEED = 42


def _wind_cooling_c(wind_speed_kph: np.ndarray) -> np.ndarray:
    # Explicitly synthetic, not a validated meteorological formula: a bounded
    # evaporative-cooling-style effect (capped at 4C) that increases with wind speed.
    # See the module docstring for why this exists.
    return np.minimum(wind_speed_kph * 0.15, 4.0)


@dataclass(frozen=True)
class TrainingData:
    features: np.ndarray
    labels: np.ndarray


def generate_training_data(
    *, sample_count: int = _DEFAULT_SAMPLE_COUNT, seed: int = _DEFAULT_SEED
) -> TrainingData:
    rng = np.random.default_rng(seed)
    temperature_c = rng.uniform(-10.0, 50.0, size=sample_count)
    humidity_percent = rng.uniform(0.0, 100.0, size=sample_count)
    wind_speed_kph = rng.uniform(0.0, 60.0, size=sample_count)

    labels = np.array(
        [
            heat_index_celsius(temperature_c=t, humidity_percent=h)
            for t, h in zip(temperature_c, humidity_percent, strict=True)
        ]
    ) - _wind_cooling_c(wind_speed_kph)

    features = np.column_stack([temperature_c, humidity_percent, wind_speed_kph])
    return TrainingData(features=features, labels=labels)


def train_model(data: TrainingData, *, seed: int = _DEFAULT_SEED) -> tuple[Any, float]:
    """Fit the regressor and return it along with test-set MAE (degrees Celsius)."""
    x_train, x_test, y_train, y_test = train_test_split(
        data.features, data.labels, test_size=0.2, random_state=seed
    )
    model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=seed)
    model.fit(x_train, y_train)
    mae = float(mean_absolute_error(y_test, model.predict(x_test)))
    return model, mae


def save_model(model: Any, *, mae: float, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)

    metadata = {
        "version": MODEL_VERSION,
        "feature_names": list(FEATURE_NAMES),
        "test_mae_celsius": mae,
        "trained_at": datetime.now(UTC).isoformat(),
    }
    path.with_suffix(".meta.json").write_text(json.dumps(metadata, indent=2))


def main() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    data = generate_training_data()
    model, mae = train_model(data)
    model_path = Path(settings.ml_model_path)
    save_model(model, mae=mae, path=model_path)
    print(f"Saved model to {model_path} (test MAE: {mae:.3f} C)")


if __name__ == "__main__":
    main()
