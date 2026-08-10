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
  } | null;
  verification: {
    suggested_steps: unknown[];
    missing_information_summary: string[];
    requires_doctor_review: boolean;
  } | null;
  treatment_draft: {
    considerations?: unknown[];
    general_cautions: string[];
    status: string;
    requires_doctor_review: boolean;
    doctor_approval_status: string;
  } | null;
  workflow_status: string;
  workflow_id: string;
  requires_doctor_review: boolean;
  doctor_approval_status: string;
};

export type AssessmentOption = {
  value: string;
  label: string;
};

export type AssessmentQuestion = {
  code: string;
  question: string;
  data_type: string;
  answer_kind: string;
  is_antecedent: boolean;
  initial_evidence_allowed: boolean;
  default_value: unknown;
  options: AssessmentOption[];
  scale_min: number | null;
  scale_max: number | null;
};

export type AssessmentQuestionnaire = {
  version: string;
  question_count: number;
  initial_evidence_count: number;
  initial_evidence_codes: string[];
  questions: AssessmentQuestion[];
  source: Record<string, unknown>;
};

export type AssessmentAnswer = {
  code: string;
  value: unknown;
};

export type AssessmentPrepareRequest = {
  age: number;
  sex: "M" | "F";
  initial_evidence: string;
  answers: AssessmentAnswer[];
};

export type AssessmentPrepareResponse = {
  patient_context: Record<string, unknown>;
  initial_evidence: string;
  positive_evidence_tokens: string[];
  answered_question_codes: string[];
  eligible_question_codes: string[];
  answered_question_count: number;
  eligible_question_count: number;
  questionnaire_completion_fraction: number;
};

function decodePossiblyWrappedJson<T>(text: string): T {
  let value: unknown = text.trim();

  for (let depth = 0; depth < 3 && typeof value === "string"; depth += 1) {
    const candidate = value.trim();

    if (!candidate) {
      throw new Error("The backend returned an empty JSON response.");
    }

    try {
      value = JSON.parse(candidate);
    } catch {
      throw new Error("The backend returned an invalid JSON response.");
    }
  }

  if (typeof value === "string") {
    throw new Error("The backend response remained JSON-string wrapped.");
  }

  return value as T;
}

async function requestJson<T>(
  url: string,
  init: RequestInit = {},
  timeoutMs = 30_000,
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");

  try {
    const response = await fetch(url, {
      ...init,
      headers,
      signal: controller.signal,
    });

    const body = await response.text();

    if (!response.ok) {
      throw new Error(
        `Request failed (${response.status}): ${body || response.statusText}`,
      );
    }

    return decodePossiblyWrappedJson<T>(body);
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function getAssessmentQuestionnaire(): Promise<AssessmentQuestionnaire> {
  return requestJson<AssessmentQuestionnaire>(
    "/api/v1/clinical/assessment/questionnaire",
    {
      method: "GET",
    },
    30_000,
  );
}

export async function prepareAssessment(
  request: AssessmentPrepareRequest,
): Promise<AssessmentPrepareResponse> {
  return requestJson<AssessmentPrepareResponse>(
    "/api/v1/clinical/assessment/prepare",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
    60_000,
  );
}

export async function runClinicalWorkflow(
  patientContext: Record<string, unknown>,
): Promise<WorkflowResponse> {
  return requestJson<WorkflowResponse>(
    "/api/v1/clinical/workflow",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        patient_context: patientContext,
      }),
    },
    720_000,
  );
}

/*
 * Retain the engineering-demo button, but route it through the same
 * AssessmentService contract used by the clinician-facing flow.
 *
 * The browser no longer constructs AGE / evidence_tokens / consultation
 * stage fields itself.
 */
export async function runVerifiedSyntheticWorkflow(): Promise<WorkflowResponse> {
  const questionnaire = await getAssessmentQuestionnaire();

  const initialEvidence = questionnaire.initial_evidence_codes[0];

  if (!initialEvidence) {
    throw new Error(
      "The live assessment questionnaire contains no valid initial evidence.",
    );
  }

  const prepared = await prepareAssessment({
    age: 45,
    sex: "M",
    initial_evidence: initialEvidence,
    answers: [],
  });

  return runClinicalWorkflow(prepared.patient_context);
}
