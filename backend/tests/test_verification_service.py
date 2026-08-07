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



def _minimal_reasoning(**overrides):
    data = {
        "candidate_reasoning": [],
        "reasoning_summary": "Verification test reasoning.",
        "requires_doctor_review": True,
    }
    data.update(overrides)
    return ClinicalReasoningResponse(**data)


def test_verification_uses_clinical_rule_alerts():
    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(
            alerts=["Check oxygen saturation and respiratory status"],
            status="evaluated",
        ),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
            )
        ],
    )

    plan = VerificationService().generate_verification_plan(
        req,
        _minimal_reasoning(),
    )

    rule_steps = [
        step for step in plan.suggested_steps
        if step.candidate_disease == "General Clinical Safety"
    ]

    assert len(rule_steps) == 1
    assert rule_steps[0].priority == "high"
    assert rule_steps[0].is_red_flag is True
    assert (
        rule_steps[0].supporting_context
        == "Check oxygen saturation and respiratory status"
    )


def test_verification_includes_physical_examination_guidance():
    knowledge = DiseaseKnowledge(
        disease_id="pneumonia",
        name="Pneumonia",
        description="Test knowledge record.",
        knowledge_version="test-v1",
        physical_examination=["Auscultate lung fields"],
    )

    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
                knowledge=knowledge,
            )
        ],
    )

    plan = VerificationService().generate_verification_plan(
        req,
        _minimal_reasoning(),
    )

    assert any(
        step.category == "physical_examination"
        and step.supporting_context == "Auscultate lung fields"
        for step in plan.suggested_steps
    )


def test_verification_handles_missing_knowledge():
    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
                knowledge=None,
            )
        ],
    )

    plan = VerificationService().generate_verification_plan(
        req,
        _minimal_reasoning(),
    )

    assert plan.suggested_steps == []
    assert plan.requires_doctor_review is True


def test_verification_missing_information_is_sorted_and_deduplicated():
    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
            )
        ],
    )

    reasoning = ClinicalReasoningResponse(
        candidate_reasoning=[
            CandidateReasoning(
                rank=1,
                disease="Pneumonia",
                supporting_findings=[],
                conflicting_findings=[],
                missing_information=["oxygen saturation", "CBC"],
                rationale="Synthetic test rationale.",
            )
        ],
        important_uncertainties=["CBC", "symptom duration"],
        next_information_needed=["chest imaging"],
        reasoning_summary="Synthetic test reasoning.",
        requires_doctor_review=True,
    )

    plan = VerificationService().generate_verification_plan(req, reasoning)

    assert plan.missing_information_summary == sorted(
        {
            "oxygen saturation",
            "CBC",
            "symptom duration",
            "chest imaging",
        }
    )


def test_ai_highlighted_concern_is_not_deterministic_red_flag():
    req = ClinicalReasoningRequest(
        patient_context={},
        rules=ClinicalRuleResult(),
        differential=[
            ReasoningDifferentialItem(
                rank=1,
                disease="Pneumonia",
                probability=0.8,
                confidence="High",
            )
        ],
    )

    reasoning = _minimal_reasoning(
        red_flags_to_review=["Possible clinical deterioration"],
    )

    plan = VerificationService().generate_verification_plan(req, reasoning)

    ai_step = next(
        step for step in plan.suggested_steps
        if step.candidate_disease == "AI Highlighted"
    )

    assert ai_step.priority == "high"
    assert ai_step.is_red_flag is False
    assert ai_step.requires_doctor_review is True

def test_verification_api():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    payload = {
        "reasoning_request": {
            "patient_context": {},
            "rules": {
                "alerts": [
                    "Check oxygen saturation and respiratory status"
                ],
                "status": "evaluated",
            },
            "differential": [
                {
                    "rank": 1,
                    "disease": "Pneumonia",
                    "probability": 0.8,
                    "confidence": "High",
                    "knowledge": None,
                }
            ],
        },
        "reasoning_response": {
            "candidate_reasoning": [],
            "important_uncertainties": [],
            "red_flags_to_review": [],
            "next_information_needed": [],
            "reasoning_summary": "Synthetic verification API test.",
            "limitations": [],
            "requires_doctor_review": True,
        },
    }

    response = client.post(
        "/api/v1/clinical/verification",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["requires_doctor_review"] is True
    assert len(data["suggested_steps"]) == 1

    step = data["suggested_steps"][0]

    assert step["candidate_disease"] == "General Clinical Safety"
    assert step["priority"] == "high"
    assert step["is_red_flag"] is True
    assert (
        step["supporting_context"]
        == "Check oxygen saturation and respiratory status"
    )
