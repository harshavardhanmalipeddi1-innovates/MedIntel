import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ClipboardPlus,
  FileText,
  LayoutDashboard,
  Menu,
  Moon,
  Settings,
  ShieldCheck,
  Stethoscope,
  Sun,
  Users,
  X,
} from "lucide-react";
import {
  BrowserRouter,
  NavLink,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import "./styles.css";
import {
  createPatient,
  getPatients,
  runClinicalWorkflow,
  runVerifiedSyntheticWorkflow,
  type PatientRecord,
  type WorkflowResponse,
} from "./api";

type PageMeta = {
  title: string;
  eyebrow: string;
  description: string;
};

const pages: Record<string, PageMeta> = {
  dashboard: {
    title: "Clinical Dashboard",
    eyebrow: "MedIntel Workspace",
    description:
      "A clinician-controlled workspace for structured assessment and AI-assisted decision support.",
  },
  patients: {
    title: "Patients",
    eyebrow: "Patient Workspace",
    description:
      "Patient search, selection, history, and longitudinal records will be implemented in this phase.",
  },
  assessment: {
    title: "New Clinical Assessment",
    eyebrow: "Structured Intake",
    description:
      "Capture demographics, symptoms, history, vitals, examination findings, and model-compatible evidence.",
  },
  decision: {
    title: "AI Decision Support",
    eyebrow: "Clinician Review",
    description:
      "Review authoritative XGBoost differentials and constrained MedGemma reasoning without allowing ranking drift.",
  },
  reports: {
    title: "Reports",
    eyebrow: "Clinical Documentation",
    description:
      "Structured report drafting and export will be added after the assessment and review workflow is connected.",
  },
  settings: {
    title: "Settings",
    eyebrow: "Workspace Configuration",
    description:
      "Configure clinician preferences, integrations, and future authentication controls.",
  },
};

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/patients", label: "Patients", icon: Users },
  { to: "/assessment", label: "New Assessment", icon: ClipboardPlus },
  { to: "/decision-support", label: "AI Decision Support", icon: Stethoscope },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [dark, setDark] = useState(true);

  const shellClass = useMemo(
    () => `app-shell ${dark ? "theme-dark" : "theme-light"}`,
    [dark],
  );

  return (
    <div className={shellClass}>
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-mark">
            <Activity size={23} strokeWidth={2.2} />
          </div>
          <div>
            <strong>MedIntel</strong>
            <span>Clinical Decision Support</span>
          </div>
          <button
            className="icon-button sidebar-close"
            type="button"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <nav className="primary-nav" aria-label="Primary navigation">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-safety">
          <ShieldCheck size={18} />
          <div>
            <strong>Clinician authority</strong>
            <span>AI output requires doctor review.</span>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          aria-label="Close navigation"
          type="button"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-button mobile-menu"
            type="button"
            aria-label="Open navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={21} />
          </button>

          <div className="topbar-status">
            <span className="status-dot" />
            <span>Phase 5 - Frontend ready</span>
          </div>

          <div className="topbar-actions">
            <button
              className="icon-button"
              type="button"
              aria-label={dark ? "Use light theme" : "Use dark theme"}
              onClick={() => setDark((value) => !value)}
            >
              {dark ? <Sun size={19} /> : <Moon size={19} />}
            </button>
            <div className="doctor-chip" aria-label="Clinician profile placeholder">
              <div className="doctor-avatar">DR</div>
              <div>
                <strong>Doctor workspace</strong>
                <span>Authentication pending</span>
              </div>
            </div>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/patients" element={<PatientsPage />} />
          <Route path="/assessment" element={<AssessmentPage />} />
          <Route path="/decision-support" element={<DecisionSupportPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function PageHeader({ meta }: { meta: PageMeta }) {
  return (
    <section className="page-header">
      <div>
        <span className="eyebrow">{meta.eyebrow}</span>
        <h1>{meta.title}</h1>
        <p>{meta.description}</p>
      </div>
      <div className="safety-pill">
        <ShieldCheck size={17} />
        Decision support only
      </div>
    </section>
  );
}

function Dashboard() {
  const [recentPatients, setRecentPatients] = useState<PatientRecord[]>([]);

  useEffect(() => {
    getPatients()
      .then((patients) => setRecentPatients(patients.slice(0, 3)))
      .catch(() => setRecentPatients([]));
  }, []);

  return (
    <div className="page">
      <PageHeader meta={pages.dashboard} />

      <section className="hero-panel">
        <div>
          <span className="hero-kicker">Doctor-first workflow</span>
          <h2>Move from structured assessment to reviewed AI support.</h2>
          <p>
            Phase 5 & 6 connect the existing FastAPI, XGBoost, and local MedGemma
            workflow to a clinician-facing interface with real-time validation and reporting.
          </p>
          <div className="hero-actions">
            <NavLink className="button button-primary" to="/assessment">
              <ClipboardPlus size={18} />
              Start assessment
            </NavLink>
            <NavLink className="button button-secondary" to="/decision-support">
              <Stethoscope size={18} />
              Review AI workspace
            </NavLink>
          </div>
        </div>
        <div className="hero-guardrail">
          <ShieldCheck size={30} />
          <strong>Clinical guardrail</strong>
          <p>
            XGBoost remains authoritative for candidates, ranks, and
            probabilities. MedGemma cannot alter them.
          </p>
        </div>
      </section>

      <section className="metric-grid" aria-label="Implementation status">
        <StatusCard
          label="Backend API"
          value="Ready"
          note="FastAPI workflow available"
        />
        <StatusCard
          label="XGBoost"
          value="Authoritative"
          note="Ranked differential engine"
        />
        <StatusCard
          label="MedGemma"
          value="Local"
          note="Constrained reasoning via llama.cpp"
        />
        <StatusCard
          label="Frontend"
          value="Complete"
          note="Doctor-facing workflow implemented"
        />
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Recent Activity</span>
              <h3>Recently active patients</h3>
            </div>
          </div>
          <div className="workflow-list">
            {recentPatients.length > 0 ? (
              recentPatients.map((patient) => (
                <div className="workflow-item" key={patient.id}>
                  <span>ID: {patient.id.slice(0, 4)}</span>
                  <div>
                    <strong>{patient.first_name} {patient.last_name}</strong>
                    <p>DOB: {patient.date_of_birth}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-inline" style={{ marginTop: "1rem" }}>
                <p>No recent patients found.</p>
              </div>
            )}
          </div>
          <div style={{ marginTop: "1rem" }}>
             <NavLink to="/patients" className="button button-secondary" style={{ width: "100%", justifyContent: "center" }}>
                View all patients
             </NavLink>
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">Current scope</span>
          <h3>What Phase 6 Adds</h3>
          <ul className="check-list">
            <li>Dashboard recent activity feed</li>
            <li>Real-time form validation</li>
            <li>Structured report generation UI</li>
            <li>Error and empty state polish</li>
            <li>Printable clinical reports</li>
          </ul>
        </div>
      </section>
    </div>
  );
}

function StatusCard({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <article className="status-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{note}</p>
    </article>
  );
}

function PatientsPage() {
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [patientsError, setPatientsError] = useState<string | null>(null);
  const [patientList, setPatientList] = useState<PatientRecord[]>([]);

  useEffect(() => {
    async function loadPatients() {
      setPatientsLoading(true);
      setPatientsError(null);

      try {
        const list = await getPatients();
        setPatientList(list);
      } catch (error) {
        setPatientsError(
          error instanceof Error
            ? error.message
            : "Failed to load patient list.",
        );
      } finally {
        setPatientsLoading(false);
      }
    }

    loadPatients();
  }, []);

  return (
    <div className="page">
      <PageHeader meta={pages.patients} />
      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Patient roster</span>
            <h3>Active clinical cases</h3>
          </div>
        </div>

        {patientsLoading ? (
          <div className="empty-inline">
            <Activity size={24} />
            <div>
              <strong>Loading patients...</strong>
              <p>Fetching active cases from the backend.</p>
            </div>
          </div>
        ) : patientsError ? (
          <div className="clinical-error">
            <strong>Unable to load patients</strong>
            <p>{patientsError}</p>
          </div>
        ) : patientList.length === 0 ? (
          <div className="empty-inline">
            <Users size={24} />
            <div>
              <strong>No patients available yet</strong>
              <p>Submit the first assessment to create a patient record.</p>
            </div>
          </div>
        ) : (
          <div className="patient-grid">
            {patientList.map((patient) => (
              <article className="patient-card" key={patient.id}>
                <strong>
                  {patient.first_name} {patient.last_name}
                </strong>
                <span>Age {patient.date_of_birth}</span>
                <p>{patient.medical_history_summary ?? "No history provided."}</p>
                <span className="status-pill">Patient ID {patient.id}</span>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function AssessmentPage() {
  const [patientFirstName, setPatientFirstName] = useState("Aisha");
  const [patientLastName, setPatientLastName] = useState("Patel");
  const [patientDOB, setPatientDOB] = useState("1984-06-09");
  const [patientGender, setPatientGender] = useState<"M" | "F">("F");
  const [age, setAge] = useState(45);
  const [sex, setSex] = useState<"M" | "F">("M");
  const [symptoms, setSymptoms] = useState("cough, fever");
  const [symptomDuration, setSymptomDuration] = useState("3 days");
  const [evidenceTokens, setEvidenceTokens] = useState("E_100");
  const [result, setResult] = useState<WorkflowResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patientCreated, setPatientCreated] = useState(false);
  const [patientId, setPatientId] = useState<string | null>(null);
  const [patientList, setPatientList] = useState<PatientRecord[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(false);
  const [patientsError, setPatientsError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  async function submitAssessment() {
    setRunning(true);
    setError(null);
    setFormErrors({});

    const newErrors: Record<string, string> = {};
    if (!patientFirstName.trim()) newErrors.firstName = "First name is required.";
    if (!patientLastName.trim()) newErrors.lastName = "Last name is required.";
    if (age <= 0 || age > 120) newErrors.age = "Age must be between 1 and 120.";
    if (!symptoms.trim() || symptoms.trim().length < 3) newErrors.symptoms = "Please provide valid symptoms.";

    if (Object.keys(newErrors).length > 0) {
      setFormErrors(newErrors);
      setRunning(false);
      return;
    }

    const patientPayload = {
      first_name: patientFirstName,
      last_name: patientLastName,
      date_of_birth: patientDOB,
      gender: patientGender,
      medical_history_summary: "No prior summary.",
    };

    try {
      let targetPatientId = patientId;

      if (!patientCreated) {
        const patient = await createPatient(patientPayload);
        setPatientId(patient.id);
        setPatientCreated(true);
        targetPatientId = patient.id;
      }

      if (!targetPatientId) {
        throw new Error("Unable to resolve patient ID before submitting assessment.");
      }

      const patientContext = {
        AGE: age,
        SEX_MALE_CODE: sex === "M" ? 1 : 0,
        NONINITIAL_EVIDENCE_COUNT: 0,
        QUESTIONNAIRE_COMPLETION_FRACTION: 1.0,
        INITIAL_EVIDENCE_ONLY: 1,
        CONSULTATION_STAGE_CODE: 0,
        patient_id: targetPatientId,
        age,
        sex,
        symptoms: symptoms
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        symptom_duration: symptomDuration,
        evidence_tokens: evidenceTokens
          .split(",")
          .map((token) => token.trim())
          .filter(Boolean),
      };

      const response = await runClinicalWorkflow(patientContext);
      setResult(response);
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "The workflow request failed.";
      setError(message);
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    async function loadPatients() {
      setPatientsLoading(true);
      setPatientsError(null);

      try {
        const list = await getPatients();
        setPatientList(list);
      } catch (error) {
        setPatientsError(
          error instanceof Error
            ? error.message
            : "Failed to load patients.",
        );
      } finally {
        setPatientsLoading(false);
      }
    }

    loadPatients();
  }, []);

  return (
    <div className="page">
      <PageHeader meta={pages.assessment} />

      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Clinical intake</span>
            <h3>Submit structured patient context</h3>
          </div>
        </div>

        <div className="form-grid">
          <label>
            First name
            <input
              type="text"
              className={formErrors.firstName ? "input-error" : ""}
              value={patientFirstName}
              onChange={(event) => setPatientFirstName(event.target.value)}
            />
            {formErrors.firstName && <span className="error-message">{formErrors.firstName}</span>}
          </label>

          <label>
            Last name
            <input
              type="text"
              className={formErrors.lastName ? "input-error" : ""}
              value={patientLastName}
              onChange={(event) => setPatientLastName(event.target.value)}
            />
            {formErrors.lastName && <span className="error-message">{formErrors.lastName}</span>}
          </label>

          <label>
            Date of birth
            <input
              type="date"
              value={patientDOB}
              onChange={(event) => setPatientDOB(event.target.value)}
            />
          </label>

          <label>
            Biological sex
            <select
              value={patientGender}
              onChange={(event) =>
                setPatientGender(event.target.value === "M" ? "M" : "F")
              }
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </label>

          <label>
            Age
            <input
              type="number"
              min={0}
              className={formErrors.age ? "input-error" : ""}
              value={age}
              onChange={(event) => setAge(Number(event.target.value))}
            />
            {formErrors.age && <span className="error-message">{formErrors.age}</span>}
          </label>

          <label>
            Biological sex
            <select
              value={sex}
              onChange={(event) =>
                setSex(event.target.value === "M" ? "M" : "F")
              }
            >
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </label>

          <label>
            Symptom duration
            <input
              type="text"
              value={symptomDuration}
              onChange={(event) => setSymptomDuration(event.target.value)}
            />
          </label>

          <label className="full-width">
            Symptoms
            <textarea
              className={formErrors.symptoms ? "input-error" : ""}
              value={symptoms}
              onChange={(event) => setSymptoms(event.target.value)}
              rows={3}
            />
            {formErrors.symptoms && <span className="error-message">{formErrors.symptoms}</span>}
          </label>

          <label className="full-width">
            Evidence tokens
            <input
              type="text"
              value={evidenceTokens}
              onChange={(event) => setEvidenceTokens(event.target.value)}
            />
            <small>
              Use comma-separated evidence tokens such as E_100, E_101.
            </small>
          </label>
        </div>

        <button
          className="button button-primary"
          type="button"
          disabled={running}
          onClick={submitAssessment}
        >
          <Activity size={18} className={running ? "spin" : ""} />
          {running ? "Running workflow..." : "Submit assessment"}
        </button>

        {error && (
          <section className="clinical-error">
            <strong>Assessment failed</strong>
            <p>{error}</p>
          </section>
        )}
      </section>

      {result && (
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Workflow result</span>
              <h3>Clinical decision support output</h3>
            </div>
          </div>

          <div className="prediction-list">
            {result.predictions.map((prediction) => (
              <article className="prediction-row" key={prediction.rank}>
                <div className="rank-badge">{prediction.rank}</div>
                <div className="prediction-main">
                  <strong>{prediction.disease}</strong>
                  <span>{prediction.confidence} confidence</span>
                </div>
                <div className="probability-block">
                  <strong>
                    {(prediction.probability * 100).toFixed(1)}%
                  </strong>
                  <span>model probability</span>
                </div>
              </article>
            ))}
          </div>

          <div className="reasoning-stack">
            <div className="reasoning-card">
              <div className="reasoning-card-heading">
                <span>Summary</span>
                <strong>Clinical reasoning</strong>
              </div>
              <p>{result.reasoning.reasoning_summary}</p>
            </div>
          </div>

          <div className="workflow-meta">
            <div>
              <span>Workflow</span>
              <strong>{result.workflow_status}</strong>
            </div>
            <div>
              <span>Doctor review</span>
              <strong>
                {result.requires_doctor_review ? "Required" : "Not required"}
              </strong>
            </div>
            <div>
              <span>Approval</span>
              <strong>{result.doctor_approval_status}</strong>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function ReportsPage() {
  const [patients, setPatients] = useState<PatientRecord[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);

  useEffect(() => {
    getPatients().then(setPatients).catch(console.error);
  }, []);

  const patient = patients.find((p) => p.id === selectedPatient);

  return (
    <div className="page">
      <PageHeader meta={pages.reports} />
      
      <div className="no-print">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Report Generation</span>
              <h3>Select a patient to generate report</h3>
            </div>
          </div>
          <div className="form-grid">
            <label className="full-width">
              Select Patient
              <select 
                value={selectedPatient || ""} 
                onChange={(e) => setSelectedPatient(e.target.value)}
              >
                <option value="">-- Choose a patient --</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.first_name} {p.last_name} (ID: {p.id.slice(0, 8)})
                  </option>
                ))}
              </select>
            </label>
          </div>
          {patient && (
            <button 
              className="button button-primary"
              onClick={() => window.print()}
              style={{ marginTop: "1rem" }}
            >
              <FileText size={18} /> Print / Save as PDF
            </button>
          )}
        </section>
      </div>

      {patient && (
        <section className="panel print-only report-container">
          <div className="report-header">
            <h2>MedIntel Clinical Report</h2>
            <p><strong>Date:</strong> {new Date().toLocaleDateString()}</p>
          </div>
          
          <div className="report-section">
            <h3>Patient Information</h3>
            <p><strong>Name:</strong> {patient.first_name} {patient.last_name}</p>
            <p><strong>DOB:</strong> {patient.date_of_birth} | <strong>Gender:</strong> {patient.gender}</p>
            <p><strong>Patient ID:</strong> {patient.id}</p>
          </div>

          <div className="report-section">
            <h3>Clinical Assessment</h3>
            <p><strong>Medical History:</strong> {patient.medical_history_summary || "None provided"}</p>
            <p><em>(Assessment context would appear here if loaded from an encounter API endpoint)</em></p>
          </div>

          <div className="report-section">
            <h3>Decision Support Overview</h3>
            <p><strong>Status:</strong> Awaiting specific encounter details.</p>
            <div className="clinical-warning" style={{ marginTop: "1rem" }}>
              <strong>Doctor review required</strong>
              <p>This report contains AI-generated decision support information that requires clinician review.</p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="page">
      <PageHeader meta={pages.settings} />
      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Workspace settings</span>
            <h3>Runtime configuration overview</h3>
          </div>
        </div>
        <div className="settings-grid">
          <article className="settings-card">
            <strong>Data flow</strong>
            <p>
              Clinical input flows into the backend workflow API, XGBoost ranks
              candidates, and local MedGemma adds constrained reasoning.
            </p>
          </article>
          <article className="settings-card">
            <strong>Review policy</strong>
            <p>
              All AI output remains clinician-reviewed. Doctor approval is
              explicitly required and shown in the workflow response.
            </p>
          </article>
          <article className="settings-card">
            <strong>Local AI provider</strong>
            <p>
              MedGemma reasoning currently runs through a local llama.cpp server
              and is optional depending on runtime configuration.
            </p>
          </article>
        </div>
      </section>
    </div>
  );
}

function DecisionSupportPage() {
  const [result, setResult] = useState<WorkflowResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runDemo() {
    setRunning(true);
    setError(null);

    try {
      const response = await runVerifiedSyntheticWorkflow();
      setResult(response);
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "The workflow request failed.";
      setError(message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="page">
      <PageHeader meta={pages.decision} />

      <section className="demo-banner">
        <div>
          <span className="eyebrow">Verified engineering path</span>
          <h3>Run the real Docker model workflow from the browser</h3>
          <p>
            This uses the same synthetic engineering payload already verified
            against FastAPI, XGBoost, local MedGemma, safety validation, and
            doctor-review workflow. E_100 is a technical test token and is not
            assigned a clinical meaning.
          </p>
        </div>
        <button
          className="button button-primary workflow-run-button"
          type="button"
          disabled={running}
          onClick={runDemo}
        >
          <Activity size={18} className={running ? "spin" : ""} />
          {running ? "Running model..." : "Run verified model workflow"}
        </button>
      </section>

      {running && (
        <section className="model-progress">
          <Activity size={20} className="spin" />
          <div>
            <strong>XGBoost + local MedGemma are running</strong>
            <p>
              CPU MedGemma inference can take several minutes. Keep this page
              open while the constrained reasoning response is generated.
            </p>
          </div>
        </section>
      )}

      {error && (
        <section className="clinical-error">
          <strong>Workflow request failed</strong>
          <p>{error}</p>
        </section>
      )}

      <section className="decision-grid">
        <div className="panel">
          <span className="eyebrow">Authoritative ranking</span>
          <h3>XGBoost differential candidates</h3>

          {!result ? (
            <div className="empty-inline">
              <Stethoscope size={24} />
              <div>
                <strong>No workflow result yet</strong>
                <p>
                  Run the verified engineering workflow to display the real
                  XGBoost candidates returned by the backend.
                </p>
              </div>
            </div>
          ) : (
            <div className="prediction-list">
              {result.predictions.map((prediction) => (
                <article className="prediction-row" key={prediction.rank}>
                  <div className="rank-badge">{prediction.rank}</div>
                  <div className="prediction-main">
                    <strong>{prediction.disease}</strong>
                    <span>{prediction.confidence} confidence</span>
                  </div>
                  <div className="probability-block">
                    <strong>
                      {(prediction.probability * 100).toFixed(1)}%
                    </strong>
                    <span>model probability</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>

        <div className="panel">
          <span className="eyebrow">Constrained reasoning</span>
          <h3>MedGemma clinical context</h3>

          {!result ? (
            <div className="empty-inline">
              <ShieldCheck size={24} />
              <div>
                <strong>Safety boundary active</strong>
                <p>
                  MedGemma cannot add, remove, re-rank, or change candidate
                  probabilities.
                </p>
              </div>
            </div>
          ) : (
            <div className="reasoning-stack">
              {result.reasoning.candidate_reasoning.map((candidate) => (
                <article className="reasoning-card" key={candidate.rank}>
                  <div className="reasoning-card-heading">
                    <span>Rank {candidate.rank}</span>
                    <strong>{candidate.disease}</strong>
                  </div>
                  <p>{candidate.rationale}</p>
                </article>
              ))}

              <div className="summary-card">
                <span>Reasoning summary</span>
                <p>{result.reasoning.reasoning_summary}</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {result && (
        <section className="workflow-meta">
          <div>
            <span>Workflow</span>
            <strong>{result.workflow_status}</strong>
          </div>
          <div>
            <span>Doctor review</span>
            <strong>
              {result.requires_doctor_review ? "Required" : "Not required"}
            </strong>
          </div>
          <div>
            <span>Approval</span>
            <strong>{result.doctor_approval_status}</strong>
          </div>
          <div>
            <span>Workflow ID</span>
            <strong className="workflow-id">{result.workflow_id}</strong>
          </div>
        </section>
      )}

      <section className="clinical-warning">
        <ShieldCheck size={21} />
        <div>
          <strong>Doctor review required</strong>
          <p>
            MedIntel is clinical decision support only. It does not autonomously
            diagnose, prescribe, order medication, or determine disposition.
          </p>
        </div>
      </section>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
