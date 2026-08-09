import numpy as np

from backend.services.prediction_service import PredictionService


def test_prediction_service_initialization():
    service = PredictionService()

    assert service is not None
    assert hasattr(service, "_loader")


def test_primary_prediction_structure():
    service = PredictionService()

    features = np.zeros(10)

    result = service.predict_primary_disease(features)

    assert isinstance(result, dict)
    assert "predictions" in result
    assert "model" in result
    assert "status" in result
    assert result["model"] == "xgboost"
    assert result["status"] == "success"


def test_supported_prediction_structure():
    service = PredictionService()

    features = np.zeros(10)

    result = service.predict_supported_conditions(features)

    assert isinstance(result, dict)
    assert "predictions" in result
    assert result["model"] == "xgboost"

def test_prediction_service_uses_trained_class_names():
    service = PredictionService()

    probabilities = np.array([0.20, 0.10, 0.70])

    predictions = service._format_predictions(probabilities)

    assert predictions[0]["condition"] == "Bronchiectasis"
    assert predictions[1]["condition"] == "Acute COPD exacerbation / infection"
    assert predictions[2]["condition"] == "Acute laryngitis"

    assert all(
        not item["condition"].startswith("condition_")
        for item in predictions
    )
