# AI Cover Letter Generator

A desktop application that generates tailored cover letters by combining a user’s resume and a job description using OpenAI’s GPT-4 model. The app features a simple GUI, supports multiple file formats, and exports cover letters in DOCX and PDF formats. It is packaged as a standalone macOS application for easy distribution.

---

## Features

- **AI-Powered Generation**  
  Uses GPT-4 to generate personalized, professional cover letters based on the user’s resume and a pasted job description.

- **Resume File Parsing**  
  Extracts text content from PDF, DOCX, and TXT resume files for use in prompts.

- **GUI Interface**  
  Built with Tkinter, allowing users to upload a resume, paste a job description, generate a cover letter, and export results with a few clicks.

- **PDF and DOCX Export**  
  Supports exporting generated cover letters as well-formatted PDF (ReportLab) or DOCX (python-docx) files.

- **Standalone macOS Application**  
  Bundled with PyInstaller, enabling users to launch the application without requiring a Python environment or command line.

---

## Tech Stack

- **Python**  
- **Tkinter** – GUI framework  
- **LangChain + OpenAI API** – LLM integration  
- **PyPDF2, python-docx** – Resume parsing  
- **ReportLab** – PDF export  
- **dotenv** – API key management  
- **PyInstaller** – Application bundling

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-cover-letter-generator.git
cd ai-cover-letter-generator

### 2. Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Create .env file in the project root
OPENAI_API_KEY=your_api_key_here

### 5. RUnning the App
python main.py
