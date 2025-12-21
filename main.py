from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils import extract_text
from docx import Document
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from tkinter import filedialog, messagebox
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import os
import sys
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(base_path, ".env")
load_dotenv(env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

def choose_resume():
    path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[("Documents", "*.pdf *.docx *.txt"), ("All files", "*.*")]
    )
    if path:
        resume_path_var.set(path)
        try:
            txt = extract_text(path)
            resume_preview.delete("1.0", tk.END)
            resume_preview.insert(tk.END, txt[:2000])
            status_var.set("Resume loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read resume:\n{e}")

def generate_cover_letter():
    resume_path = resume_path_var.get().strip()
    if not resume_path:
        messagebox.showwarning("Missing resume", "Please choose a resume file.")
        return

    try:
        resume_text = extract_text(resume_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read resume:\n{e}")
        return

    job_text = job_desc_text.get("1.0", tk.END).strip()
    if not job_text:
        messagebox.showwarning("Missing job description", "Please paste a job description.")
        return

    prompt = f"""
    You are an expert career writer. Write a professional and tailored cover letter 
    based on the following resume and job description. 

    The cover letter should:
    - Be 3–4 paragraphs (one page)
    - Address the hiring manager by "Hiring Manager"
    - Highlight relevant skills and achievements
    - Match tone and keywords of the job description
    - Not simply restate the contents of the resume; summarize if necessary
    - Not restate any numbers already mentioned in the resume
    - Provide the full name, city of residence, email, and phone number of the applicant on seperate lines in the header
    - Not include the date
    --- Resume ---
    {resume_text}

    --- Job Description ---
    {job_text}
    """

    try:
        status_var.set("Generating...")
        root.update_idletasks()
        response = llm.invoke(prompt)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, response.content)
        status_var.set("Cover letter generated")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate cover letter:\n{e}")
        status_var.set("Error")

def save_cover_letter():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Nothing to save", "Please generate a cover letter first.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".docx",
        filetypes=[("Word Document", "*.docx")],
        title="Save Cover Letter As"
    )
    if file_path:
        doc = Document()
        for para in text.split("\n\n"):
            doc.add_paragraph(para)
        doc.save(file_path)
        messagebox.showinfo("Saved", f"Cover letter saved:\n{file_path}")
        status_var.set("Saved cover letter")

def save_as_pdf():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("Nothing to save", "Please generate a cover letter first.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save Cover Letter As PDF"
    )
    if not file_path:
        return

    try:
        # assume first 4 lines of the text are header
        lines = text.splitlines()
        header_lines = []
        body_lines = []

        # stop header at "Dear Hiring Manager,"
        for i, line in enumerate(lines):
            if line.strip() == "Dear Hiring Manager,":
                header_lines = lines[:i]
                body_lines = lines[i:]
                break
        else:
            # If no dear hiring manager found, default to first 4 lines as header
            header_lines = lines[:4]
            body_lines = lines[4:]

        doc = SimpleDocTemplate(
            file_path,
            pagesize=LETTER,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )

        styles = getSampleStyleSheet()
        story = []

        for hline in header_lines:
            story.append(Paragraph(hline.strip(), styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Add body paragraphs (split by blank lines)
        paragraphs = "\n".join(body_lines).split("\n\n")
        for para in paragraphs:
            story.append(Paragraph(para.strip(), styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        messagebox.showinfo("Saved", f"Cover letter saved as PDF:\n{file_path}")
        status_var.set("Saved PDF cover letter")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save PDF:\n{e}")

# ----- GUI -----

root = tk.Tk()
root.title("Cover Letter Generator")
root.minsize(800, 600)

resume_frame = tk.Frame(root)
resume_frame.pack(fill="x", padx=10, pady=5)

tk.Label(resume_frame, text="Resume File:").pack(side="left")
resume_path_var = tk.StringVar()
tk.Entry(resume_frame, textvariable=resume_path_var, width=50).pack(side="left", padx=5)
tk.Button(resume_frame, text="Choose...", command=choose_resume).pack(side="left")

resume_preview = ScrolledText(root, height=5)
resume_preview.pack(fill="x", padx=10, pady=5)
resume_preview.insert(tk.END, "Resume preview will appear here after choosing a file.")

tk.Label(root, text="Paste Job Description Below:").pack(anchor="w", padx=10)
job_desc_text = ScrolledText(root, height=10)
job_desc_text.pack(fill="both", expand=False, padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=5)

tk.Button(button_frame, text="Generate Cover Letter", command=generate_cover_letter).pack(side="left")
tk.Button(button_frame, text="Save as .docx", command=save_cover_letter).pack(side="left", padx=5)
tk.Button(button_frame, text="Save as .pdf", command=save_as_pdf).pack(side="left", padx=5)

tk.Label(root, text="Generated Cover Letter:").pack(anchor="w", padx=10)
output_box = ScrolledText(root, height=15)
output_box.pack(fill="both", expand=True, padx=10, pady=5)

status_var = tk.StringVar(value="Idle")
status_bar = tk.Label(root, textvariable=status_var, anchor="w", relief="sunken")
status_bar.pack(fill="x", side="bottom")

root.mainloop()
