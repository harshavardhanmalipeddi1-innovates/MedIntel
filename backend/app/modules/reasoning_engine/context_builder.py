import json
from backend.app.schemas.reasoning_schema import ClinicalReasoningRequest
from backend.app.config.settings import settings


class ContextBuilder:
    """
    Builds deterministic structured context from:
    - patient context
    - clinical rule results
    - existing differential
    - knowledge base entries

    Ensures that rank, disease, probability, and confidence are exactly preserved.
    """

    @staticmethod
    def build_context(request: ClinicalReasoningRequest) -> str:
        # Respect the REASONING_MAX_CANDIDATES limit
        max_candidates = settings.REASONING_MAX_CANDIDATES
        candidates = request.differential[:max_candidates]

        context_data = {
            "Patient_Context": request.patient_context,
            "Clinical_Rules_Evaluated": request.rules.model_dump(),
            "Ranked_Differential_Candidates": []
        }

        for candidate in candidates:
            # We strictly preserve the original values
            candidate_dict = {
                "Rank": candidate.rank,
                "Disease": candidate.disease,
                "Probability": candidate.probability,
                "Confidence": candidate.confidence,
                "Knowledge_Available": False
            }

            if candidate.knowledge:
                candidate_dict["Knowledge_Available"] = True
                candidate_dict["Knowledge"] = candidate.knowledge.model_dump()
            
            context_data["Ranked_Differential_Candidates"].append(candidate_dict)

        return json.dumps(context_data, indent=2)
