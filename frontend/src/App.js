import React, { useMemo, useState } from "react";
import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost" ? "http://localhost:8000" : "/api");

const SUPPORTED_DRUGS = [
  { name: "CODEINE", label: "Codeine", gene: "CYP2D6" },
  { name: "CLOPIDOGREL", label: "Clopidogrel", gene: "CYP2C19" },
  { name: "WARFARIN", label: "Warfarin", gene: "CYP2C9" },
  { name: "SIMVASTATIN", label: "Simvastatin", gene: "SLCO1B1" },
  { name: "AZATHIOPRINE", label: "Azathioprine", gene: "TPMT" },
  { name: "FLUOROURACIL", label: "Fluorouracil", gene: "DPYD" },
  { name: "TRAMADOL", label: "Tramadol", gene: "CYP2D6" },
  { name: "OMEPRAZOLE", label: "Omeprazole", gene: "CYP2C19" },
  { name: "LOSARTAN", label: "Losartan", gene: "CYP2C9" },
  { name: "ATORVASTATIN", label: "Atorvastatin", gene: "SLCO1B1" },
  { name: "MERCAPTOPURINE", label: "Mercaptopurine", gene: "TPMT" },
  { name: "CAPECITABINE", label: "Capecitabine", gene: "DPYD" },
];

const SAMPLE_FILES = [
  { name: "safe_result.vcf", label: "Safe Case" },
  { name: "adjust_dosage_result.vcf", label: "Adjust Case" },
  { name: "toxic_result.vcf", label: "Toxic Case" },
];

const RISK_THEME = {
  Safe: { tone: "tone-safe", caption: "Proceed with standard dosing strategy" },
  "Adjust Dosage": { tone: "tone-adjust", caption: "Dose tuning and monitoring advised" },
  Toxic: { tone: "tone-toxic", caption: "High toxicity risk, evaluate alternatives" },
  Ineffective: { tone: "tone-ineffective", caption: "Likely subtherapeutic response" },
  default: { tone: "tone-default", caption: "Guidance pending detailed interpretation" },
};

