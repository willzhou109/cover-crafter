import { useState } from 'react'

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [resumeFile, setResumeFile] = useState(null)
  const [jobText, setJobText] = useState('')
  const [coverLetter, setCoverLetter] = useState('')
  const [fileTitle, setFileTitle] = useState('cover_letter')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    setError('')
    setStatus('')

    if (!resumeFile) {
      setError('Please upload a resume file.')
      return
    }
    if (!jobText.trim()) {
      setError('Please paste a job description.')
      return
    }

    const formData = new FormData()
    formData.append('resume', resumeFile)
    formData.append('jobText', jobText)

    try {
      setLoading(true)
      setStatus('Generating cover letter...')
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        body: formData,
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to generate cover letter')
      }
      setCoverLetter(data.coverLetter || '')
      setStatus('Cover letter generated.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadFile = async (type) => {
    setError('')
    setStatus('')

    try {
      setLoading(true)
      setStatus(`Preparing ${type.toUpperCase()}...`)

      const res = await fetch(`${API_BASE}/api/export/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coverLetter }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Failed to export ${type.toUpperCase()}`)
      }

      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const safeTitle = (fileTitle || 'cover_letter')
        .trim()
        .replace(/[^a-zA-Z0-9-_ ]+/g, '')
        .replace(/\s+/g, '_')
        .slice(0, 80) || 'cover_letter'
      a.download = `${safeTitle}.${type}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      setStatus(`${type.toUpperCase()} downloaded.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>CoverCrafter</h1>
      <div className="subtitle">
        Upload a resume, paste a job description, and generate a tailored cover letter.
      </div>

      <label htmlFor="resume">Resume (PDF/DOCX/TXT)</label>
      <input
        id="resume"
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => setResumeFile(e.target.files[0] || null)}
      />

      <label htmlFor="job">Job Description</label>
      <textarea
        id="job"
        value={jobText}
        onChange={(e) => setJobText(e.target.value)}
        placeholder="Paste the job description here..."
      />

      <label htmlFor="title">Download File Title</label>
      <input
        id="title"
        type="text"
        value={fileTitle}
        onChange={(e) => setFileTitle(e.target.value)}
        placeholder="cover_letter"
      />

      <div className="button-row">
        <button onClick={handleGenerate} disabled={loading}>
          Generate
        </button>
        <button
          className="secondary"
          onClick={() => downloadFile('pdf')}
          disabled={!coverLetter || loading}
        >
          Download PDF
        </button>
      </div>

      <label htmlFor="output">Cover Letter (Editable)</label>
      <textarea
        id="output"
        className="output"
        value={coverLetter}
        onChange={(e) => setCoverLetter(e.target.value)}
        placeholder="Your cover letter will appear here..."
      />

      {status && <div className="status">{status}</div>}
      {error && <div className="status error">{error}</div>}
    </div>
  )
}
