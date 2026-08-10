import json
from pathlib import Path
from typing import Any

from backend.app.config.settings import settings
from backend.app.schemas.reasoning_schema import ClinicalReasoningRequest


class ContextBuilder:
    """
    Builds deterministic structured context from:
    - patient context
    - semantic evidence derived from existing DDXPlus metadata
    - clinical rule results
    - existing differential
    - knowledge base entries

    The upstream ML feature contract is never modified here.
    Rank, disease, probability, and confidence are preserved exactly.
    """

    _evidence_metadata_cache: dict[str, dict[str, Any]] | None = None

    @classmethod
    def _load_evidence_metadata(cls) -> dict[str, dict[str, Any]]:
        if cls._evidence_metadata_cache is not None:
            return cls._evidence_metadata_cache

        backend_root = Path(__file__).resolve().parents[3]

        metadata_path = (
            backend_root
            / "models"
            / "respiratory"
            / "metadata"
            / "ddxplus_evidence_metadata.json"
        )

        with metadata_path.open("r", encoding="utf-8-sig") as file:
            payload = json.load(file)

        evidences = payload.get("evidences")

        if not isinstance(evidences, dict):
            raise RuntimeError(
                "DDXPlus evidence metadata is missing or invalid."
            )

        cls._evidence_metadata_cache = evidences
        return evidences

    @staticmethod
    def _decode_evidence_token(
        token: str,
    ) -> tuple[str, str | None, bool]:
        """
        Decode model evidence without changing the original token.

        Examples:
            INITIAL::E_77
                -> E_77, None, True

            E_66
                -> E_66, None, False

            E_130_@_V_11
                -> E_130, V_11, False

            E_132_@_3
                -> E_132, 3, False
        """
        raw_token = str(token).strip()

        is_initial = raw_token.startswith("INITIAL::")

        if is_initial:
            raw_token = raw_token.removeprefix("INITIAL::")

        if "_@_" in raw_token:
            code, encoded_value = raw_token.split("_@_", 1)
            return code, encoded_value, is_initial

        return raw_token, None, is_initial

    @classmethod
    def _semantic_evidence_item(
        cls,
        token: str,
        *,
        source: str,
    ) -> dict[str, Any]:
        code, encoded_value, is_initial = cls._decode_evidence_token(
            token
        )

        metadata = cls._load_evidence_metadata()
        details = metadata.get(code, {})

        question = details.get("question_en")

        if not isinstance(question, str) or not question.strip():
            question = (
                f"Human-readable metadata unavailable for evidence {code}."
            )

        item: dict[str, Any] = {
            "Code": code,
            "Original_Token": token,
            "Clinical_Meaning": question.strip(),
            "Source": source,
            "Observed": True,
        }

        if is_initial:
            item["Initial_Evidence"] = True

        if encoded_value is not None:
            item["Encoded_Value"] = encoded_value

            value_meaning = details.get("value_meaning", {})

            if isinstance(value_meaning, dict):
                meaning = value_meaning.get(encoded_value)

                if meaning is not None:
                    item["Value_Meaning"] = str(meaning)
                else:
                    item["Value_Meaning"] = (
                        f"Encoded selected value: {encoded_value}"
                    )
            else:
                item["Value_Meaning"] = (
                    f"Encoded selected value: {encoded_value}"
                )

        return item

    @classmethod
    def _build_semantic_evidence(
        cls,
        patient_context: dict[str, Any],
    ) -> dict[str, Any]:
        observed: list[dict[str, Any]] = []

        initial_evidence = str(
            patient_context.get("initial_evidence", "")
        ).strip()

        if initial_evidence:
            observed.append(
                cls._semantic_evidence_item(
                    f"INITIAL::{initial_evidence}",
                    source="initial_evidence",
                )
            )

        positive_tokens = patient_context.get(
            "positive_evidence_tokens",
            [],
        )

        if isinstance(positive_tokens, list):
            for token in positive_tokens:
                token_text = str(token).strip()

                if not token_text:
                    continue

                observed.append(
                    cls._semantic_evidence_item(
                        token_text,
                        source="questionnaire_positive_evidence",
                    )
                )

        answered_codes = patient_context.get(
            "answered_question_codes",
            [],
        )

        if not isinstance(answered_codes, list):
            answered_codes = []

        return {
            "Observed_Clinical_Evidence": observed,
            "Explicitly_Answered_Question_Codes": [
                str(code)
                for code in answered_codes
            ],
            "Evidence_Interpretation": {
                "initial_evidence_is_observed": True,
                "observed_evidence_is_present": True,
                "answered_question_codes_are_supplied": True,
                "raw_model_tokens_are_preserved": True,
            },
        }

    @classmethod
    def build_context(
        cls,
        request: ClinicalReasoningRequest,
    ) -> str:
        max_candidates = settings.REASONING_MAX_CANDIDATES
        candidates = request.differential[:max_candidates]

        context_data = {
            "Patient_Context": request.patient_context,
            "Semantic_Evidence_Context": cls._build_semantic_evidence(
                request.patient_context
            ),
            "Clinical_Rules_Evaluated": request.rules.model_dump(),
            "Ranked_Differential_Candidates": [],
        }

        for candidate in candidates:
            candidate_dict = {
                "Rank": candidate.rank,
                "Disease": candidate.disease,
                "Probability": candidate.probability,
                "Confidence": candidate.confidence,
                "Knowledge_Available": False,
            }

            if candidate.knowledge:
                candidate_dict["Knowledge_Available"] = True
                candidate_dict["Knowledge"] = (
                    candidate.knowledge.model_dump()
                )

            context_data[
                "Ranked_Differential_Candidates"
            ].append(candidate_dict)

        return json.dumps(context_data, indent=2)
