import pytest
from backend.app.schemas.reasoning_schema import (
    ClinicalReasoningRequest,
    ClinicalReasoningResponse,
    ReasoningDifferentialItem,
    CandidateReasoning,
    ClinicalRuleResult
)
from backend.app.schemas.knowledge_schema import DiseaseKnowledge
from backend.services.verification_service import VerificationService

def test_verification_service():
    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
                knowledge=DiseaseKnowledge(
                    disease_id="pneumonia",
                    name="Pneumonia",
                    description="Test knowledge record for pneumonia.",
                    knowledge_version="test-v1",
                    red_flags=["High fever > 39C"],
                    recommended_investigations=["Chest X-Ray"],
                    common_symptoms=[],
                    associated_symptoms=[],
                    physical_examination=[],
                    differential_diagnoses=[],
                    contraindications=[]
                )
            )
        ]
    )
    res = ClinicalReasoningResponse(
        candidate_reasoning=[],
        reasoning_summary="Test clinical reasoning summary.",
        requires_doctor_review=True,
        red_flags_to_review=["Patient has severe dyspnea"]
    )
    
    service = VerificationService()
    plan = service.generate_verification_plan(req, res)
    
    # Expect 1 from KB red flags, 1 from KB investigations, 1 from AI red flag
    assert len(plan.suggested_steps) == 3
    assert any(s.is_red_flag for s in plan.suggested_steps)
    assert any(s.category == "imaging" for s in plan.suggested_steps)


