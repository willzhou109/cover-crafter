# CoverCraft

Web app that generates tailored cover letters from a resume file and a job description. Backend uses FastAPI + LangChain; frontend uses React (Vite). The web app has accelerated the application process for 20+ users and 1000+ applications in one semester.

<img width="1710" height="876" alt="image" src="https://github.com/user-attachments/assets/c5c2dc2d-eb0b-48bb-9f6b-fba98d4f6309" />
<img width="1710" height="876" alt="image" src="https://github.com/user-attachments/assets/9f5d477e-9a4f-4e11-bb66-058ea734f3c4" />
<img width="1710" height="1062" alt="image" src="https://github.com/user-attachments/assets/9ebeafb1-27cc-439a-a25d-356efde426e7" />



## Features
- Upload resume (PDF/DOCX/TXT)
- Paste job description
- Generate cover letter via backend API
- Edit the generated draft
- Download as PDF or DOCX
- File size limit (5MB) and text truncation to keep prompts small

## Tech Stack
- Frontend: React 18, Vite 5
- Backend: Python 3.11, FastAPI
- LLM: LangChain + OpenAI
- Parsing: PyPDF2, python-docx
- Exports: reportlab (PDF), python-docx (DOCX)
- Tooling: npm, pip, uvicorn

## Local Development

### Backend (FastAPI)
```bash
cd /Users/williamzhou/projects/Cover_Letter_Project/backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create `backend/.env`:
```
OPENAI_API_KEY=your_key_here
```

Run:
```bash
uvicorn app:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd /Users/williamzhou/projects/Cover_Letter_Project/frontend
npm install
npm run dev
```

Open:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## API Endpoints
- `POST /api/generate` (multipart/form-data)
  - fields: `resume` (file), `jobText` (string)
  - response: `{ "coverLetter": "..." }`
- `POST /api/export/pdf` (JSON)
  - body: `{ "coverLetter": "..." }`
- `POST /api/export/docx` (JSON)
  - body: `{ "coverLetter": "..." }`

## Environment Variables
Backend:
- `OPENAI_API_KEY` (required)
- `FRONTEND_ORIGINS` (optional, comma-separated)

Frontend:
- `VITE_API_BASE_URL` (optional, default `http://localhost:8000`)
