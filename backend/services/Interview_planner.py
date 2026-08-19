# import json
# import re
# from urllib import response

# from services.gemini_client import model


# def create_interview_plan(resume_json_str):

#     prompt = f"""
#     You are an experienced technical recruiter.

#     Given this resume:

#     Parsed Resume Data:
#     {resume_json_str}
   

#     Create an interview plan.

#     Rules:
#     1. Pick top 2 strongest projects.
#     2. Remaining projects go to other_projects.
#     3. Pick top 2 important skills.
#     4. Keep total interview under 15 questions.


    

    
#     """

#     response = model.generate_content(
#         prompt,
#         generation_config={
#             "response_mime_type": "application/json",
#             "response_schema": {
#                 "type": "OBJECT",
#                 "properties": {
#                     "parsed": {
#                         "type": "OBJECT",
#                         "properties": {
#                             "skills": {"type": "ARRAY", "items": {"type": "STRING"}},
#                             "projects": {"type": "ARRAY", "items": {"type": "STRING"}}
#                         },
#                         "required": ["skills", "projects"]
#                     },
#                     "interview_plan": {
#                         "type": "OBJECT",
#                         "properties": {
#                             "role_focus": {"type": "STRING"},
#                             "top_projects": {
#                                 "type": "ARRAY",
#                                 "items": {
#                                     "type": "OBJECT",
#                                     "properties": {
#                                         "title": {"type": "STRING"},
#                                         "description": {"type": "STRING"}
#                                     }
#                                 }
#                             },
#                             "other_projects": {
#                                 "type": "ARRAY",
#                                 "items": {
#                                     "type": "OBJECT",
#                                     "properties": {
#                                         "title": {"type": "STRING"},
#                                         "description": {"type": "STRING"}
#                                     }
#                                 }
#                             },
#                             "top_skills_to_test": {"type": "ARRAY", "items": {"type": "STRING"}},
#                             "interview_questions": {
#                                 "type": "ARRAY",
#                                 "items": {
#                                     "type": "OBJECT",
#                                     "properties": {
#                                         "category": {"type": "STRING"},
#                                         "questions": {"type": "ARRAY", "items": {"type": "STRING"}}
#                                     }
#                                 }
#                             }
#                         },
#                         "required": ["role_focus", "interview_questions"]
#                     }
#                 },
#                 "required": ["parsed", "interview_plan"]
#             }
#         }
#     )

#     try:
#         return json.loads(response.text)
#     except Exception as e:
#         raise Exception(f"Planner JSON load error: {str(e)} | Raw Response: {response.text}")
import json
import re
from typing import List, Optional
from urllib import response

from pydantic import BaseModel
import ollama


# 📑 Sub-Schemas for Nested Structural Items
class ProjectDetail(BaseModel):
    title: str
    description: str

class QuestionCategory(BaseModel):
    category: str
    questions: List[str]

class ParsedData(BaseModel):
    skills: List[str]
    projects: List[str]

class InterviewPlanDetails(BaseModel):
    role_focus: str
    top_projects: Optional[List[ProjectDetail]] = []
    other_projects: Optional[List[ProjectDetail]] = []
    top_skills_to_test: Optional[List[str]] = []
    interview_questions: List[QuestionCategory]

# 🎯 Main Configuration Schema matching Gemini's exact hierarchy
class InterviewPlanSchema(BaseModel):
    parsed: ParsedData
    interview_plan: InterviewPlanDetails


def create_interview_plan(resume_json_str):

    prompt = f"""
    You are an experienced technical recruiter.

    Given this resume:

    Parsed Resume Data:
    {resume_json_str}
    

    Create an interview plan.

    Rules:
    1. Pick top 2 strongest projects.
    2. Remaining projects go to other_projects.
    3. Pick top 2 important skills.
    4. Keep total interview under 15 questions.
    """

    try:
        # 🚀 Ollama call with nested structural model json schema enforcement
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': prompt}],
            format=InterviewPlanSchema.model_json_schema() # Strict nested object structure enforcement
        )
        
        return json.loads(response['message']['content'])
        
    except Exception as e:
        # Aapka error handling module updated response validation ke sath
        raw_text = response['message']['content'] if 'response' in locals() and 'message' in response else "No response generated"
        raise Exception(f"Planner JSON load error: {str(e)} | Raw Response: {raw_text}")