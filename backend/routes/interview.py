from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from session_store import interview_sessions

# Gemini client se hamara banaya hua function import kar rahe hain
from services.gemini_client import generate_question ,evaluate_answer

router = APIRouter()

# Data validation ke liye Pydantic schemas
class StartInterviewRequest(BaseModel):
    session_id: str

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

# 1. Interview Shuru karne ka API Endpoint
@router.post("/start")
def start_interview(payload: StartInterviewRequest):
    session_id = payload.session_id
    
    # Check karo ki session memory mein hai ya nahi
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session nahi mila! Pehle resume upload karo.")
        
    session = interview_sessions[session_id]
    
    # Agar galti se page refresh hua aur history mein pehle se sawal hai, to wahi wapas de do
    if session["history"]:
        return {"question": session["history"][-1]["question"]}
        
    # Pehla question generate karne ke liye data nikalo
    skills = session["skills"]
    projects = session["projects"]
    
    # Gemini ko call karke pehla sawaal mangaao
    first_question = generate_question(skills, projects, history=[])
    
    # History mein sawal save karo
    session["history"].append({
        "question": first_question,
        "answer": None,

        "score": None,
        "feedback":None
    })
    
    return {"question": first_question}
    
def build_scorecard_response(history):
        scores_list = [turn["score"] for turn in history if turn.get("score") is not None]
        total_score = sum(scores_list)
        total_questions = len(scores_list)
        
        # Final % calculations
        max_score = total_questions * 10
        final_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        final_percentage = round(final_percentage, 2)
        
        # Performance Verdict
        verdict = "Excellent Performance" if final_percentage >= 80 else "Good Progress" if final_percentage >= 50 else "Needs Training"
        
        # Clean detailed breakdown of questions, answers, and feedback for the frontend scorecard view
        final_evaluation_data = [
            {
                "question": turn.get("question"),
                "answer": turn.get("answer"),
                "score": turn.get("score"),
                "feedback": turn.get("feedback", "No feedback available")
            }
            for turn in history if turn.get("question") is not None
        ]
        
        return {
            "message": "Interview completed successfully!",
            "end_of_interview": True,
            "question": None,
            "final_percentage_score": f"{final_percentage}%",
            "verdict": verdict,
            "total_questions_attempted": total_questions,
            "raw_scores": scores_list,
            "final_evaluation": final_evaluation_data
        }

# 2. Answer Submit karne aur Agla Sawal lene ka API Endpoint
@router.post("/submit-answer")
def submit_answer(payload: AnswerRequest):
    session_id = payload.session_id
    user_answer = payload.answer
    
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session valid nahi hai.")
        
    session = interview_sessions[session_id]
    history = session["history"]
    
    if not history:
        first_question = "Can you take a few minutes to introduce yourself, share your background in software engineering, and highlight any key projects that you've worked on recently?"
        history.append({
            "question": first_question,
            "answer": None,
            "score": None,
            "feedback": None
        })
        
    # Sabse aakhiri pucha gaye sawaal mein user ka answer save karo
    last_turn=history[-1]
    last_question=last_turn["question"]
    evaluation=evaluate_answer(last_question, user_answer)
    last_turn["answer"] = user_answer
    last_turn["score"] = evaluation.get("score", 1)
    last_turn["feedback"] = evaluation.get("feedback", "no feedback available")

    # MVP Rule: Agar 10 sawaal ho chuke hain, to interview khatam!
    if len(history) >= 10:
        return build_scorecard_response(history)
        
    # Agla sawaal generate karne ke liye history ke sath Gemini ko call karo
    next_question = generate_question(session["skills"], session["projects"], history)
       
    # Naye sawal ko history mein jod do
    history.append({
        "question": next_question,
        "answer": None,
        "score": None,
        "feedback": None
    })
    
    return {
        "question": next_question,
        "end_of_interview": False,
        "last_answer_evaluation": {
            "score": last_turn["score"],
            "feedback": last_turn["feedback"]
        }
    }