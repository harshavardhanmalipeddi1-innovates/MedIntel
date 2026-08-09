import logging
from typing import Any, Dict, List, Callable

import numpy as np
import xgboost as xgb

from backend.app.ml.artifact_manager import ArtifactManager
from backend.services.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service layer for MedIntel XGBoost inference.

    Responsible for:
    - Primary disease ranking
    - Supported condition ranking
    - Differential diagnosis generation

    This module does NOT provide final diagnosis.
    Clinical confirmation remains with the doctor.
    """

    def __init__(self) -> None:
        self._loader = ModelLoader()
        self._artifact_manager = ArtifactManager()

        self._primary_model: xgb.Booster | None = None
        self._supported_model: xgb.Booster | None = None
        self._class_names: List[str] | None = None

        logger.info("PredictionService initialized")

    def _get_class_names(self) -> List[str]:
        """Return the trained model class names in authoritative output order."""

        if self._class_names is None:
            metadata = self._artifact_manager.get_metadata()
            class_names = metadata.get("class_names")

            if (
                not isinstance(class_names, list)
                or not class_names
                or not all(
                    isinstance(name, str) and name.strip()
                    for name in class_names
                )
            ):
                raise RuntimeError(
                    "Respiratory model metadata contains invalid class_names."
                )

            self._class_names = list(class_names)

        return self._class_names

    def _ensure_model(
        self,
        attribute: str,
        loader_function: Callable[[], xgb.Booster]
    ) -> xgb.Booster:

        model = getattr(self, attribute)

        if model is None:
            model = loader_function()
            setattr(self, attribute, model)

        return model

    def _predict(
        self,
        model: xgb.Booster,
        features: np.ndarray
    ) -> np.ndarray:

        try:
            data = xgb.DMatrix(features.reshape(1, -1))
            prediction = model.predict(data)
            return np.asarray(prediction)

        except Exception as error:
            logger.error(
                "Prediction failed: %s",
                error
            )
            return np.array([])

    def _format_predictions(
        self,
        probabilities: np.ndarray
    ) -> List[Dict[str, Any]]:

        if probabilities.size == 0:
            return []

        probabilities = probabilities.flatten()
        class_names = self._get_class_names()

        if probabilities.size > len(class_names):
            raise RuntimeError(
                "Prediction output contains more classes than model metadata."
            )

        results = []

        for index in np.argsort(probabilities)[::-1]:

            probability = float(probabilities[index])

            confidence = (
                "high"
                if probability >= 0.75
                else "medium"
                if probability >= 0.50
                else "low"
            )

            results.append(
                {
                    "condition": class_names[index],
                    "probability": probability,
                    "confidence": confidence
                }
            )

        return results

    def predict_primary_disease(
        self,
        features: np.ndarray
    ) -> Dict[str, Any]:

        model = self._ensure_model(
            "_primary_model",
            self._loader.load_primary_model
        )

        predictions = self._predict(
            model,
            features
        )

        return {
            "predictions": self._format_predictions(predictions),
            "model": "xgboost",
            "status": "success"
        }

    def predict_supported_conditions(
        self,
        features: np.ndarray
    ) -> Dict[str, Any]:

        model = self._ensure_model(
            "_supported_model",
            self._loader.load_supported_scope_model
        )

        predictions = self._predict(
            model,
            features
        )

        return {
            "predictions": self._format_predictions(predictions),
            "model": "xgboost",
            "status": "success"
        }

    def rank_differential_diagnosis(
        self,
        features: np.ndarray
    ) -> Dict[str, Any]:

        primary = self.predict_primary_disease(features)
        supported = self.predict_supported_conditions(features)

        combined = (
            primary["predictions"]
            +
            supported["predictions"]
        )

        combined.sort(
            key=lambda x: x["probability"],
            reverse=True
        )

        return {
            "predictions": combined,
            "model": "xgboost",
            "status": "success"
        }