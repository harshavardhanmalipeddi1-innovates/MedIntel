export type Prediction = {
  rank: number;
  disease: string;
  probability: number;
  confidence: string;
};

export type CandidateReasoning = {
  rank: number;
  disease: string;
  supporting_findings: string[];
  conflicting_findings: string[];
  missing_information: string[];
  rationale: string;
};

export type WorkflowResponse = {
  success: boolean;
  predictions: Prediction[];
  reasoning: {
    candidate_reasoning: CandidateReasoning[];
    important_uncertainties: string[];
    red_flags_to_review: string[];
    next_information_needed: string[];
    reasoning_summary: string;
    limitations: string[];
    requires_doctor_review: boolean;
  };
  verification: {
    suggested_steps: string[];
    missing_information_summary: string[];
    requires_doctor_review: boolean;
  };
  treatment_draft: {
    general_cautions: string[];
    status: string;
    requires_doctor_review: boolean;
    doctor_approval_status: string;
  };
  workflow_status: string;
  workflow_id: string;
  requires_doctor_review: boolean;
  doctor_approval_status: string;
};

const syntheticPayload = {
  patient_context: {
    AGE: 45,
    SEX_MALE_CODE: 1,
    NONINITIAL_EVIDENCE_COUNT: 0,
    QUESTIONNAIRE_COMPLETION_FRACTION: 1.0,
    INITIAL_EVIDENCE_ONLY: 1,
    CONSULTATION_STAGE_CODE: 0,
    evidence_tokens: ["E_100"],
    age: 45,
    sex: "M",
    symptoms: ["synthetic test case"],
    symptom_duration: "3 days",
    test_case: true,
  },
};

export async function runVerifiedSyntheticWorkflow(): Promise<WorkflowResponse> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 420_000);

  try {
    const response = await fetch("/api/v1/clinical/workflow", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(syntheticPayload),
      signal: controller.signal,
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`Workflow request failed (${response.status}): ${detail}`);
    }

    return (await response.json()) as WorkflowResponse;
  } finally {
    window.clearTimeout(timeout);
  }
}
