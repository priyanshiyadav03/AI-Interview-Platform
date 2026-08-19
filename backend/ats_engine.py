# ats_engine.py
import re
from typing import TypedDict, Optional
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, END, START
import json

# 1. Initialize Local LLM (Phi-3)
llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.7,
)

# 2. Pydantic Schemas for Structured Output
class GetAtsSchema(BaseModel):
    skill_score: Optional[float] = Field(default=0.0, description="calculate skill_score (0 to 100)")
    experience_score: Optional[float] = Field(default=0.0, description="calculate experience_score (0 to 100)")
    qualification_score: Optional[float] = Field(default=0.0, description="calculate qualification_score (0 to 100)")
    achievement_score: Optional[float] = Field(default=0.0, description="calculate achievement_score (0 to 100)")
    technology_and_tools_score: Optional[float] = Field(default=0.0, description="calculate technology_and_tools_score (0 to 100)")
    internship_score: Optional[float] = Field(default=0.0, description="calculate internship_score (0 to 100)")
    soft_skill_score: Optional[float] = Field(default=0.0, description="calculate soft_skill_score (0 to 100)")
    has_strong_project: Optional[bool] = Field(default=False, description="determine if the candidate has strong project score")

class GetDescSchema(BaseModel):
    skill: Optional[list[str]] = Field(default=[], description="skills required for the job")
    qualification: Optional[list[str]] = Field(default=[], description="Qualification required for the job")
    soft_skill: Optional[list[str]] = Field(default=[], description="soft_skill required for the job")
    experience_year: Optional[str] = Field(default="0", description="Year of experience required for the job")
    project_experience: Optional[list[str]] = Field(default=[], description="project experience required for some projects")
    other_info: Optional[str] = Field(default="", description="Any important other info")
    technology_and_tools: Optional[list[str]] = Field(default=[], description="Add all the required tools and technology")
def extract_clean_json(raw_text: str) -> str:
    """LLM ke kachre text me se sirf valid JSON structure nikalne ke liye regex block"""
    # Remove single-line comments like // not applicable because they break json parsing
    clean_text = re.sub(r'//.*', '', raw_text)
    
    # Extract everything inside the outermost curly braces {}
    match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return clean_text.strip()
# 3. Parsers & LCEL Chains
parser_desc = PydanticOutputParser(pydantic_object=GetDescSchema)
parser_ats = PydanticOutputParser(pydantic_object=GetAtsSchema)

chain_desc = llm | parser_desc
chain_ats = llm | parser_ats

# 4. LangGraph State Definition
class AtsState(TypedDict):
    desc: str
    resume: str
    skill: list[str]
    qualification: list[str]
    soft_skill: list[str]
    technology_and_tools: list[str]
    experience_year: str
    project_experience: list[str]
    other_info: str
    skill_score: float
    experience_score: float
    qualification_score: float
    achievement_score: float
    technology_and_tools_score: float
    internship_score: float
    soft_skill_score: float
    has_strong_project: bool

# 5. Nodes (Processing Functions)
def summarise_desc(state: AtsState):
    job_desc = state["desc"]
    prompt = """
    You are an ATS Job Description Requirement Extractor.
    Analyze the recruiter job description and extract information STRICTLY according to the schema.
    
    JOB DESCRIPTION:
    """+ str(job_desc) +"""
    
    Convert all text to lowercase. Return ONLY structured output.
    
    CRITICAL INSTRUCTION FOR ARRAYS/LISTS:
    The fields 'skill', 'qualification', 'soft_skill', and 'project_experience' MUST be simple arrays of PLAIN STRINGS (e.g., ["python", "communication"]). 
    DO NOT wrap these strings inside any internal object or dictionary like [{"value": "python"}] or [{"type": "education"}]. 
    If a field has no data, return an empty list [].
    Strictly follow this plain string format, otherwise the output parser will crash.
   
    {parser_desc.get_format_instructions()}"""
   
    raw_response = llm.invoke(prompt).content
    try:
        clean_json_str = extract_clean_json(raw_response)
        parsed_dict = json.loads(clean_json_str)
        # Validate through Pydantic model safely
        result = GetDescSchema(**parsed_dict)
    except Exception:
        result = GetDescSchema()
    return {
        "skill": result.skill, "qualification": result.qualification,
        "soft_skill": result.soft_skill, "technology_and_tools": result.technology_and_tools,
        "experience_year": result.experience_year, "project_experience": result.project_experience,
        "other_info": result.other_info
    }

def matching(state: AtsState):
    mresume = state["resume"]
    # 
    jd_skills_str = ", ".join(state.get("skill", [])) if isinstance(state.get("skill"), list) else str(state.get("skill", ""))
    jd_tech_str = ", ".join(state.get("technology_and_tools", [])) if isinstance(state.get("technology_and_tools"), list) else str(state.get("technology_and_tools", ""))
    jd_exp_str = str(state.get("experience_year", "0"))

    prompt = """
    You are an Expert ATS Scoring Engine. Compare the Job Description requirements with the candidate Resume.
    
    RESUME: 
    """+ str(mresume) +"""
    
    JOB DESCRIPTION REQUIREMENTS TO MATCH:
    JD SKILLS:"""+ jd_skills_str +"""
    JD TECH: """+ jd_tech_str +"""
    JD EXP YEARS: """+ jd_exp_str +"""
    
    Give individual scores from 0 to 100 strictly based on explicit facts found in the resume. Do not hallucinate.
    
    
   
    """+ parser_ats.get_format_instructions()
    result = chain_ats.invoke(prompt)
    return {
        "skill_score": result.skill_score, "experience_score": result.experience_score,
        "qualification_score": result.qualification_score, "achievement_score": result.achievement_score,
        "internship_score": result.internship_score, "soft_skill_score": result.soft_skill_score,
        "has_strong_project": result.has_strong_project, "technology_and_tools_score": result.technology_and_tools_score
    }

# 6. Main Callable Function for your FastAPI
def calculate_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Kyunki FastAPI me text pehle hi extract ho chuka hai, 
    yeh function direct strings lega aur final scores return karega.
    """
    # Build LangGraph Workflow
    builder = StateGraph(AtsState)
    builder.add_node("summarise_desc", summarise_desc)
    builder.add_node("matching", matching)
    builder.add_edge(START, "summarise_desc")
    builder.add_edge("summarise_desc", "matching")
    builder.add_edge("matching", END)
    
    graph = builder.compile()
    
    # Run pipeline
    initial_input = {
        "desc": job_description,
        "resume": resume_text
    }
    
    final_output = graph.invoke(initial_input)
    
    # Filter only scores/results keys to send back
    score_keys = [
        "skill_score", "experience_score", "qualification_score", 
        "achievement_score", "technology_and_tools_score", 
        "internship_score", "soft_skill_score", "has_strong_project"
    ]
    return {key: final_output[key] for key in score_keys if key in final_output}

