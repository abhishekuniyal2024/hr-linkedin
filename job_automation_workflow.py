from langgraph.graph import StateGraph, END
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid
import json

from models import WorkflowState, Employee, JobPosting, Candidate, JobStatus, CandidateStatus
from ai_service import AIService
from linkedin_service import LinkedInService
from email_service import EmailService
from config import Config

class JobAutomationWorkflow:
    def __init__(self):
        self.ai_service = AIService()
        self.linkedin_service = LinkedInService()
        self.email_service = EmailService()
        
        # Create the workflow graph
        self.workflow = self.create_workflow()
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("generate_job_posting", self.generate_job_posting)
        workflow.add_node("request_human_approval", self.request_human_approval)
        workflow.add_node("post_job_to_linkedin", self.post_job_to_linkedin)
        workflow.add_node("check_applicants", self.check_applicants)
        workflow.add_node("modify_job_posting", self.modify_job_posting)
        workflow.add_node("select_top_candidates", self.select_top_candidates)
        workflow.add_node("schedule_interviews", self.schedule_interviews)
        workflow.add_node("conduct_interviews", self.conduct_interviews)
        workflow.add_node("make_salary_offers", self.make_salary_offers)
        workflow.add_node("handle_offer_responses", self.handle_offer_responses)
        workflow.add_node("send_rejection_emails", self.send_rejection_emails)
        
        # Set entry point
        workflow.set_entry_point("generate_job_posting")
        
        # Add edges
        workflow.add_edge("generate_job_posting", "request_human_approval")
        workflow.add_edge("request_human_approval", "post_job_to_linkedin")
        workflow.add_edge("post_job_to_linkedin", "check_applicants")
        workflow.add_edge("check_applicants", "select_top_candidates")
        workflow.add_edge("modify_job_posting", "check_applicants")
        workflow.add_edge("select_top_candidates", "schedule_interviews")
        workflow.add_edge("schedule_interviews", "conduct_interviews")
        workflow.add_edge("conduct_interviews", "make_salary_offers")
        workflow.add_edge("make_salary_offers", "handle_offer_responses")
        workflow.add_edge("handle_offer_responses", "send_rejection_emails")
        workflow.add_edge("send_rejection_emails", END)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "request_human_approval",
            self.should_skip_approval,
            {
                "skip": "post_job_to_linkedin",
                "wait": "request_human_approval"
            }
        )
        
        workflow.add_conditional_edges(
            "check_applicants",
            self.should_modify_job_posting,
            {
                "modify": "modify_job_posting",
                "continue": "select_top_candidates"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_offer_responses",
            self.should_make_counter_offer,
            {
                "counter": "make_salary_offers",
                "complete": "send_rejection_emails"
            }
        )
        
        return workflow.compile()
    
    def generate_job_posting(self, state: WorkflowState) -> WorkflowState:
        """Generate job posting using AI"""
        print("Generating job posting...")
        
        if not state.employee_who_quit:
            state.error_message = "No employee data provided"
            return state
        
        # Convert employee to dict for AI service
        employee_data = {
            "name": state.employee_who_quit.name,
            "position": state.employee_who_quit.position,
            "department": state.employee_who_quit.department,
            "salary": state.employee_who_quit.salary,
            "reason_for_leaving": state.employee_who_quit.reason_for_leaving
        }
        
        # Generate job posting using AI
        job_data = self.ai_service.generate_job_posting(employee_data)
        
        # Create JobPosting object
        job_posting = JobPosting(
            id=str(uuid.uuid4()),
            title=job_data["title"],
            department=state.employee_who_quit.department,
            description=job_data["description"],
            requirements=job_data["requirements"],
            salary_range=job_data["salary_range"],
            location="Remote",  # Default location
            status=JobStatus.DRAFT
        )
        
        state.job_posting = job_posting
        state.current_step = "job_posting_generated"
        
        print(f"Job posting generated: {job_posting.title}")
        return state
    
    def request_human_approval(self, state: WorkflowState) -> WorkflowState:
        """Request human approval for job posting"""
        print("Requesting human approval...")
        
        if not state.job_posting:
            state.error_message = "No job posting to approve"
            return state
        
        # Set approval pending
        state.human_approval_needed = True
        state.approval_pending_content = f"""
        Job Title: {state.job_posting.title}
        Department: {state.job_posting.department}
        Salary Range: ${state.job_posting.salary_range['min']:,.2f} - ${state.job_posting.salary_range['max']:,.2f}
        
        Description:
        {state.job_posting.description}
        
        Requirements:
        {chr(10).join([f"- {req}" for req in state.job_posting.requirements])}
        
        Please review and approve this job posting.
        """
        
        # Send approval request email
        admin_email = "hr@company.com"
        self.email_service.send_email(
            admin_email,
            "Job Posting Approval Required",
            state.approval_pending_content
        )
        
        state.current_step = "awaiting_approval"
        print("Human approval requested")
        return state
    
    def should_skip_approval(self, state: WorkflowState) -> str:
        """Determine if approval should be skipped (for demo purposes)"""
        # In a real scenario, this would check if approval was given
        # For demo, we'll skip approval after a short delay
        return "skip"
    
    def post_job_to_linkedin(self, state: WorkflowState) -> WorkflowState:
        """Post job to LinkedIn"""
        print("Posting job to LinkedIn...")
        
        if not state.job_posting:
            state.error_message = "No job posting to post"
            return state
        
        # Convert job posting to dict for LinkedIn service
        job_data = {
            "title": state.job_posting.title,
            "description": state.job_posting.description,
            "requirements": state.job_posting.requirements,
            "salary_range": state.job_posting.salary_range,
            "location": state.job_posting.location,
            "department": state.job_posting.department
        }
        
        # Post to LinkedIn
        linkedin_job_id = self.linkedin_service.post_job(job_data)
        
        if linkedin_job_id:
            state.job_posting.linkedin_post_id = linkedin_job_id
            state.job_posting.status = JobStatus.POSTED
            state.job_posting.posted_at = datetime.now()
            state.current_step = "job_posted"
            print(f"Job posted to LinkedIn with ID: {linkedin_job_id}")
        else:
            state.error_message = "Failed to post job to LinkedIn"
        
        return state
    
    def check_applicants(self, state: WorkflowState) -> WorkflowState:
        """Check number of applicants"""
        print("Checking applicants...")
        
        if not state.job_posting or not state.job_posting.linkedin_post_id:
            state.error_message = "No job posting to check applicants for"
            return state
        
        # Get applicants from LinkedIn
        applicants_data = self.linkedin_service.get_applicants(state.job_posting.linkedin_post_id)
        
        # Convert to Candidate objects
        candidates = []
        for app_data in applicants_data:
            candidate = Candidate(
                id=app_data["id"],
                name=app_data["name"],
                email=app_data["email"],
                phone=app_data["phone"],
                resume_url=app_data["resume_url"],
                experience_years=app_data["experience_years"],
                skills=app_data["skills"],
                current_salary=app_data.get("current_salary"),
                expected_salary=app_data.get("expected_salary")
            )
            candidates.append(candidate)
        
        state.candidates = candidates
        state.job_posting.applicant_count = len(candidates)
        state.current_step = "applicants_checked"
        
        print(f"Found {len(candidates)} applicants")
        return state
    
    def should_modify_job_posting(self, state: WorkflowState) -> str:
        """Determine if job posting should be modified based on applicant count"""
        if state.job_posting and state.job_posting.applicant_count < Config.MIN_APPLICANTS:
            return "modify"
        return "continue"
    
    def modify_job_posting(self, state: WorkflowState) -> WorkflowState:
        """Modify job posting to attract more applicants"""
        print("Modifying job posting to attract more applicants...")
        
        if not state.job_posting:
            state.error_message = "No job posting to modify"
            return state
        
        # Use AI to improve the job posting
        employee_data = {
            "name": state.employee_who_quit.name,
            "position": state.employee_who_quit.position,
            "department": state.employee_who_quit.department,
            "salary": state.employee_who_quit.salary,
            "reason_for_leaving": state.employee_who_quit.reason_for_leaving
        }
        
        # Generate improved job posting
        improved_job_data = self.ai_service.generate_job_posting(employee_data)
        
        # Update existing job posting
        state.job_posting.title = improved_job_data["title"]
        state.job_posting.description = improved_job_data["description"]
        state.job_posting.requirements = improved_job_data["requirements"]
        state.job_posting.salary_range = improved_job_data["salary_range"]
        state.job_posting.status = JobStatus.MODIFIED
        
        # Update on LinkedIn
        if state.job_posting.linkedin_post_id:
            updates = {
                "title": state.job_posting.title,
                "description": state.job_posting.description
            }
            self.linkedin_service.update_job_posting(state.job_posting.linkedin_post_id, updates)
        
        state.current_step = "job_modified"
        print("Job posting modified")
        return state
    
    def select_top_candidates(self, state: WorkflowState) -> WorkflowState:
        """Select top candidates using AI analysis"""
        print("Selecting top candidates...")
        
        if not state.candidates or not state.job_posting:
            state.error_message = "No candidates or job posting to analyze"
            return state
        
        # Convert candidates to dict for AI service
        candidates_data = [
            {
                "id": c.id,
                "name": c.name,
                "experience_years": c.experience_years,
                "skills": c.skills
            }
            for c in state.candidates
        ]
        
        # Analyze candidates using AI
        rankings = self.ai_service.analyze_candidates(candidates_data, state.job_posting.requirements)
        
        # Sort candidates by score and select top 5
        candidate_scores = {r["candidate_id"]: r["score"] for r in rankings}
        
        # Sort candidates by score (descending)
        sorted_candidates = sorted(
            state.candidates,
            key=lambda c: candidate_scores.get(c.id, 0),
            reverse=True
        )
        
        # Select top candidates
        top_candidates = sorted_candidates[:Config.TOP_CANDIDATES_COUNT]
        
        # Update candidate status
        for candidate in top_candidates:
            candidate.status = CandidateStatus.SELECTED
        
        state.selected_candidates = top_candidates
        state.current_step = "candidates_selected"
        
        print(f"Selected {len(top_candidates)} top candidates")
        return state
    
    def schedule_interviews(self, state: WorkflowState) -> WorkflowState:
        """Schedule interviews with selected candidates"""
        print("Scheduling interviews...")
        
        if not state.selected_candidates:
            state.error_message = "No candidates selected for interviews"
            return state
        
        # Schedule interviews for next week
        base_date = datetime.now() + timedelta(days=7)
        
        for i, candidate in enumerate(state.selected_candidates):
            # Schedule interview 2 days apart
            interview_date = base_date + timedelta(days=i * 2)
            candidate.interview_scheduled = interview_date
            
            # Send interview invitation
            self.email_service.send_interview_invitation(
                {
                    "name": candidate.name,
                    "email": candidate.email
                },
                interview_date,
                state.job_posting.title
            )
        
        state.current_step = "interviews_scheduled"
        print(f"Scheduled interviews for {len(state.selected_candidates)} candidates")
        return state
    
    def conduct_interviews(self, state: WorkflowState) -> WorkflowState:
        """Conduct interviews and evaluate candidates"""
        print("Conducting interviews...")
        
        if not state.selected_candidates:
            state.error_message = "No candidates to interview"
            return state
        
        for candidate in state.selected_candidates:
            # Generate interview questions
            candidate_data = {
                "name": candidate.name,
                "experience_years": candidate.experience_years,
                "skills": candidate.skills
            }
            
            questions = self.ai_service.generate_interview_questions(
                candidate_data, 
                state.job_posting.requirements
            )
            
            # Simulate interview evaluation (in real scenario, this would be done by humans)
            # For demo, we'll use a simple scoring system
            interview_score = min(10, candidate.experience_years + len(candidate.skills))
            candidate.interview_feedback = f"Interview score: {interview_score}/10"
            candidate.status = CandidateStatus.INTERVIEWED
        
        state.current_step = "interviews_completed"
        print("Interviews completed")
        return state
    
    def make_salary_offers(self, state: WorkflowState) -> WorkflowState:
        """Make salary offers to interviewed candidates"""
        print("Making salary offers...")
        
        if not state.selected_candidates:
            state.error_message = "No candidates to make offers to"
            return state
        
        for candidate in state.selected_candidates:
            if candidate.status == CandidateStatus.INTERVIEWED:
                # Generate salary offer using AI
                candidate_data = {
                    "name": candidate.name,
                    "experience_years": candidate.experience_years,
                    "skills": candidate.skills,
                    "current_salary": candidate.current_salary,
                    "expected_salary": candidate.expected_salary
                }
                
                offer_data = self.ai_service.generate_salary_offer(
                    candidate_data, 
                    state.job_posting.salary_range
                )
                
                candidate.offer_salary = offer_data["offer_amount"]
                candidate.status = CandidateStatus.OFFERED
                
                # Send offer email
                self.email_service.send_salary_offer(
                    {
                        "name": candidate.name,
                        "email": candidate.email
                    },
                    offer_data['offer_amount'],
                    state.job_posting.title
                )
        
        state.current_step = "offers_made"
        print("Salary offers made")
        return state
    
    def handle_offer_responses(self, state: WorkflowState) -> WorkflowState:
        """Handle candidate responses to offers"""
        print("Handling offer responses...")
        
        if not state.selected_candidates:
            state.error_message = "No candidates to handle responses for"
            return state
        
        for candidate in state.selected_candidates:
            if candidate.status == CandidateStatus.OFFERED:
                # Simulate candidate response (in real scenario, this would come from email responses)
                # For demo, we'll simulate some acceptances and rejections
                import random
                response = random.choice(["accept", "reject", "counter"])
                
                if response == "accept":
                    candidate.status = CandidateStatus.ACCEPTED
                    candidate.offer_status = "accepted"
                    print(f"{candidate.name} accepted the offer")
                    
                elif response == "reject":
                    candidate.status = CandidateStatus.REJECTED
                    candidate.offer_status = "rejected"
                    print(f"{candidate.name} rejected the offer")
                    
                elif response == "counter":
                    candidate.status = CandidateStatus.COUNTER_OFFERED
                    candidate.offer_status = "counter_offered"
                    print(f"{candidate.name} made a counter offer")
        
        state.current_step = "responses_handled"
        print("Offer responses handled")
        return state
    
    def should_make_counter_offer(self, state: WorkflowState) -> str:
        """Determine if counter offers should be made"""
        # Check if any candidates made counter offers
        counter_offers = [c for c in state.selected_candidates if c.status == CandidateStatus.COUNTER_OFFERED]
        if counter_offers:
            return "counter"
        return "complete"
    
    def send_rejection_emails(self, state: WorkflowState) -> WorkflowState:
        """Send rejection emails to candidates who weren't selected"""
        print("Sending rejection emails...")
        
        # Send rejections to candidates who weren't selected for interviews
        for candidate in state.candidates:
            if candidate not in state.selected_candidates:
                self.email_service.send_rejection_email(
                    {
                        "name": candidate.name,
                        "email": candidate.email
                    },
                    state.job_posting.title
                )
        
        # Send rejections to candidates who were interviewed but not offered or rejected offers
        for candidate in state.selected_candidates:
            if candidate.status in [CandidateStatus.REJECTED, CandidateStatus.INTERVIEWED]:
                self.email_service.send_rejection_email(
                    {
                        "name": candidate.name,
                        "email": candidate.email
                    },
                    state.job_posting.title
                )
        
        state.current_step = "rejections_sent"
        state.workflow_completed = True
        print("Rejection emails sent")
        return state
    
    def run_workflow(self, employee_data: Dict[str, Any]) -> WorkflowState:
        """Run the complete job automation workflow"""
        print("Starting job automation workflow...")
        
        # Create initial state
        employee = Employee(**employee_data)
        initial_state = WorkflowState(employee_who_quit=employee)
        
        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            print("Workflow completed successfully!")
            return final_state
        except Exception as e:
            print(f"Workflow failed: {str(e)}")
            initial_state.error_message = str(e)
            return initial_state 