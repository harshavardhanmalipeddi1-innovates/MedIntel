import logging
from typing import Any, Dict, List
import numpy as np
import pandas as pd
from scipy import sparse

from app.ml.artifact_manager import ArtifactManager
from app.ml.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Construct runtime feature vectors for Respiratory XGBoost models.

    This class does **not** load models or perform inference. It relies on
    :class:`ArtifactManager` for preprocessing objects (e.g. a
    ``HashingVectorizer`` for evidence tokens, a ``MultiLabelBinarizer`` for
    categorical encodings, and the definitive ``feature_names`` order.
    """

    def __init__(self, artifact_manager: ArtifactManager | None = None, model_loader: ModelLoader | None = None) -> None:
        self._artifact_manager = artifact_manager or ArtifactManager()
        self._model_loader = model_loader or ModelLoader()
        self._bundle = None  # Lazy‑loaded preprocessing bundle
        self._logger = logger

    # ---------------------------------------------------------------------
    # Lazy accessors
    # ---------------------------------------------------------------------
    @property
    def preprocessing_bundle(self) -> Any:
        """Return the cached preprocessing bundle, loading it on first use.

        The bundle is expected to expose:
        * ``feature_names`` – ordered list of all model features
        * ``dense_feature_names`` – numeric feature column identifiers
        * ``evidence_encoder`` – a ``HashingVectorizer`` or compatible transformer
        * ``mlb`` – a ``MultiLabelBinarizer`` for any multi‑label columns
        """
        if self._bundle is None:
            self._bundle = self._artifact_manager.get_preprocessing_bundle()
            self._logger.debug("Preprocessing bundle loaded lazily")
        return self._bundle

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def get_feature_names(self) -> List[str]:
        """Return the exact feature order required by the XGBoost models."""
        return list(self.preprocessing_bundle.feature_names)

    def validate_input(self, data: Dict[str, Any]) -> None:
        """Validate that the supplied ``data`` dictionary contains required fields.

        Required keys are inferred from the preprocessing bundle:
        * All entries in ``dense_feature_names``
        * ``evidence_tokens`` – a list of free‑text tokens describing physician findings.
        Raises ``RuntimeError`` with a descriptive message on failure.
        """
        missing = []
        for field in getattr(self.preprocessing_bundle, "dense_feature_names", []):
            if field not in data:
                missing.append(field)
        if "evidence_tokens" not in data:
            missing.append("evidence_tokens")
        if missing:
            msg = f"Input data missing required fields: {', '.join(missing)}"
            self._logger.error(msg)
            raise RuntimeError(msg)
        self._logger.debug("Input validation passed")

    def build_dense_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Construct the dense numeric feature matrix.

        The function extracts the columns defined in ``dense_feature_names``
        from ``data``. Missing values are set to ``np.nan``. The returned
        array has shape ``(1, n_features)``.
        """
        feature_names = getattr(self.preprocessing_bundle, "dense_feature_names", [])
        values = []
        for name in feature_names:
            val = data.get(name, np.nan)
            if isinstance(val, (bool, int, float)):
                val = float(val)
            values.append(val)
        dense_array = np.array(values, dtype=float).reshape(1, -1)
        self._logger.debug("Dense feature array shape: %s", dense_array.shape)
        return dense_array

    def encode_evidence(self, tokens: List[str]) -> sparse.csr_matrix:
        """Encode free‑text evidence tokens using the bundled vectorizer.

        ``tokens`` is expected to be a list of strings; the vectorizer works on a
        single document, so we ``' '.join`` the tokens before transformation.
        """
        if not isinstance(tokens, list):
            raise RuntimeError("evidence_tokens must be a list of strings")
        text = " ".join(tokens)
        vectorizer = getattr(self.preprocessing_bundle, "evidence_encoder")
        encoded = vectorizer.transform([text])
        self._logger.debug("Evidence encoding shape: %s", encoded.shape)
        return encoded

    def build_feature_vector(self, data: Dict[str, Any]) -> sparse.csr_matrix:
        """Combine dense and evidence representations into the final feature matrix.

        The resulting matrix aligns with ``self.get_feature_names()`` – the order
        of columns is dense features followed by the sparse evidence columns.
        """
        self.validate_input(data)
        dense = self.build_dense_features(data)
        evidence = self.encode_evidence(data["evidence_tokens"])
        dense_csr = sparse.csr_matrix(dense)
        combined = sparse.hstack([dense_csr, evidence], format="csr")
        expected_len = len(self.get_feature_names())
        if combined.shape[1] != expected_len:
            msg = f"Feature vector column count {combined.shape[1]} does not match expected {expected_len}."
            self._logger.error(msg)
            raise RuntimeError(msg)
        if np.isnan(combined.data).any():
            self._logger.error("NaN values detected in feature matrix")
            raise RuntimeError("Feature matrix contains NaN values")
        self._logger.debug("Final feature matrix shape: %s", combined.shape)
        return combined

# End of FeatureBuilder implementation

