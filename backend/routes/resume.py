from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from session_store import interview_sessions

# Aapki banayi hui services ko import kar rahe hain
from services.resume_parser import  parse_resume  # Maan lete hain is function ka naam yeh hai
from services.Interview_planner import create_interview_plan    # Maan lete hain is function ka naam yeh hai

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    # 1. Check karo ki file sirf PDF ho
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sirf PDF files hi allowed hain!")
        
    try:
        # File ka data read karo
        file_content = await file.read()
        
        # 2. PDF Se Text extract karo (Aapki service use karke)
        # Note: Agar aapka function file path leta hai ya bytes, us hisab se pass karein
        extracted_text = parse_resume(file_content) 
        
        # 3. Interview Planner se Skills aur Projects nikalo (Aapki service)
        # Yeh function aapko ek dictionary return karega, e.g., {"skills": [...], "projects": [...]}
        extracted_data = create_interview_plan(extracted_text)
        print("\n=== [DEBUG] INTERVIEW PLANNER KA RAW RESPONSE SEEDHE GEMINI SE ===")
        print(extracted_data)
        print("==================================================================\n")
        parsed_part=extracted_data.get("parsed", {})
        skills = parsed_part.get("skills") or parsed_part.get("Skills") or []
        
        raw_projects = parsed_part.get("projects") or parsed_part.get("Projects") or []
        
        # Projects agar direct list of strings hai ya dictionaries, dono handle honge
        projects = []
        if isinstance(raw_projects, list):
            for p in raw_projects:
                if isinstance(p, dict) and p.values():
                    # Dictionary ki pehli key ki value uthao (Title/name agnostic)
                    first_val = list(p.values())[0]
                    if first_val: projects.append(str(first_val))
                elif isinstance(p, str):
                    projects.append(p)
        
        # 4. Unique Session ID banayein aur central memory mein save karein
        session_id = str(uuid.uuid4())
        
        interview_sessions[session_id] = {
            "skills": skills,
            "projects": projects,
            "history": [],
            "current_topic_index": 0
        }
        
        return {
            "message": "Resume processed and session created successfully!",
            "session_id": session_id,
            "extracted_data": {
                "skills": skills,
                "projects": projects
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")