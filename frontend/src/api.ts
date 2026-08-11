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

export async function runClinicalWorkflow(
  patientContext: Record<string, unknown>,
): Promise<WorkflowResponse> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 420_000);

  try {
    const response = await fetch("/api/v1/clinical/workflow", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ patient_context: patientContext }),
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

export type PatientRecord = {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  medical_history_summary?: string;
  created_at: string;
  updated_at: string;
};

export type EncounterRecord = {
  id: string;
  patient_id: string;
  doctor_id: string;
  symptoms: string[];
  history?: string;
  vitals: Record<string, unknown>;
  physical_examination?: string;
  created_at: string;
  updated_at: string;
  ai_prediction_results?: Record<string, unknown>;
  ai_reasoning_results?: Record<string, unknown>;
  ai_verification_results?: Record<string, unknown>;
  ai_treatment_draft?: Record<string, unknown>;
  doctor_confirmed_outcome?: Record<string, unknown>;
};

export async function createPatient(
  patient: Omit<PatientRecord, "id" | "created_at" | "updated_at">,
): Promise<PatientRecord> {
  const response = await fetch("/api/v1/clinical/patients", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(patient),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Create patient failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as PatientRecord;
}

export async function getPatient(
  patientId: string,
): Promise<PatientRecord> {
  const response = await fetch(`/api/v1/clinical/patients/${patientId}`);

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Get patient failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as PatientRecord;
}

export async function getPatients(): Promise<PatientRecord[]> {
  const response = await fetch("/api/v1/clinical/patients");

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Get patients failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as PatientRecord[];
}

export async function updatePatient(
  patientId: string,
  update: Partial<Omit<PatientRecord, "id" | "created_at" | "updated_at">>,
): Promise<PatientRecord> {
  const response = await fetch(`/api/v1/clinical/patients/${patientId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(update),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Update patient failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as PatientRecord;
}

export async function createEncounter(
  encounter: Omit<EncounterRecord, "id" | "created_at" | "updated_at">,
): Promise<EncounterRecord> {
  const response = await fetch("/api/v1/clinical/encounters", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(encounter),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Create encounter failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as EncounterRecord;
}

export async function getEncounter(encounterId: string): Promise<EncounterRecord> {
  const response = await fetch(`/api/v1/clinical/encounters/${encounterId}`);

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Get encounter failed (${response.status}): ${detail}`);
  }

  return (await response.json()) as EncounterRecord;
}
