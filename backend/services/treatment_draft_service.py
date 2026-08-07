from backend.app.schemas.reasoning_schema import ClinicalReasoningRequest, ClinicalReasoningResponse
from backend.app.schemas.treatment_schema import TreatmentDraftResponse, TreatmentConsideration

class TreatmentDraftService:
    """
    Generates a draft of potential treatment considerations based ONLY on the
    validated differential and Knowledge Base. 
    Does not autonomously order medications or prescribe.
    """

    def generate_draft(
        self,
        request: ClinicalReasoningRequest,
        reasoning: ClinicalReasoningResponse
    ) -> TreatmentDraftResponse:
        
        considerations = []
        general_cautions = ["AI-Generated Draft: Not a final prescription. DOCTOR REVIEW REQUIRED."]

        # Ensure we only use established KB info, or generic safe advice.
        for candidate in request.differential:
            if candidate.knowledge:
                # Mock extraction of treatment from knowledge base
                # In a real scenario, KB would have a `treatment_options` field
                # For Phase 3.10, we'll provide standard supportive care suggestions.
                
                contra_concern = len(candidate.knowledge.contraindications) > 0
                cautions = candidate.knowledge.contraindications.copy()
                
                # Check for high-risk conditions
                if candidate.disease.lower() in ["pneumonia", "sepsis", "myocardial infarction"]:
                    cautions.append("High-risk condition: immediate clinical evaluation required.")
                    contra_concern = True

                considerations.append(
                    TreatmentConsideration(
                        candidate_disease=candidate.disease,
                        consideration=f"Evaluate standard clinical protocols for {candidate.disease}",
                        rationale="Derived from Knowledge Base recommendations.",
                        warnings=cautions,
                        missing_information=[],
                        contraindication_concern=contra_concern
                    )
                )

        return TreatmentDraftResponse(
            considerations=considerations,
            general_cautions=general_cautions
        )
