import pytest
from backend.app.schemas.reasoning_schema import (
    ClinicalReasoningRequest,
    ClinicalReasoningResponse,
    ReasoningDifferentialItem,
    ClinicalRuleResult
)
from backend.app.schemas.knowledge_schema import DiseaseKnowledge
from backend.services.treatment_draft_service import TreatmentDraftService

def test_treatment_draft_service():
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
                    red_flags=[],
                    recommended_investigations=[],
                    common_symptoms=[],
                    associated_symptoms=[],
                    physical_examination=[],
                    differential_diagnoses=[],
                    contraindications=["Allergy to penicillin"]
                )
            )
        ]
    )
    res = ClinicalReasoningResponse(
        candidate_reasoning=[],
        reasoning_summary="Test clinical reasoning summary.",
        requires_doctor_review=True,
        red_flags_to_review=[]
    )
    
    service = TreatmentDraftService()
    draft = service.generate_draft(req, res)
    
    assert len(draft.considerations) == 1
    assert draft.status == "AI_GENERATED_DRAFT"
    assert draft.requires_doctor_review is True
    assert draft.doctor_approval_status == "PENDING"
    
    # Check for pneumonia high risk
    assert draft.considerations[0].contraindication_concern is True
    assert "High-risk condition" in draft.considerations[0].warnings[-1]


