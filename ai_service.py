from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any
import json
from config import Config

class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
            model="llama-3.3-70b-versatile"
            # model="llama-3.1-8b-instant"
        )
    
    def generate_job_posting(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a job posting based on the employee who quit.

        Output constraints:
        - description must be human-written prose (no code fences/backticks, no braces, no JSON formatting words)
        - requirements must be a simple list of short bullet phrases
        - still return a JSON envelope with keys: title, description, requirements, salary_range
        """

        system_prompt = (
            "You are an expert HR professional who writes engaging, human-friendly job descriptions. "
            "Produce a valid JSON object with keys: title (string), description (string), requirements (array of strings), "
            "salary_range (object with numeric min and max). The description must be clean prose suitable for LinkedIn, "
            "and must NOT contain code fences, backticks, or JSON/braces. Requirements should be concise bullet phrases."
        )
        
        human_prompt = f"""
        Create a job posting for a replacement hire.

        Employee details:
        - Name: {employee_data['name']}
        - Position: {employee_data['position']}
        - Department: {employee_data['department']}
        - Current Salary: ${employee_data['salary']:,.2f}
        - Reason for leaving: {employee_data['reason_for_leaving']}
        - Location: {employee_data.get('location', 'Remote')}

        Style & constraints:
        - Write like a human recruiter (no code blocks/backticks, no JSON/braces in description).
        - Requirements must be short bullet phrases (no numbering or punctuation noise).
        - Keep it concise and impactful.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        print(f"[DEBUG] Raw LLM response: {response.content[:500]}...")
        
        try:
            # Clean the response content first to remove any code fences
            cleaned_content = response.content
            if cleaned_content.lstrip().startswith("```"):
                stripped = cleaned_content.strip()
                if stripped.startswith("```json"):
                    stripped = stripped[len("```json"):]
                elif stripped.startswith("```"):
                    stripped = stripped[len("```"):]
                if stripped.endswith("```"):
                    stripped = stripped[:-3]
                cleaned_content = stripped.strip()
            
            job_data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Fallback: create structured data from the response
            job_data = {
                "title": f"{employee_data['position']} - {employee_data['department']}",
                "description": self._clean_text(response.content),
                "requirements": [
                    f"Experience in {employee_data['department']}",
                    "Strong communication skills", 
                    "Team collaboration",
                    "Problem-solving mindset"
                ],
                "salary_range": {
                    "min": round(employee_data['salary'] * 0.9),
                    "max": round(employee_data['salary'] * 1.2)
                }
            }

        # Sanitize fields to ensure human-readable output
        job_data["description"] = self._clean_text(job_data.get("description", "")).strip()
        if isinstance(job_data.get("requirements"), list):
            job_data["requirements"] = [self._clean_text(str(r)).strip("- *• ") for r in job_data["requirements"] if str(r).strip()]

        return job_data

    def _clean_text(self, text: str) -> str:
        """Remove code fences/backticks and obvious JSON/braces artifacts from LLM output."""
        if not text:
            return ""
        cleaned = str(text)
        for fence in ("```json", "```", "`"):
            cleaned = cleaned.replace(fence, "")
        cleaned = cleaned.replace("{", " ").replace("}", " ")
        cleaned = cleaned.replace("[", " ").replace("]", " ")
        return " ".join(cleaned.split())
    
    def analyze_candidates(self, candidates: List[Dict[str, Any]], job_requirements: List[str]) -> List[Dict[str, Any]]:
        """Analyze candidates and rank them based on job requirements"""
        
        system_prompt = """You are an expert HR recruiter who analyzes candidate profiles and ranks them based on job requirements.
        Analyze each candidate's skills, experience, and fit for the position.
        Return a JSON array with each candidate's ID and a score from 1-10, where 10 is the best match."""
        
        candidates_text = "\n".join([
            f"Candidate {c['id']}: {c['name']}, Experience: {c['experience_years']} years, Skills: {', '.join(c['skills'])}"
            for c in candidates
        ])
        
        human_prompt = f"""
        Job Requirements: {', '.join(job_requirements)}
        
        Candidates to analyze:
        {candidates_text}
        
        Rank each candidate from 1-10 based on their fit for the position.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            rankings = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback ranking
            rankings = [
                {"candidate_id": c["id"], "score": min(10, c["experience_years"] + len(c["skills"]))}
                for c in candidates
            ]
        
        return rankings

    def score_resume_against_requirements(self, resume_text: str, requirements: List[str]) -> Dict[str, Any]:
        """Compute comprehensive ATS score using the LLM based on specific scoring factors."""
        system_prompt = (
            "You are an expert ATS evaluator. You MUST score resumes using this exact rubric:\n\n"
            "SCORING RUBRIC (Total: 100 points):\n"
            "1. Keywords (30 points) - Look for job-specific terms, technologies, methodologies mentioned in requirements\n"
            "2. Skills Match (25 points) - Technical skills and competencies that align with job requirements\n"
            "3. Experience Level (20 points) - Years of relevant experience (give points even for 1+ years)\n"
            "4. Education (15 points) - Degrees, certifications, training relevant to the field\n"
            "5. Format Quality (10 points) - Resume structure, clarity, professional presentation\n\n"
            "IMPORTANT: You MUST give points where applicable. Do not return all zeros unless the resume is completely irrelevant.\n"
            "Even a basic resume should get some points for format (5-10) and basic skills.\n\n"
            "Return ONLY valid JSON with these exact keys: score (0-100), matched (array), missing (array), "
            "breakdown (object with: keywords, skills, experience, education, format - each 0-30/25/20/15/10 respectively)."
        )

        req_lines = "\n".join([f"- {r}" for r in requirements])
        human_prompt = f"""
        JOB REQUIREMENTS:
        {req_lines}

        RESUME TEXT:
        {resume_text[:6000]}

        EVALUATION INSTRUCTIONS:
        1. Keywords (30 pts): Find terms from requirements in the resume
        2. Skills (25 pts): Match technical skills mentioned in resume to requirements  
        3. Experience (20 pts): Award points for any work experience (1+ years = 10+ points)
        4. Education (15 pts): Award points for degrees, certifications, training
        5. Format (10 pts): Award points for professional structure and clarity

        EXAMPLES:
        - Resume with Python, Django, 2 years experience, Bachelor's degree = 60-80 points
        - Resume with basic skills, 1 year experience, some education = 40-60 points
        - Resume with no relevant skills but good format = 10-20 points

        Return JSON only, no explanations.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        response = self.llm.invoke(messages)
        raw = response.content or ""
        
        # Remove common code fences like ```json ... ```
        if raw.lstrip().startswith("```"):
            stripped = raw.strip()
            # remove leading ```json or ``` and trailing ```
            if stripped.startswith("```json"):
                stripped = stripped[len("```json"):]
            elif stripped.startswith("```"):
                stripped = stripped[len("```"):]
            if stripped.endswith("```"):
                stripped = stripped[:-3]
            raw = stripped.strip()
        
        try:
            data = json.loads(raw)
            # Ensure breakdown exists with default values
            if "breakdown" not in data:
                data["breakdown"] = {
                    "keywords": 0,
                    "skills": 0,
                    "experience": 0,
                    "education": 0,
                    "format": 0
                }
        except Exception:
            data = {
                "score": 0, 
                "matched": [], 
                "missing": requirements,
                "breakdown": {
                    "keywords": 0,
                    "skills": 0,
                    "experience": 0,
                    "education": 0,
                    "format": 0
                }
            }
        return data
    
    def generate_interview_questions(self, candidate: Dict[str, Any], job_requirements: List[str]) -> List[str]:
        """Generate interview questions based on candidate profile and job requirements"""
        
        system_prompt = """You are an expert HR interviewer. Generate 5-7 relevant interview questions based on the candidate's profile and job requirements.
        Return the questions as a JSON array of strings."""
        
        human_prompt = f"""
        Generate interview questions for:
        
        Candidate: {candidate['name']}
        Experience: {candidate['experience_years']} years
        Skills: {', '.join(candidate['skills'])}
        
        Job Requirements: {', '.join(job_requirements)}
        
        Create relevant technical and behavioral questions.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            questions = json.loads(response.content)
        except json.JSONDecodeError:
            questions = [
                "Tell me about your experience in this field.",
                "What are your greatest strengths?",
                "Where do you see yourself in 5 years?",
                "Describe a challenging project you worked on.",
                "Why are you interested in this position?"
            ]
        
        return questions
    
    def generate_salary_offer(self, candidate: Dict[str, Any], job_salary_range: Dict[str, float]) -> Dict[str, Any]:
        """Generate a salary offer based on candidate experience and market rates"""
        
        system_prompt = """You are an expert HR professional who determines salary offers.
        Based on the candidate's experience, skills, and market rates, suggest an appropriate salary offer.
        Return a JSON object with: offer_amount, reasoning."""
        
        human_prompt = f"""
        Generate a salary offer for:
        
        Candidate: {candidate['name']}
        Experience: {candidate['experience_years']} years
        Skills: {', '.join(candidate['skills'])}
        Current Salary: ${candidate.get('current_salary', 0):,.2f}
        Expected Salary: ${candidate.get('expected_salary', 0):,.2f}
        
        Job Salary Range: ${job_salary_range['min']:,.2f} - ${job_salary_range['max']:,.2f}
        
        Suggest an appropriate offer amount and provide reasoning.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            offer_data = json.loads(response.content)
        except json.JSONDecodeError:
            # Calculate offer based on experience and salary range
            base_salary = job_salary_range['min']
            experience_bonus = min(candidate['experience_years'] * 0.05, 0.3)  # Max 30% bonus
            offer_amount = base_salary * (1 + experience_bonus)
            
            offer_data = {
                "offer_amount": min(offer_amount, job_salary_range['max']),
                "reasoning": f"Based on {candidate['experience_years']} years of experience and market rates"
            }
        
        return offer_data
    
    def generate_counter_offer(self, candidate: Dict[str, Any], original_offer: float, rejection_reason: str) -> Dict[str, Any]:
        """Generate a counter offer when a candidate rejects the initial offer"""
        
        system_prompt = """You are an expert HR negotiator. When a candidate rejects an offer, analyze the reason and suggest a counter offer if appropriate.
        Return a JSON object with: counter_offer_amount, reasoning, should_counter_offer (boolean)."""
        
        human_prompt = f"""
        Generate a counter offer for:
        
        Candidate: {candidate['name']}
        Original Offer: ${original_offer:,.2f}
        Rejection Reason: {rejection_reason}
        Expected Salary: ${candidate.get('expected_salary', 0):,.2f}
        
        Should we make a counter offer? If yes, suggest an amount and reasoning.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            counter_data = json.loads(response.content)
        except json.JSONDecodeError:
            # Simple counter offer logic
            expected_salary = candidate.get('expected_salary', original_offer * 1.1)
            if expected_salary > original_offer:
                counter_amount = min(expected_salary * 0.95, original_offer * 1.15)
                should_counter = True
            else:
                counter_amount = original_offer
                should_counter = False
            
            counter_data = {
                "counter_offer_amount": counter_amount,
                "reasoning": "Adjusted based on candidate's expectations",
                "should_counter_offer": should_counter
            }
        
        return counter_data 