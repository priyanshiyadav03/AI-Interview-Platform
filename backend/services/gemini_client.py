import json
import os
from click import prompt
from dotenv import load_dotenv
#import google.generativeai as genai
import ollama

load_dotenv()



def generate_question(skills: list, projects: list, history: list) -> str:
    """
    Interview Planner ke diye gaye strongest_topics par deep-dive (max 3) karta hai.
    Baaki standard skills/projects se sirf 1-2 normal questions pooch kar pure profile ko cover karta hai.
    """
    # 1. History ko text mein convert karna
    formatted_history = ""
    for turn in history:
        formatted_history += f"Interviewer: {turn['question']}\n"
        if turn['answer']:
            formatted_history += f"Candidate: {turn['answer']}\n"
        formatted_history += "---\n"
    if len(history) >= 2:
        last_two_answers = [str(turn.get('answer', '')).lower().strip() for turn in history[-2:]]
        if all(ans in ["", "i don't know", "dont know", "skip", "no idea", "na"] or len(ans) < 5 for ans in last_two_answers):
            return "TERMINATE"
       
    if not history:
        # Pehla turn: Ek solid starting question
        prompt = f"""
        You are an expert technical interviewer conducting a structured Software Engineering interview.
        Candidate's strongest Skills: {", ".join(skills)}
        Candidate's Key Projects: {", ".join(projects)}
        
        Task:
        - Ask exactly ONE clear introductory question. 
        - Start smoothly: Ask the candidate to briefly introduce themselves and give an overview of their journey with their core skills or main project.
        - Output ONLY the question text directly. No hello/welcome greetings.
        """
    else:
        # Baaki turns: Pichle answer par deep dive / cross-questioning
        last_turn = history[-1]
        prompt = f"""
        
        You are an elite Technical Interviewer. You must maintain a balance between deep-diving into the candidate's strongest areas and touching upon all other listed skills/projects to ensure full profile coverage.
        
        Candidate's strongest Skills: {", ".join(skills)}
        Candidate's Key Projects: {", ".join(projects)}
        
        Full Conversation History:
        {formatted_history}
        
        Most Recent Turn to Focus On:
        Last Question Asked: {last_turn['question']}
        Candidate's Answer: {last_turn['answer'] if last_turn['answer'] else 'No answer provided.'}
        
        
        Task:
        - Critically analyze the candidate's last answer. 
        - If the answer is vague or incomplete, ask a sharp follow-up or cross-question about the technical details they missed or mentioned.
        - DYNAMIC INTERVIEW RULES:
        1. NO REPETITION: Do NOT repeat any question, concept, or core topic that has already been discussed in the Full Conversation History.
        2. TOPIC ROTATION (STRICT CEILING): Do NOT spend more than 2-3 questions total on any single project (like RAG) or single skill domain. Once that limit is hit, you MUST force a pivot to an untouched project or skill from the provided lists.
        3. SCAN THE ENTIRE PROFILE: Look at the full lists: Skills=[{", ".join(skills)}] and Projects=[{", ".join(projects)}]. Identify which skills or projects have NOT been tested yet in the history, and pick one for the next question.
        4. WIDE TECH STACK COVERAGE: Ensure you touch upon backend engineering fundamentals (e.g., Database optimization, indexing, caching, asynchronous workers, concurrency, API design, or system architecture) if listed in their skills, rather than sticking only to AI/LLM topics.
        5. TRANSITION PHRASE: You MUST use a natural conversational transition when moving to a new domain (e.g., "Shifting gears from AI, let's talk about your experience with...", "Looking at another key skill in your profile, how do you handle...").
        6. Output exactly ONE single question. No meta-commentary, no intro/outro text.
        """
         
    try:
        # 3. Aapke banaye hue global model instance ko use kiya
        # 🚀 Naya Ollama Code:
        response = ollama.generate(model='llama3.1:8b', prompt=prompt)
        response_text= response['response']
        return response_text.strip()
        
    except Exception as e:
        print(f"ollama Error: {str(e)}")
        return "Can you explain the difference between synchronous and asynchronous programming?"
    
def evaluate_answer(question: str, answer: str) -> dict:
    """
    User ke single answer ko critical check karke score (1-10) aur feedback return karta hai.
    """
    # Edge case check: Agar answer khali ya bohot chota hai
    if not answer or len(answer.strip()) < 5:
        return {
            "score": 1,
            "feedback": "The answer was either blank or too short. A proper technical explanation was expected."
        }

    prompt = f"""
    You are an expert technical interviewer and evaluator. 
    Critically evaluate the candidate's answer for the specific question asked.

    Question: {question}
    Candidate's Answer: {answer}

    Evaluation Criteria:
    - Technical Accuracy (Is the concept correct?)
    - Completeness (Did they answer all parts of the question?)
    - Clarity (Is the explanation professional and easy to understand?)

    Return the response strictly in this JSON format:
    {{
        "score": <integer_between_1_and_10>,
        "feedback": "<clear_constructive_feedback_under_3_sentences>"
    }}
    """

    try:
        # response = model.generate_content(
        #     prompt,
        #     generation_config={
        #         "response_mime_type": "application/json",
        #         "response_schema": {
        #             "type": "OBJECT",
        #             "properties": {
        #                 "score": {"type": "INTEGER"},
        #                 "feedback": {"type": "STRING"}
        #             },
        #             "required": ["score", "feedback"]
        #         }
        #     }
        # )
        response = ollama.chat(
            model="llama3.1:8b",
            messages=[{'role': 'user', 'content': prompt}],
            format='json' # 👈 Bas model ko bol diya ki string JSON format mein dena
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"ollama Evaluation Error: {str(e)}")
        # API fail hone par safe fallback code
        return {
            "score": 5,
            "feedback": "Evaluation temporary unavailable due to server error, but response captured."
        }