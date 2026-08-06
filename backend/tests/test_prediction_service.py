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