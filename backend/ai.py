import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key and len(api_key) > 30 else None

# Rule-based fallback for skills and questions
FALLBACK_SKILLS = []
FALLBACK_QUESTIONS = {
    "Python": ("What are decorators in Python and how do they work?", "Decorators wrap a function, modifying its behavior. They are used via the @ symbol."),
    "JavaScript": ("Explain the concept of closures in JavaScript.", "A closure is a function having access to the parent scope, even after the parent function has closed."),
    "React": ("What are React Hooks and why were they introduced?", "Hooks let you use state and lifecycle methods in functional components, avoiding complex class structures."),
    "SQL": ("What is the difference between an INNER JOIN and a LEFT JOIN?", "INNER returns only rows with matches in both tables. LEFT returns all rows from the left table and matched rows from the right."),
    "Machine Learning": ("Explain the bias-variance tradeoff.", "Bias causes underfitting. Variance causes overfitting. You must balance both to generalize well."),
    "Deep Learning": ("What is backpropagation?", "The algorithm used to calculate the gradient of the loss function with respect to weights using the chain rule."),
    "FastAPI": ("How does FastAPI handle asynchronous requests?", "It is built on top of Starlette and ASGI, using Python's async/await syntax to handle concurrent requests natively without blocking."),
    "Linear Algebra": ("What is an eigenvalue?", "A scalar lambda where Av = lambda * v, preserving the direction of the eigenvector v under transformation A."),
    "Statistics": ("Explain the central limit theorem.", "The sampling distribution of the sample mean approaches a normal distribution as the sample size gets larger, regardless of the population distribution.")
}

def extract_skills_from_resume(resume_text: str) -> list:
    """Uses OpenAI to extract a list of skills from a resume. Fallback to rule-based."""
    if not client:
        print("No valid OpenAI API Key found. Using fallback logic.")
        return FALLBACK_SKILLS

    # Truncate text to avoid Free Tier Groq 6000 TPM limit
    resume_text = resume_text[:15000]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter. Extract ALL hard technical skills from the resume text. Return ONLY a valid JSON object matching this exact format: {\"skills\": [\"Python\", \"React\"]}"},
                {"role": "user", "content": resume_text}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content, strict=False)
        skills = parsed.get("skills", [])
        if isinstance(skills, list) and len(skills) > 0:
            return skills
        return FALLBACK_SKILLS
    except Exception as e:
        print(f"AI Extraction failed: {e}. Using fallback.")
        return FALLBACK_SKILLS

def generate_mock_interview_question(skill: str) -> tuple:
    """Uses Groq to generate a mock interview question and answer for a given skill. Fallback to rule-based."""
    if not client:
        return FALLBACK_QUESTIONS.get(skill, (f"Can you describe your experience with {skill}?", "Candidate should describe relevant projects and concrete challenges they solved using this technology."))

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"You are a technical interviewer. Generate ONE challenging but fair technical interview question for a candidate claiming the skill: {skill}. You must write a comprehensive answer to evaluate them against. Output ONLY valid JSON containing exactly two string keys: 'question' (a string) and 'answer' (a single continuous string, do NOT use arrays or nested objects). Example: {{\\\"question\\\": \\\"...\\\", \\\"answer\\\": \\\"...\\\"}}"}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0), strict=False)
            return parsed.get("question", "Failed to parse question."), parsed.get("answer", "Failed to parse answer.")
        return "Failed to parse question.", "Failed to parse answer."
    except Exception as e:
        print(f"AI Question Generation failed: {e}. Using fallback.")
        return FALLBACK_QUESTIONS.get(skill, (f"Can you describe your experience with {skill}?", "Candidate should describe relevant projects and concrete challenges they solved using this technology."))

def generate_verification_question(skill: str, missing_prereqs: list) -> tuple:
    """Uses Groq to generate a verification question when prerequisites are missing. Fallback to rule-based."""
    if not client:
        return FALLBACK_QUESTIONS.get(skill, (f"You claim {skill} without {', '.join(missing_prereqs)}. How did you learn it?", "Candidate should explain their non-traditional learning path."))

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"A candidate claims the skill '{skill}' but is missing the standard prerequisites: {', '.join(missing_prereqs)}. Generate ONE deep technical interview question that tests if they actually understand the foundations of '{skill}'. Provide the answer too. Output ONLY valid JSON containing exactly two string keys: 'question' (a string) and 'answer' (a single continuous string, do NOT use arrays or nested objects). Example: {{\\\"question\\\": \\\"...\\\", \\\"answer\\\": \\\"...\\\"}}"}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0), strict=False)
            return parsed.get("question", "Failed to parse question."), parsed.get("answer", "Failed to parse answer.")
        return "Failed to parse question.", "Failed to parse answer."
    except Exception as e:
        print(f"AI Verification Generation failed: {e}. Using fallback.")
        return FALLBACK_QUESTIONS.get(skill, (f"You claim {skill} without {', '.join(missing_prereqs)}. How did you learn it?", "Candidate should explain their non-traditional learning path."))

def extract_role_from_jd(jd_text: str) -> dict:
    if not client:
        return {"title": "Software Engineer", "description": "Generic Developer", "required_skills": ["Python", "SQL"]}
    
    jd_text = jd_text[:15000]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert technical data extractor. Read the provided job description.
Extract the Job Title, Description, and an array of REQUIRED HARD SKILLS.
CRITICAL: The 'required_skills' array elements MUST be extremely concise, single-word or 2-word technical skill names.
DO NOT include or copy ANY of the original sentences from the text. 
EVERY single array element MUST be 1 to 3 words maximum. Discard the original phrasing completely.

BAD: ["Proficiency in one or more modern programming languages like Python and Java"]
GOOD: ["Python", "Java"]

BAD: ["Understanding of software development lifecycle, DevOps principles, and Git"]
GOOD: ["SDLC", "DevOps", "Git", "Version Control"]

Return ONLY a JSON object EXACTLY matching: {"title": "Role Title", "description": "Short summary", "required_skills": ["Skill1", "Skill2", "Skill3"]}"""
                },
                {"role": "user", "content": jd_text}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content, strict=False)
        if "required_skills" in parsed:
            parsed["required_skills"] = [s for s in parsed["required_skills"] if s.lower().strip() not in ["programming", "ai"]]
        return parsed
        return {"title": "Software Engineer", "description": "Generic Developer", "required_skills": ["Python", "SQL"]}
    except Exception as e:
        print(f"JD Extraction failed: {e}")
        return {"title": "Software Engineer", "description": "Generic Developer", "required_skills": ["Python", "SQL"]}

def extract_skills_from_syllabus(syllabus_text: str) -> list:
    if not client:
        return [{"subject": "Data Structures", "skills": [{"name": "C++", "tag": "language"}]}]
        
    syllabus_text = syllabus_text[:15000]
        
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Extract the academic academic subject names from the syllabus. For every subject, aggressively extract ALL mentioned Programming Languages, Hardware, Software Tools, and Frameworks. Output max 25 subjects. Return ONLY a valid JSON object EXACTLY matching this format: {\"subjects\": [{\"subject\": \"Subject Name\", \"skills\": [{\"name\": \"Specific Language or Tool (e.g. Python, C, Jupyter, HTML)\", \"tag\": \"language/tool/framework\"}]}]}"},
                {"role": "user", "content": syllabus_text}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content, strict=False)
        subjects = parsed.get("subjects", [])
        if isinstance(subjects, list) and len(subjects) > 0:
            return subjects
        return []
    except Exception as e:
        print(f"Syllabus Extraction failed: {e}")
        return []
