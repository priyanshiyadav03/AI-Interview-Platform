import os
import sys

# Ensure UTF-8 output encoding for Windows stdout logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, Form,UploadFile, File,HTTPException
from services.email_Services import send_interview_email
import fitz 
import uuid
from ats_engine import calculate_ats_score
from services.resume_parser import parse_resume
from services.Interview_planner import create_interview_plan
from session_store import interview_sessions
from routes import resume, interview
app = FastAPI()
# 1. Resume waale router ko register kiya
#app.include_router(resume.router, prefix="/api")

# 2. Interview waale router ko register kiya
app.include_router(interview.router, prefix="/api")


@app.get("/")
def home():
    return {"message": "AI Interview Platform Backend Running"}
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...),
    candidate_name: str = Form(...),   # 👈 Form se Name extract ho gaya
    candidate_email: str = Form(...),
):
    jd_path = "jd.txt"
    if not os.path.exists(jd_path):
        raise HTTPException(
            
            status_code=404, 
            detail="jd.txt file project root directory mein nahi mili! Pehle file banayein."
        )
    with open(jd_path, "r", encoding="utf-8") as f:
        job_description = f.read()
    pdf_bytes = await file.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    parsed_data = parse_resume(text)
    interview_plan = create_interview_plan(parsed_data)
    parsed_part = interview_plan.get("parsed", {})
    skills = parsed_part.get("skills", [])
    projects = parsed_part.get("projects", [])
    
    # Asli plan content
    plan_details = interview_plan.get("interview_plan", {})
    # 6. Session state maintain karne ke liye central memory me save kiya
    print("[INFO] Running LangGraph ATS Engine on local model...")
    try:
        ats_results = calculate_ats_score(text, job_description)
        print("[SUCCESS] ATS Analysis Completed Successfully!")
    except Exception as e:
        print(f"[ERROR] ATS Engine Error: {e}")
        # Agar local LLM respond na kare ya crash ho, toh backup ke liye 0 scores set kar rahe hain
        ats_results = {
            "skill_score": 0, "experience_score": 0, "qualification_score": 0,
            "achievement_score": 0, "technology_and_tools_score": 0, 
            "internship_score": 0, "soft_skill_score": 0, "has_strong_project": False
        }
    # 6. Session state maintain karne ke liye central memory me save kiya
    session_id = str(uuid.uuid4())
    interview_sessions[session_id] = {
            "skills": skills,
            "projects": projects,
            "interview_plan": plan_details,
            "history": [],
            "current_topic_index": 0,
            "ats_scores": ats_results
            
        }  
    skill_score = int(float(ats_results.get('skill_score') or 0))
    tech_score = int(float(ats_results.get('technology_and_tools_score') or 0))
    exp_score = int(float(ats_results.get('experience_score') or 0))
    soft_score = int(float(ats_results.get('soft_skill_score') or 0))
    
    # Frontend wala same formula backend par lagaya decision lene ke liye
    final_score = (skill_score * 0.40) + (tech_score * 0.30) + (soft_score * 0.15) + (exp_score * 0.15)
    final_score = round(final_score, 1)

    if final_score >= 70.0:
        interview_link = f"http://localhost:8501/?session_id={session_id}"
        print(f"[EMAIL] Sending shortlist email to {candidate_email} (Score: {final_score}%)...")
        send_interview_email(
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            interview_link=interview_link
        )
    else:
        print(f"[WARNING] Candidate {candidate_name} not shortlisted. Score: {final_score}%")
    # ================================================================  
    return {
        
        
        "interview_plan": interview_plan,
        "ats_scores": ats_results,
        "message": "Resume processed and session created successfully!",
        "session_id": session_id,
        "extracted_data": {
        "skills": skills,
        "projects": projects
            }
        }
