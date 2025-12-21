import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const sanitizeFileName = (value) =>
  value
    .replace(/[\\/?:%*|"<>]/g, "")
    .replace(/\s+/g, " ")
    .trim();

const deriveDefaultFileName = (text) => {
  const fallback = "Position at Company Cover Letter";
  if (!text) return fallback;

  const lines = text
    .split(/\r?\n/)
    .map((line) => line.replace(/^[-*•\s]+/, "").trim())
    .filter(Boolean);

  const findValue = (label) => {
    const regex = new RegExp(`^${label}\\s*[:\\-]\\s*(.+)$`, "i");
    for (const line of lines) {
      const match = line.match(regex);
      if (match) return match[1].trim();
    }
    return "";
  };

  const position =
    findValue("position") ||
    findValue("role") ||
    findValue("title") ||
    "";
  const company =
    findValue("company") ||
    findValue("employer") ||
    findValue("organization") ||
    "";

  if (position && company) {
    return sanitizeFileName(`${position} at ${company} Cover Letter`) || fallback;
  }

  for (const line of lines.slice(0, 3)) {
    const atMatch = line.match(/^(.+?)\s+at\s+(.+)$/i);
    if (atMatch) {
      return (
        sanitizeFileName(`${atMatch[1]} at ${atMatch[2]} Cover Letter`) ||
        fallback
      );
    }
  }

  if (position) {
    return sanitizeFileName(`${position} at Company Cover Letter`) || fallback;
  }
  if (company) {
    return sanitizeFileName(`Position at ${company} Cover Letter`) || fallback;
  }

  return fallback;
};

export default function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobText, setJobText] = useState("");
  const [coverLetter, setCoverLetter] = useState("");
  const [fileName, setFileName] = useState("Position at Company Cover Letter");
  const [fileNameTouched, setFileNameTouched] = useState(false);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setStatus("");
    setCoverLetter("");

    if (!resumeFile) {
      setStatus("Please upload a resume file.");
      return;
    }
    if (!jobText.trim()) {
      setStatus("Please paste a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("jobText", jobText);

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to generate cover letter");
      }

      const data = await res.json();
      setCoverLetter(data.coverLetter || "");
      if (!fileNameTouched) {
        setFileName(deriveDefaultFileName(jobText));
      }
      setStatus("Cover letter generated.");
    } catch (err) {
      setStatus(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (type) => {
    setStatus("");
    if (!coverLetter.trim()) {
      setStatus("Generate a cover letter first.");
      return;
    }

    const safeName = sanitizeFileName(
      fileName || "Position at Company Cover Letter"
    );

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/export/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coverLetter })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Failed to export ${type.toUpperCase()}`);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = type === "pdf" ? `${safeName}.pdf` : `${safeName}.docx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setStatus(`Downloaded ${type.toUpperCase()}.`);
    } catch (err) {
      setStatus(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <header>
          <h1>Cover Letter Generator</h1>
          <p>Upload a resume, paste a job description, and generate a tailored cover letter.</p>
        </header>

        <section className="field">
          <label htmlFor="resume">Resume (PDF, DOCX, TXT)</label>
          <input
            id="resume"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
          />
        </section>

        <section className="field">
          <label htmlFor="job">Job Description</label>
          <textarea
            id="job"
            placeholder="Paste the job description here..."
            rows={8}
            value={jobText}
            onChange={(e) => setJobText(e.target.value)}
          />
        </section>

        {coverLetter && (
          <section className="field">
            <label htmlFor="filename">Download File Name</label>
            <input
              id="filename"
              type="text"
              value={fileName}
              onChange={(e) => {
                setFileNameTouched(true);
                setFileName(e.target.value);
              }}
            />
          </section>
        )}

        <div className="actions">
          <button onClick={handleGenerate} disabled={loading}>
            {loading ? "Working..." : "Generate"}
          </button>
          <button onClick={() => downloadFile("pdf")} disabled={loading || !coverLetter}>
            Download PDF
          </button>
          <button onClick={() => downloadFile("docx")} disabled={loading || !coverLetter}>
            Download DOCX
          </button>
        </div>

        {status && <div className="status">{status}</div>}

        <section className="field">
          <label htmlFor="output">Cover Letter (Editable Preview)</label>
          <textarea
            id="output"
            rows={12}
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
          />
        </section>
      </div>
    </div>
  );
}
