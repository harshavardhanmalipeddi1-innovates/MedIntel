from typing import List
from backend.app.schemas.reasoning_schema import (
    ClinicalReasoningRequest,
    ClinicalReasoningResponse
)

class SafetyValidator:
    """
    Ensures model outputs do not violate clinical safety boundaries.
    """

    @staticmethod
    def validate(request: ClinicalReasoningRequest, response: ClinicalReasoningResponse):
        # 1. requires_doctor_review must be True
        if response.requires_doctor_review is not True:
            raise ValueError("Safety Violation: requires_doctor_review was bypassed.")

        original_candidates = request.differential
        reasoning_candidates = response.candidate_reasoning

        # Match counts (assuming we sent up to max_candidates)
        # We need to see exactly how many were sent in the prompt.
        # It's better to just verify that every candidate returned matches the original list in order.
        
        # The prompt only sends up to max_candidates.
        from backend.app.config.settings import settings
        max_c = settings.REASONING_MAX_CANDIDATES
        expected_candidates = original_candidates[:max_c]

        if len(reasoning_candidates) != len(expected_candidates):
            raise ValueError("Safety Violation: Number of candidates was changed by the model.")

        for i, (orig, generated) in enumerate(zip(expected_candidates, reasoning_candidates)):
            if generated.rank != orig.rank:
                raise ValueError(f"Safety Violation: Candidate rank changed from {orig.rank} to {generated.rank}.")
            if generated.disease.lower() != orig.disease.lower():
                raise ValueError(f"Safety Violation: Candidate disease changed from {orig.disease} to {generated.disease}.")

        # If we passed all checks, it's safe.
        return True
