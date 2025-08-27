from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict, Any
import json
from config import Config

class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model_name="llama3-70b-8192"
        )
    
    def generate_job_posting(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a job posting based on the employee who quit"""
        
        system_prompt = """You are an expert HR professional who creates compelling job postings. 
        Create a detailed job posting that will attract qualified candidates. 
        Include a compelling title, detailed description, requirements, and salary range.
        Return the response as a JSON object with keys: title, description, requirements (list), salary_range (dict with min and max)."""
        
        human_prompt = f"""
        Create a job posting for a position that was vacated by an employee who quit.
        
        Employee details:
        - Name: {employee_data['name']}
        - Position: {employee_data['position']}
        - Department: {employee_data['department']}
        - Salary: ${employee_data['salary']:,.2f}
        - Reason for leaving: {employee_data['reason_for_leaving']}
        
        Create a job posting that will attract qualified candidates to replace this employee.
        Make it compelling and professional.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Try to parse as JSON
            job_data = json.loads(response.content)
        except json.JSONDecodeError:
            # If not JSON, create a structured response
            job_data = {
                "title": f"{employee_data['position']} - {employee_data['department']}",
                "description": response.content,
                "requirements": [
                    f"Experience in {employee_data['department']}",
                    "Strong communication skills",
                    "Team player",
                    "Problem-solving abilities"
                ],
                "salary_range": {
                    "min": employee_data['salary'] * 0.9,
                    "max": employee_data['salary'] * 1.2
                }
            }
        
        return job_data
    
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