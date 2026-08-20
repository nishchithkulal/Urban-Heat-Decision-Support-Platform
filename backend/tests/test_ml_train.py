from __future__ import annotations

import json
from pathlib import Path

from app.modules.prediction.ml.train import (
    MODEL_VERSION,
    generate_training_data,
    save_model,
    train_model,
)


def test_generate_training_data_is_deterministic_for_a_fixed_seed() -> None:
    first = generate_training_data(sample_count=50, seed=1)
    second = generate_training_data(sample_count=50, seed=1)

    assert (first.features == second.features).all()
    assert (first.labels == second.labels).all()


def test_generate_training_data_shapes_match() -> None:
    data = generate_training_data(sample_count=50, seed=1)

    assert data.features.shape == (50, 3)
    assert data.labels.shape == (50,)


def test_train_model_produces_reasonable_predictions() -> None:
    # A small sample keeps this test fast while still exercising the real
    # fit/predict/evaluate path end to end (not a mocked model).
    data = generate_training_data(sample_count=300, seed=1)

    model, mae = train_model(data, seed=1)

    assert mae < 5.0
    # A hot, humid point should predict a higher heat index than a cool, dry one --
    # sanity that the model learned *something* about the relationship, not just a
    # constant.
    hot_humid = model.predict([[40.0, 80.0, 5.0]])[0]
    cool_dry = model.predict([[10.0, 20.0, 5.0]])[0]
    assert hot_humid > cool_dry


def test_save_model_writes_an_artifact_and_metadata(tmp_path: Path) -> None:
    data = generate_training_data(sample_count=200, seed=1)
    model, mae = train_model(data, seed=1)
    model_path = tmp_path / "nested" / "model.joblib"

    save_model(model, mae=mae, path=model_path)

    assert model_path.exists()
    meta_path = model_path.with_suffix(".meta.json")
    assert meta_path.exists()
    metadata = json.loads(meta_path.read_text())
    assert metadata["version"] == MODEL_VERSION
    assert metadata["feature_names"] == [
        "temperature_c",
        "humidity_percent",
        "wind_speed_kph",
    ]
