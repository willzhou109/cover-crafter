import io
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from utils import extract_text_from_upload

load_dotenv()

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 20000

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


def _truncate(text: str, limit: int = MAX_TEXT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def _build_prompt(resume_text: str, job_text: str) -> str:
    return f"""
You are an expert career writer.

Your task is to write a concise, professional, and tailored cover letter using the resume and job description below.

Before writing:
1. Identify the 4–6 most important skills or qualifications from the job description.
2. Select the most relevant experiences from the resume that demonstrate those skills.
3. Focus on alignment and impact rather than listing responsibilities.

Writing requirements:
- Length: 3–4 paragraphs (one page maximum)
- Begin the letter with "Dear Hiring Manager"
- Tone: professional, confident, and clear
- Match keywords and priorities from the job description naturally
- Summarize resume content; do NOT restate it verbatim
- Do NOT repeat any numbers or metrics already present in the resume
- Avoid generic phrases (e.g., “hard-working,” “fast learner”)
- Do not include the date

Header formatting (must appear at the top in this exact order):
Applicant information (each on its own line):
Full Name  
City of Residence (if available)
Email Address (if available)
Phone Number (if available)

Then include a separator line consisting of three hyphens:
---

Company information (each on its own line):
Company Name  
Company Address (if available)

Letter structure:
- Paragraph 1: Express interest in the role and briefly explain why you are a strong fit
- Paragraph 2: Highlight the most relevant technical skills and experiences that match the role
- Paragraph 3 (optional 4th): Emphasize alignment with the company/team and conclude professionally

Closing format:
- End the letter with the word "Sincerely,"
- Then include the applicant’s full name on the next line

Output rules:
- Output only the final cover letter text
- No bullet points
- No explanations or analysis

--- Resume ---
{resume_text}

--- Job Description ---
{job_text}
""".strip()


def _require_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY on server")
    return api_key


class ExportRequest(BaseModel):
    coverLetter: str


def _split_header_and_body(text: str):
    lines = text.splitlines()
    header_lines = []
    body_start_idx = 0

    for i, line in enumerate(lines):
        if line.strip() == "Dear Hiring Manager,":
            header_lines = lines[:i]
            body_start_idx = i
            break
        if line.strip() == "":
            header_lines = lines[:i]
            body_start_idx = i + 1
            break
    else:
        header_lines = []
        body_start_idx = 0

    body_text = "\n".join(lines[body_start_idx:]).strip()
    body_paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    header_lines = [h.strip() for h in header_lines if h.strip()]
    return header_lines, body_paragraphs


def _normalize_sincerely_spacing(paragraphs):
    normalized = []
    for para in paragraphs:
        if para.strip() == "Sincerely,":
            normalized.append(para.strip())
            normalized.append("")
        else:
            normalized.append(para)
    return normalized


@app.post("/api/generate")
async def generate_cover_letter(
    resume: UploadFile = File(...),
    jobText: str = Form(...),
):
    if not resume:
        raise HTTPException(status_code=400, detail="Missing resume file")

    job_text = jobText.strip()
    if not job_text:
        raise HTTPException(status_code=400, detail="Missing job description")

    content = await resume.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Resume file too large (max 5MB)")

    try:
        resume_text = extract_text_from_upload(resume.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to extract resume text: {exc}") from exc

    resume_text = _truncate(resume_text)
    job_text = _truncate(job_text)

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty or unreadable")

    _require_api_key()

    prompt = _build_prompt(resume_text, job_text)

    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        response = llm.invoke(prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {exc}") from exc

    return JSONResponse({"coverLetter": response.content.strip()})


@app.post("/api/export/pdf")
async def export_pdf(payload: ExportRequest):
    text = (payload.coverLetter or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing cover letter text")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()
    story = []
    header_lines, body_paragraphs = _split_header_and_body(text)
    body_paragraphs = _normalize_sincerely_spacing(body_paragraphs)

    for line in header_lines:
        story.append(Paragraph(line, styles["Normal"]))

    if header_lines:
        story.append(Spacer(1, 0.3 * inch))

    for para in body_paragraphs:
        if not para:
            story.append(Spacer(1, 0.2 * inch))
            continue
        pdf_para = para.replace("\n", "<br/>")
        story.append(Paragraph(pdf_para, styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=cover_letter.pdf"
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
