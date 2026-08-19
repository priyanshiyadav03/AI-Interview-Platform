import json
import re
from typing import List
from urllib import response

from pydantic import BaseModel
#import google.generativeai as genai
import ollama
from dotenv import load_dotenv
import os

load_dotenv()



def parse_resume(text):

    prompt = f"""
    You are a resume parser.

    Extract:
    1. Skills
    2. Projects
    3. Education
    4. Experience

    Return ONLY valid JSON.

    Resume:
    {text}
    """
    class ResumeSchema(BaseModel):
        skills: List[str]
        projects: List[str]
        education: List[str]
        experience: List[str]
    try:
        response = ollama.chat(
                model='qwen2.5:3b',
                messages=[{'role': 'user', 'content': prompt}],
                format=ResumeSchema.model_json_schema() # 👈 Yeh line model ko strict keys dene par majboor karegi
            )
        
        return json.loads(response['message']['content'])
    except Exception as e:
        raise Exception(f"JSON convert karne me dikkat aayi: {str(e)}")