const toPercent = (value) => `${Math.round((Number(value) || 0) * 100)}%`;

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [selectedDrug, setSelectedDrug] = useState("");
  const [patientId, setPatientId] = useState("PATIENT_001");
  const [useLlm, setUseLlm] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const selectedDrugInfo = useMemo(() => {
    return SUPPORTED_DRUGS.find((drug) => drug.name === selectedDrug) || null;
  }, [selectedDrug]);

  const riskVisual = useMemo(() => {
    const label = result?.risk_assessment?.risk_label;
    return RISK_THEME[label] || RISK_THEME.default;
  }, [result]);

  const profile = result?.pharmacogenomic_profile || {};
  const risk = result?.risk_assessment || {};
  const recommendation = result?.clinical_recommendation || {};
  const advice = result?.patient_advice || {};
  const discussionCard = result?.smart_patient_guidance?.doctor_discussion_card;
  const variants = Array.isArray(profile.detected_variants) ? profile.detected_variants : [];
  const doctorPoints = Array.isArray(advice.doctor_talking_points) ? advice.doctor_talking_points : [];

  const onFilePicked = (file) => {
    if (!file) return;
    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".vcf") && !lower.endsWith(".vcf.gz")) {
      setError("Please upload a .vcf or .vcf.gz file.");
      return;
    }
    setUploadedFile(file);
    setError(null);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      onFilePicked(event.dataTransfer.files[0]);
    }
  };

  const loadSample = async (filename) => {
    try {
      const response = await fetch(`/data/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${filename}`);
      }
      const blob = await response.blob();
      const file = new File([blob], filename, { type: "text/plain" });
      setUploadedFile(file);
      setError(null);
    } catch (err) {
      setError(err.message || "Failed to load sample file");
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedFile) {
      setError("Upload a VCF file first.");
      return;
    }
    if (!selectedDrug) {
      setError("Select a drug to analyze.");
      return;
    }

    setIsAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("vcf_file", uploadedFile, uploadedFile.name);
      formData.append("drug", selectedDrug);
      formData.append("patient_id", patientId || "PATIENT_001");
      formData.append("use_llm", String(useLlm));

      const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data?.risk_assessment?.risk_label === "Error") {
        setError(response.data?.clinical_recommendation?.action || "Analysis failed");
      }
      setResult(response.data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `pgx_${result.patient_id}_${result.drug}_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-shell">
      <div className="bg-shape shape-a" />
      <div className="bg-shape shape-b" />
      <div className="bg-shape shape-c" />
      <div className="bg-grid" />
      <div className="noise-layer" />

      <header className="hero">
        <div className="hero-main">
          <p className="eyebrow">Precision Pharmacogenomics Studio</p>
          <h1>PGx AI Analyzer</h1>
          <p className="hero-sub">
            Analyze VCF evidence against CPIC-aligned pharmacogenomic rules with a clinician-ready output.
          </p>
          <div className="hero-pills">
            <span>6 Genes</span>
            <span>18 Drugs</span>
            <span>VCF + AI Guidance</span>
          </div>
        </div>
        <div className="hero-side">
          <div className="status-chip">API Endpoint</div>
          <code>{API_BASE_URL}</code>
          <p>Use sample files or your own `.vcf` / `.vcf.gz` input.</p>
        </div>
      </header>

      {error && (
        <div className="alert">
          <strong>Issue:</strong> {error}
          <button className="btn-ghost" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      <section className="panel-grid">
        <article className="panel glass">
          <h2>1) Upload Genomic File</h2>
          <div
            className={`drop-zone ${dragActive ? "active" : ""}`}
            onDragEnter={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragOver={(e) => e.preventDefault()}
            onDragLeave={(e) => {
              e.preventDefault();
              setDragActive(false);
            }}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input").click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".vcf,.vcf.gz"
              onChange={(e) => onFilePicked(e.target.files?.[0])}
              hidden
            />
            <p className="drop-title">{uploadedFile ? uploadedFile.name : "Drop .vcf / .vcf.gz here"}</p>
            <p className="drop-sub">
              {uploadedFile
                ? `${Math.max(1, Math.round(uploadedFile.size / 1024))} KB loaded`
                : "or click to browse"}
            </p>
          </div>
          <div className="sample-row">
            {SAMPLE_FILES.map((sample) => (
              <button key={sample.name} className="btn-mini" onClick={() => loadSample(sample.name)}>
                {sample.label}
              </button>
            ))}
          </div>
        </article>

        <article className="panel glass">
          <h2>2) Configure Analysis</h2>
          <label>Patient ID</label>
          <input value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="PATIENT_001" />

          <label>Drug</label>
          <select value={selectedDrug} onChange={(e) => setSelectedDrug(e.target.value)}>
            <option value="">Select a drug</option>
            {SUPPORTED_DRUGS.map((drug) => (
              <option key={drug.name} value={drug.name}>
                {drug.label} ({drug.gene})
              </option>
            ))}
          </select>
          {selectedDrugInfo && (
            <p className="gene-chip">
              Primary gene: <strong>{selectedDrugInfo.gene}</strong>
            </p>
          )}

          <label className="toggle">
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
            <span>Use LLM enhancement</span>
          </label>

          <button
            className="btn-primary"
            disabled={isAnalyzing || !uploadedFile || !selectedDrug}
            onClick={handleAnalyze}
          >
            {isAnalyzing ? "Analyzing..." : "Run Analysis"}
          </button>
        </article>
      </section>

      {result && (
        <section className="results">
          <article className={`risk-hero ${riskVisual.tone}`}>
            <div>
              <p className="eyebrow">Risk Assessment</p>
              <h3>{risk.risk_label || "Unknown"}</h3>
              <p>{riskVisual.caption}</p>
            </div>
            <div className="kpi-strip">
              <div className="kpi-box">
                <span>{toPercent(risk.confidence_score)}</span>
                <small>confidence</small>
              </div>
              <div className="kpi-box">
                <span>{risk.severity || "unknown"}</span>
                <small>severity</small>
              </div>
            </div>
          </article>

          <div className="result-grid">
            <article className="panel glass">
              <h4>Pharmacogenomic Profile</h4>
              <p>
                <strong>Gene:</strong> {profile.primary_gene || "Unknown"}
              </p>
              <p>
                <strong>Diplotype:</strong> {profile.diplotype || "Unknown"}
              </p>
              <p>
                <strong>Phenotype:</strong> {profile.phenotype || "Unknown"}
              </p>
              <div className="chip-wrap">
                {variants.map((v, idx) => (
                  <span className="chip" key={`${v.rsid}-${idx}`}>
                    {v.rsid} ({v.genotype})
                  </span>
                ))}
              </div>
            </article>

            <article className="panel glass">
              <h4>Clinical Recommendation</h4>
              <p>
                <strong>Action:</strong> {recommendation.action || "Consult physician"}
              </p>
              <p>
                <strong>Alternative:</strong> {recommendation.alternative_suggestion || "Not required"}
              </p>
              <a href={recommendation.cpic_guideline_link} target="_blank" rel="noreferrer">
                Open CPIC Guideline
              </a>
              <button className="btn-secondary" onClick={handleDownload}>
                Download JSON
              </button>
            </article>
          </div>

          <article className="panel glass">
            <h4>Patient Advice</h4>
            <p>{advice.patient_friendly_summary || "No summary generated."}</p>
            <ul>
              {doctorPoints.map((point, idx) => (
                <li key={`${point}-${idx}`}>{point}</li>
              ))}
            </ul>
          </article>

          <article className="panel glass">
            <h4>AI Clinical Explanation</h4>
            <p>{result?.llm_generated_explanation?.summary || "No explanation generated."}</p>
            {discussionCard && (
              <pre>{discussionCard.card_content}</pre>
            )}
          </article>
        </section>
      )}
    </div>
  );
}

export default App;
