# from langgraph.graph import StateGraph, END
# from typing import Dict, Any, List
# from datetime import datetime, timedelta
# import uuid
# import json

# from models import WorkflowState, Employee, JobPosting, Candidate, JobStatus, CandidateStatus
# from ai_service import AIService
# from linkedin_service import LinkedInService
# from email_service import EmailService
# from config import Config

# class JobAutomationWorkflow:
#     def __init__(self):
#         self.ai_service = AIService()
#         self.linkedin_service = LinkedInService()
#         self.email_service = EmailService()
        
#         # Create the workflow graph
#         self.workflow = self.create_workflow()
    
#     def create_workflow(self) -> StateGraph:
#         """Create the LangGraph workflow"""
        
#         workflow = StateGraph(WorkflowState)
        
#         # Add nodes
#         workflow.add_node("generate_job_posting", self.generate_job_posting)
#         workflow.add_node("request_human_approval", self.request_human_approval)
#         workflow.add_node("post_job_to_linkedin", self.post_job_to_linkedin)
#         workflow.add_node("check_applicants", self.check_applicants)
#         workflow.add_node("modify_job_posting", self.modify_job_posting)
#         workflow.add_node("select_top_candidates", self.select_top_candidates)
#         workflow.add_node("schedule_interviews", self.schedule_interviews)
#         workflow.add_node("conduct_interviews", self.conduct_interviews)
#         workflow.add_node("make_salary_offers", self.make_salary_offers)
#         workflow.add_node("handle_offer_responses", self.handle_offer_responses)
#         workflow.add_node("send_rejection_emails", self.send_rejection_emails)
        
#         # Set entry point
#         workflow.set_entry_point("generate_job_posting")
        
#         # Add edges
#         workflow.add_edge("generate_job_posting", "request_human_approval")
#         # workflow.add_edge("request_human_approval", "post_job_to_linkedin")
#         workflow.add_conditional_edges(
#             "post_job_to_linkedin",
#             self.should_continue_after_posting,
#             {
#                 "continue": "check_applicants",
#                 "end": END
#             }
#         )
#         workflow.add_edge("check_applicants", "select_top_candidates")
#         workflow.add_edge("modify_job_posting", "check_applicants")
#         workflow.add_edge("select_top_candidates", "schedule_interviews")
#         workflow.add_edge("schedule_interviews", "conduct_interviews")
#         workflow.add_edge("conduct_interviews", "make_salary_offers")
#         workflow.add_edge("make_salary_offers", "handle_offer_responses")
#         workflow.add_edge("handle_offer_responses", "send_rejection_emails")
#         workflow.add_edge("send_rejection_emails", END)
        
#         # Add conditional edges
#         workflow.add_conditional_edges(
#             "request_human_approval",
#             self.should_skip_approval,
#             {
#                 "skip": "post_job_to_linkedin",
#                 "wait": "request_human_approval"
#             }
#         )
        
#         workflow.add_conditional_edges(
#             "check_applicants",
#             self.should_modify_job_posting,
#             {
#                 "modify": "modify_job_posting",
#                 "continue": "select_top_candidates"
#             }
#         )
        
#         workflow.add_conditional_edges(
#             "handle_offer_responses",
#             self.should_make_counter_offer,
#             {
#                 "counter": "make_salary_offers",
#                 "complete": "send_rejection_emails"
#             }
#         )
        
#         return workflow.compile()
    
#     def generate_job_posting(self, state: WorkflowState) -> dict[str, Any]:
#         """Generate job posting using AI"""
#         print("Generating job posting...")
        
#         if not state.employee_who_quit:
#             return {"error_message": "No employee data provided"}
        
#         # Convert employee to dict for AI service
#         employee_data = {
#             "name": state.employee_who_quit.name,
#             "position": state.employee_who_quit.position,
#             "department": state.employee_who_quit.department,
#             "salary": state.employee_who_quit.salary,
#             "reason_for_leaving": state.employee_who_quit.reason_for_leaving
#         }
        
#         # Generate job posting using AI
#         job_data = self.ai_service.generate_job_posting(employee_data)
        
#         # Create JobPosting object
#         job_posting = JobPosting(
#             id=str(uuid.uuid4()),
#             title=job_data["title"],
#             department=state.employee_who_quit.department,
#             description=job_data["description"],
#             requirements=job_data["requirements"],
#             salary_range=job_data["salary_range"],
#             location="Remote",  # Default location
#             status=JobStatus.DRAFT
#         )
        
#         state.job_posting = job_posting
#         state.current_step = "job_posting_generated"
        
#         print(f"Job posting generated: {job_posting.title}")
#         return {"job_posting": job_posting, "current_step": "job_posting_generated"}
    
#     def request_human_approval(self, state: WorkflowState) -> dict[str, Any]:
#         """Request human approval for job posting"""
#         print("Requesting human approval...")

#         if not state.job_posting:
#             return {"error_message": "No job posting to approve"}

#         # Set approval pending
#         approval_pending_content = f"""
#         Job Title: {state.job_posting.title}
#         Department: {state.job_posting.department}
#         Salary Range: ₹{state.job_posting.salary_range['min']:,.2f} - ₹{state.job_posting.salary_range['max']:,.2f}

#         Description:
#         {state.job_posting.description}

#         Requirements:
#         {chr(10).join([f"- {req}" for req in state.job_posting.requirements])}

#         Please review and approve this job posting.
#         """

#         # Send approval request email
#         admin_email = "hr@company.com"
#         self.email_service.send_email(
#             admin_email,
#             "Job Posting Approval Required",
#             approval_pending_content
#         )

#         print("Human approval requested")
#         return {"human_approval_needed": True, "approval_pending_content": approval_pending_content, "current_step": "awaiting_approval"}
    
#     def should_skip_approval(self, state: WorkflowState) -> str:
#         """Determine if approval should be skipped (for demo purposes)"""
#         # In a real scenario, this would check if approval was given
#         # For demo, we'll skip approval after a short delay
#         return "skip"

#     def post_job_to_linkedin(self, state: WorkflowState) -> dict[str, Any]:
#         """Post job to LinkedIn"""
#         print("Posting job to LinkedIn...")

#         if not state.job_posting:
#             print("No job posting to post")
#             return {"current_step": "no_job_to_post"}

#         # Convert job posting to dict for LinkedIn service
#         job_data = {
#             "title": state.job_posting.title,
#             "description": state.job_posting.description,
#             "requirements": state.job_posting.requirements,
#             "salary_range": state.job_posting.salary_range,
#             "location": state.job_posting.location,
#             "department": state.job_posting.department
#         }

#         # Post to LinkedIn
#         linkedin_job_id = self.linkedin_service.post_job(job_data)

#         if linkedin_job_id:
#             state.job_posting.linkedin_post_id = linkedin_job_id
#             state.job_posting.status = JobStatus.POSTED
#             state.job_posting.posted_at = datetime.now()
#             print(f"Job posted to LinkedIn with ID: {linkedin_job_id}")
#             return {"job_posting": state.job_posting, "current_step": "job_posted"}
#         else:
#             print("Failed to post job to LinkedIn; stopping workflow early.")
#             return {"current_step": "post_failed"}

#     def should_continue_after_posting(self, state: WorkflowState) -> str:
#         """Continue only if job successfully posted; otherwise end workflow."""
#         if state.job_posting and state.job_posting.status == JobStatus.POSTED:
#             return "continue"
#         return "end"

#     def check_applicants(self, state: WorkflowState) -> dict[str, Any]:
#         """Check number of applicants"""
#         print("Checking applicants...")

#         if not state.job_posting or not state.job_posting.linkedin_post_id:
#             return {"error_message": "No job posting to check applicants for"}

#         # Get applicants from LinkedIn
#         applicants_data = self.linkedin_service.get_applicants(state.job_posting.linkedin_post_id)

#         # Convert to Candidate objects
#         candidates = []
#         for app_data in applicants_data:
#             candidate = Candidate(
#                 id=app_data["id"],
#                 name=app_data["name"],
#                 email=app_data["email"],
#                 phone=app_data["phone"],
#                 resume_url=app_data["resume_url"],
#                 experience_years=app_data["experience_years"],
#                 skills=app_data["skills"],
#                 current_salary=app_data.get("current_salary"),
#                 expected_salary=app_data.get("expected_salary")
#             )
#             candidates.append(candidate)
        
#         state.job_posting.applicant_count = len(candidates) # Update the existing job_posting object

#         print(f"Found {len(candidates)} applicants")
#         return {"candidates": candidates, "job_posting": state.job_posting, "current_step": "applicants_checked"}

#     def should_modify_job_posting(self, state: WorkflowState) -> str:
#         """Determine if job posting should be modified based on applicant count"""
#         if state.job_posting and state.job_posting.applicant_count < Config.MIN_APPLICANTS:
#             return "modify"
#         return "continue"

#     def modify_job_posting(self, state: WorkflowState) -> dict[str, Any]:
#         """Modify job posting to attract more applicants"""
#         print("Modifying job posting to attract more applicants...")

#         if not state.job_posting:
#             return {"error_message": "No job posting to modify"}

#         # Use AI to improve the job posting
#         employee_data = {
#             "name": state.employee_who_quit.name,
#             "position": state.employee_who_quit.position,
#             "department": state.employee_who_quit.department,
#             "salary": state.employee_who_quit.salary,
#             "reason_for_leaving": state.employee_who_quit.reason_for_leaving
#         }

#         # Generate improved job posting
#         improved_job_data = self.ai_service.generate_job_posting(employee_data)

#         # Update existing job posting
#         state.job_posting.title = improved_job_data["title"]
#         state.job_posting.description = improved_job_data["description"]
#         state.job_posting.requirements = improved_job_data["requirements"]
#         state.job_posting.salary_range = improved_job_data["salary_range"]
#         state.job_posting.status = JobStatus.MODIFIED

#         # Update on LinkedIn
#         if state.job_posting.linkedin_post_id:
#             updates = {
#                 "title": state.job_posting.title,
#                 "description": state.job_posting.description
#             }
#             self.linkedin_service.update_job_posting(state.job_posting.linkedin_post_id, updates)

#         print("Job posting modified")
#         return {"job_posting": state.job_posting, "current_step": "job_modified"}

#     def select_top_candidates(self, state: WorkflowState) -> dict[str, Any]:
#         """Select top candidates using AI analysis"""
#         print("Selecting top candidates...")

#         if not state.candidates or not state.job_posting:
#             return {"error_message": "No candidates or job posting to analyze"}

#         # Convert candidates to dict for AI service
#         candidates_data = [
#             {
#                 "id": c.id,
#                 "name": c.name,
#                 "experience_years": c.experience_years,
#                 "skills": c.skills
#             }
#             for c in state.candidates
#         ]

#         # Analyze candidates using AI
#         rankings = self.ai_service.analyze_candidates(candidates_data, state.job_posting.requirements)

#         # Sort candidates by score and select top 5
#         candidate_scores = {r["candidate_id"]: r["score"] for r in rankings}

#         # Sort candidates by score (descending)
#         sorted_candidates = sorted(
#             state.candidates,
#             key=lambda c: candidate_scores.get(c.id, 0),
#             reverse=True
#         )

#         # Select top candidates
#         top_candidates = sorted_candidates[:Config.TOP_CANDIDATES_COUNT]

#         # Update candidate status
#         for candidate in top_candidates:
#             candidate.status = CandidateStatus.SELECTED

#         print(f"Selected {len(top_candidates)} top candidates")
#         return {"selected_candidates": top_candidates, "current_step": "candidates_selected"}

#     def schedule_interviews(self, state: WorkflowState) -> dict[str, Any]:
#         """Schedule interviews with selected candidates"""
#         print("Scheduling interviews...")
#         if not state.selected_candidates:
#             return {"error_message": "No candidates selected for interviews"}

#         # Interview is 2 days after job posting
#         if hasattr(state.job_posting, 'posted_at') and state.job_posting.posted_at:
#             base_date = state.job_posting.posted_at + timedelta(days=2)
#         else:
#             base_date = datetime.now() + timedelta(days=2)

#         # Google Calendar integration
#         credentials_file = getattr(Config, 'GOOGLE_CALENDAR_CREDENTIALS', 'google_service_account.json')
#         hr_email = getattr(Config, 'HR_EMAIL', 'hr@company.com')
#         calendar = CalendarService(credentials_file)
#         interview_time = datetime.time(15, 0)  # 3:00 PM IST

#         for i, candidate in enumerate(state.selected_candidates):
#             interview_date = datetime.combine(base_date.date(), interview_time)
#             candidate.interview_scheduled = interview_date
#             # Send interview invitation
#             self.email_service.send_interview_invitation(
#                 {
#                     "name": candidate.name,
#                     "email": candidate.email
#                 },
#                 interview_date,
#                 state.job_posting.title
#             )
#             # Create Google Calendar event
#             summary = f"Interview: {candidate.name}"
#             description = f"Interview with {candidate.name} for {state.job_posting.title}"
#             attendees = [candidate.email, hr_email]
#             event_link = calendar.create_interview_event(summary, description, interview_date, attendees)
#             candidate.calendar_event_link = event_link
#             print(f"Interview event created: {event_link}")

#         print(f"Scheduled interviews for {len(state.selected_candidates)} candidates")
#         return {"selected_candidates": state.selected_candidates, "current_step": "interviews_scheduled"}

#     def conduct_interviews(self, state: WorkflowState) -> dict[str, Any]:
#         """Conduct interviews and evaluate candidates"""
#         print("Conducting interviews...")

#         if not state.selected_candidates:
#             return {"error_message": "No candidates to interview"}

#         for candidate in state.selected_candidates:
#             # Generate interview questions
#             candidate_data = {
#                 "name": candidate.name,
#                 "experience_years": candidate.experience_years,
#                 "skills": candidate.skills
#             }

#             questions = self.ai_service.generate_interview_questions(
#                 candidate_data,
#                 state.job_posting.requirements
#             )

#             # Simulate interview evaluation (in real scenario, this would be done by humans)
#             # For demo, we'll use a simple scoring system
#             interview_score = min(10, candidate.experience_years + len(candidate.skills))
#             candidate.interview_feedback = f"Interview score: {interview_score}/10"
#             candidate.status = CandidateStatus.INTERVIEWED

#         print("Interviews completed")
#         return {"selected_candidates": state.selected_candidates, "current_step": "interviews_completed"}

#     def make_salary_offers(self, state: WorkflowState) -> dict[str, Any]:
#         """Make salary offers to interviewed candidates"""
#         print("Making salary offers...")

#         if not state.selected_candidates:
#             return {"error_message": "No candidates to make offers to"}

#         for candidate in state.selected_candidates:
#             if candidate.status == CandidateStatus.INTERVIEWED:
#                 # Generate salary offer using AI
#                 candidate_data = {
#                     "name": candidate.name,
#                     "experience_years": candidate.experience_years,
#                     "skills": candidate.skills,
#                     "current_salary": candidate.current_salary,
#                     "expected_salary": candidate.expected_salary
#                 }

#                 offer_data = self.ai_service.generate_salary_offer(
#                     candidate_data,
#                     state.job_posting.salary_range
#                 )

#                 candidate.offer_salary = offer_data["offer_amount"]
#                 candidate.status = CandidateStatus.OFFERED

#                 # Send offer email
#                 self.email_service.send_salary_offer(
#                     {
#                         "name": candidate.name,
#                         "email": candidate.email
#                     },
#                     offer_data['offer_amount'],
#                     state.job_posting.title
#                 )

#         print("Salary offers made")
#         return {"selected_candidates": state.selected_candidates, "current_step": "offers_made"}

#     def handle_offer_responses(self, state: WorkflowState) -> dict[str, Any]:
#         """Handle candidate responses to offers"""
#         print("Handling offer responses...")

#         if not state.selected_candidates:
#             return {"error_message": "No candidates to handle responses for"}

#         for candidate in state.selected_candidates:
#             if candidate.status == CandidateStatus.OFFERED:
#                 # Simulate candidate response (in real scenario, this would come from email responses)
#                 # For demo, we'll simulate some acceptances and rejections
#                 import random
#                 response = random.choice(["accept", "reject", "counter"])

#                 if response == "accept":
#                     candidate.status = CandidateStatus.ACCEPTED
#                     candidate.offer_status = "accepted"
#                     print(f"{candidate.name} accepted the offer")

#                 elif response == "reject":
#                     candidate.status = CandidateStatus.REJECTED
#                     candidate.offer_status = "rejected"
#                     print(f"{candidate.name} rejected the offer")

#                 elif response == "counter":
#                     candidate.status = CandidateStatus.COUNTER_OFFERED
#                     candidate.offer_status = "counter_offered"
#                     print(f"{candidate.name} made a counter offer")

#         print("Offer responses handled")
#         return {"selected_candidates": state.selected_candidates, "current_step": "responses_handled"}

#     def should_make_counter_offer(self, state: WorkflowState) -> str:
#         """Determine if counter offers should be made"""
#         # Check if any candidates made counter offers
#         counter_offers = [c for c in state.selected_candidates if c.status == CandidateStatus.COUNTER_OFFERED]
#         if counter_offers:
#             return "counter"
#         return "complete"

#     def send_rejection_emails(self, state: WorkflowState) -> dict[str, Any]:
#         """Send rejection emails to candidates who weren't selected"""
#         print("Sending rejection emails...")

#         # Send rejections to candidates who weren't selected for interviews
#         for candidate in state.candidates:
#             if candidate not in state.selected_candidates:
#                 self.email_service.send_rejection_email(
#                     {
#                         "name": candidate.name,
#                         "email": candidate.email
#                     },
#                     state.job_posting.title
#                 )

#         # Send rejections to candidates who were interviewed but not offered or rejected offers
#         for candidate in state.selected_candidates:
#             if candidate.status in [CandidateStatus.REJECTED, CandidateStatus.INTERVIEWED]:
#                 self.email_service.send_rejection_email(
#                     {
#                         "name": candidate.name,
#                         "email": candidate.email
#                     },
#                     state.job_posting.title
#                 )

#         print("Rejection emails sent")
#         return {"current_step": "rejections_sent", "workflow_completed": True}
    
#     def run_workflow(self, employee_data: Dict[str, Any]) -> WorkflowState:
#         """Run the complete job automation workflow"""
#         print("Starting job automation workflow...")
        
#         # Create initial state
#         employee = Employee(**employee_data)
#         initial_state = WorkflowState(employee_who_quit=employee)
        
#         # Run the workflow
#         try:
#             final_state = self.workflow.invoke(initial_state)
#             print("Workflow completed successfully!")
#             # Ensure we always return a WorkflowState even if the graph returns a dict
#             if isinstance(final_state, WorkflowState):
#                 return final_state
#             # Merge dict keys back into state for safety
#             for key, value in (final_state or {}).items():
#                 setattr(initial_state, key, value)
#             return initial_state
#         except Exception as e:
#             print(f"Workflow failed: {str(e)}")
#             initial_state.error_message = str(e)
#             return initial_state


from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import random
import json

from models import WorkflowState, Employee, JobPosting, Candidate, JobStatus, CandidateStatus
from ai_service import AIService
from linkedin_service import LinkedInService
from email_service import EmailService
from config import Config


class JobAutomationWorkflow:
    def __init__(self):
        self.ai = AIService()
        self.linkedin = LinkedInService()
        self.email = EmailService()
        self.workflow = self._create_workflow()

    # ----------------------------
    # Workflow Definition
    # ----------------------------
    def _create_workflow(self) -> StateGraph:
        wf = StateGraph(WorkflowState)

        # Define nodes
        wf.add_node("generate_job_posting", self.generate_job_posting)
        wf.add_node("request_human_approval", self.request_human_approval)
        wf.add_node("post_job_to_linkedin", self.post_job_to_linkedin)
        wf.add_node("check_applicants", self.check_applicants)
        wf.add_node("modify_job_posting", self.modify_job_posting)
        wf.add_node("select_top_candidates", self.select_top_candidates)
        wf.add_node("schedule_interviews", self.schedule_interviews)
        wf.add_node("conduct_interviews", self.conduct_interviews)
        wf.add_node("make_salary_offers", self.make_salary_offers)
        wf.add_node("handle_offer_responses", self.handle_offer_responses)
        wf.add_node("send_rejection_emails", self.send_rejection_emails)

        # Entry point
        wf.set_entry_point("generate_job_posting")

        # Edges
        wf.add_edge("generate_job_posting", "request_human_approval")
        wf.add_conditional_edges("request_human_approval", self.should_skip_approval, {
            "skip": "post_job_to_linkedin",
            "wait": "request_human_approval"
        })
        wf.add_conditional_edges("post_job_to_linkedin", self.should_continue_after_posting, {
            "continue": "check_applicants",
            "end": END
        })
        wf.add_conditional_edges("check_applicants", self.should_modify_job_posting, {
            "modify": "modify_job_posting",
            "continue": "select_top_candidates"
        })
        wf.add_edge("modify_job_posting", "check_applicants")
        wf.add_edge("select_top_candidates", "schedule_interviews")
        wf.add_edge("schedule_interviews", "conduct_interviews")
        wf.add_edge("conduct_interviews", "make_salary_offers")
        wf.add_edge("make_salary_offers", "handle_offer_responses")
        wf.add_conditional_edges("handle_offer_responses", self.should_make_counter_offer, {
            "counter": "make_salary_offers",
            "complete": "send_rejection_emails"
        })
        wf.add_edge("send_rejection_emails", END)

        return wf.compile()

    # ----------------------------
    # Workflow Steps
    # ----------------------------
    def generate_job_posting(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.employee_who_quit:
            return {"error_message": "No employee data provided"}

        emp = state.employee_who_quit
        
        # Get employee's office location from CSV
        employee_location = self._get_employee_location(emp.id)
        
        job_data = self.ai.generate_job_posting({
            "name": emp.name,
            "position": emp.position,
            "department": emp.department,
            "salary": emp.salary,
            "reason_for_leaving": emp.reason_for_leaving,
            "location": employee_location
        })

        state.job_posting = JobPosting(
            id=str(uuid.uuid4()),
            title=job_data["title"],
            department=emp.department,
            description=job_data["description"],
            requirements=job_data["requirements"],
            salary_range=job_data["salary_range"],
            location=employee_location,
            status=JobStatus.DRAFT
        )
        # Persist latest requirements so the inbox watcher scores resumes against the posted JD
        try:
            from pathlib import Path
            req_path = Path('latest_requirements.txt')
            lines = [str(r).strip() for r in state.job_posting.requirements if str(r).strip()]
            if lines:
                req_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
        except Exception as _persist_err:
            print(f"Warning: could not write latest_requirements.txt: {_persist_err}")
        
        # Display the generated job description
        self._display_job_description(state)
        
        return {"job_posting": state.job_posting, "current_step": "job_posting_generated"}
    
    def _get_employee_location(self, employee_id: str) -> str:
        """Get employee's office location from CSV"""
        try:
            import csv
            with open("employees.csv", mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['id'] == employee_id:
                        return row.get('office_location', 'Remote')
            return "Remote"  # Default fallback
        except Exception as e:
            print(f"Error reading employee location: {e}")
            return "Remote"
    
    def _display_job_description(self, state):
        """Display the complete job description"""
        if not state.job_posting:
            return
        
        print("\n" + "="*60)
        print("📋 GENERATED JOB DESCRIPTION")
        print("="*60)
        
        print(f"\n📝 JOB POSTING DETAILS:")
        print(f"Title: {state.job_posting.title}")
        print(f"Department: {state.job_posting.department}")
        print(f"Salary Range: ₹{state.job_posting.salary_range['min']:,.2f} - ₹{state.job_posting.salary_range['max']:,.2f}")
        print(f"Location: {state.job_posting.location}")
        
        print(f"\n📝 DESCRIPTION:")
        print(state.job_posting.description)
        
        print(f"\n📋 REQUIREMENTS:")
        for i, req in enumerate(state.job_posting.requirements, 1):
            print(f"{i}. {req}")
        
        # Show employee skills from original data if available
        if state.employee_who_quit:
            print(f"\n💼 EMPLOYEE SKILLS (from CSV):")
            # Try to get skills from the original employee data
            try:
                # Read the CSV to get additional employee details
                import csv
                with open("employees.csv", mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['id'] == state.employee_who_quit.id:
                            if row.get('skills_required'):
                                skills = row['skills_required'].split(',')
                                for skill in skills:
                                    print(f"  • {skill.strip()}")
                            
                            print(f"\n📊 ADDITIONAL INFO:")
                            print(f"  • Experience Level: {row.get('years_of_experience', 'N/A')} years")
                            print(f"  • Education: {row.get('education_level', 'N/A')}")
                            if row.get('certifications'):
                                print(f"  • Certifications: {row['certifications']}")
                            if row.get('projects_handled'):
                                print(f"  • Projects Handled: {row['projects_handled']}")
                            break
            except Exception as e:
                print(f"  (Additional details not available: {e})")

    def request_human_approval(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.job_posting:
            return {"error_message": "No job posting to approve"}

        # Skip sending approval emails; proceed without human approval in this streamlined flow
        return {"human_approval_needed": False, "approval_pending_content": "", "current_step": "awaiting_approval"}

    # ============================================================
    # Agentic subgraph: Resume Intake (LangGraph)
    # ============================================================
    def run_resume_intake_graph_once(self):
        """Run a lightweight LangGraph subgraph to process inbox resumes using latest JD requirements."""
        try:
            from langgraph.graph import StateGraph, END
        except Exception:
            print("LangGraph not available; cannot run resume intake graph.")
            return

        from pathlib import Path
        from ai_service import AIService
        from email_service import EmailService

        # Simple dict-based state
        def load_requirements(state: dict) -> dict:
            reqs: list[str] = []
            p = Path('latest_requirements.txt')
            if p.exists():
                reqs = [line.strip() for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
            state['requirements'] = reqs
            return state

        def fetch_resumes(state: dict) -> dict:
            email_svc = EmailService()
            resumes = email_svc.fetch_resumes_from_inbox()
            state['resumes'] = resumes or []
            return state

        def score_resumes(state: dict) -> dict:
            ai = AIService()
            requirements = state.get('requirements', [])
            summaries: list[dict] = []
            for r in state.get('resumes', []):
                text = r.get('text', '') or ''
                scoring = ai.score_resume_against_requirements(text, requirements)
                breakdown = scoring.get('breakdown', {})
                summaries.append({
                    'candidate': r.get('from_email', ''),
                    'file': r.get('filename', ''),
                    'score': scoring.get('score', 0),
                    'matched': ", ".join(scoring.get('matched', [])[:4]),
                    'missing': ", ".join(scoring.get('missing', [])[:4]),
                    'breakdown': breakdown,
                })
            state['summaries'] = summaries
            return state

        def output_summaries(state: dict) -> dict:
            summaries = state.get('summaries', [])
            if not summaries:
                print("No new resumes found.")
                return state
            print("\n📊 ATS Summary (new resumes):")
            for row in summaries:
                print(f"\n👤 {row['candidate']} | 📄 {row['file']}")
                print(f"   🎯 Overall Score: {row['score']}/100")
                br = row.get('breakdown', {})
                if br:
                    print(f"   📝 Keywords: {br.get('keywords', 0)}/30")
                    print(f"   🛠️  Skills: {br.get('skills', 0)}/25")
                    print(f"   💼 Experience: {br.get('experience', 0)}/20")
                    print(f"   🎓 Education: {br.get('education', 0)}/15")
                    print(f"   📋 Format: {br.get('format', 0)}/10")
                print(f"   ✅ Matched: {row.get('matched', '')}")
                print(f"   ❌ Missing: {row.get('missing', '')}")

            # Email notifications: invite top 3 by score OR anyone with score >= 80; reject others
            try:
                notifier = EmailService()
                # Invite strictly the top 3 candidates by score
                ordered = sorted(summaries, key=lambda r: r.get('score', 0), reverse=True)
                invitees = {r.get('candidate') for r in ordered[:3] if r.get('candidate')}

                job_title = "Interview - Current Opening"
                # Send interview scheduling emails to invitees
                slot_index = 0  # to keep a 30-minute gap between candidates
                for r in summaries:
                    to_email = r.get('candidate') or ""
                    if not to_email:
                        continue
                    if to_email in invitees:
                        # Schedule interview 2 days later at 14:00 and include details in email
                        try:
                            from calendar_service import CalendarService
                            import os as _os
                            from datetime import datetime as _dt, timedelta as _td, time as _time
                            credentials_file = _os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "google_service_account.json")
                            calendar_id = _os.getenv("GOOGLE_CALENDAR_ID", _os.getenv("EMAIL_USERNAME"))
                            calendar = CalendarService(credentials_file, calendar_id)
                            # Start 2 days later at 14:00, roll forward to weekday if needed
                            base_dt = _dt.combine((_dt.now() + _td(days=2)).date(), _time(14, 0))
                            while base_dt.weekday() >= 5:  # 5=Sat, 6=Sun
                                base_dt = base_dt + _td(days=1)
                            # Add 30-min gap per invitee
                            interview_duration = 30
                            interview_datetime = base_dt + _td(minutes=slot_index * 30)
                            summary = f"Interview: {to_email}"
                            description = f"Interview scheduled for candidate {to_email} (auto)"
                            attendees = [to_email, _os.getenv('EMAIL_USERNAME')]
                            event_link = calendar.create_interview_event(
                                summary,
                                description,
                                interview_datetime,
                                attendees,
                                duration_minutes=interview_duration,
                            )
                            # Send invitation including the scheduled details
                            notifier.send_interview_invitation(
                                {"name": to_email, "email": to_email},
                                job_title,
                                interview_datetime=interview_datetime,
                                event_link=event_link,
                            )
                            slot_index += 1
                        except Exception as _cal_err:
                            print(f"Warning: Failed to schedule calendar event: {_cal_err}")
                            # Fallback to template asking for availability
                            notifier.send_interview_invitation(
                                {"name": to_email, "email": to_email},
                                job_title,
                            )

                # Send rejection emails to the rest
                for r in summaries:
                    to_email = r.get('candidate') or ""
                    if not to_email or to_email in invitees:
                        continue
                    # Use new rejection template without ATS score
                    notifier.send_rejection_email(
                        {"name": to_email, "email": to_email},
                        job_title,
                    )
            except Exception as notify_err:
                print(f"Warning: Failed to send notifications: {notify_err}")
            return state

        # Optional: handle candidate replies proposing time slots
        def handle_candidate_replies(state: dict) -> dict:
            try:
                from ai_service import AIService
                from email_service import EmailService
                ai = AIService()
                mailer = EmailService()
                replies = mailer.fetch_interview_replies()
                if not replies:
                    return state
                from datetime import datetime
                from dateutil import parser as date_parser  # requires python-dateutil
                for m in replies:
                    body = m.get('body', '')
                    sender = m.get('from_email', '')
                    slots = ai.extract_meeting_slots(body)
                    confirmed = None
                    for s in slots:
                        try:
                            dt = date_parser.parse(s)
                            if dt > datetime.now():
                                confirmed = dt.isoformat(timespec='minutes')
                                break
                        except Exception:
                            continue
                    if confirmed and sender:
                        mailer.send_confirmation_email(sender, confirmed)
            except Exception as _err:
                print(f"Warning: Failed to handle candidate replies: {_err}")
            return state

        graph = StateGraph(dict)
        graph.add_node('load_requirements', load_requirements)
        graph.add_node('fetch_resumes', fetch_resumes)
        graph.add_node('score_resumes', score_resumes)
        graph.add_node('output_summaries', output_summaries)
        graph.add_node('handle_candidate_replies', handle_candidate_replies)

        graph.set_entry_point('load_requirements')
        graph.add_edge('load_requirements', 'fetch_resumes')
        graph.add_edge('fetch_resumes', 'score_resumes')
        graph.add_edge('score_resumes', 'output_summaries')
        graph.add_edge('output_summaries', 'handle_candidate_replies')
        graph.add_edge('handle_candidate_replies', END)

        app = graph.compile()
        app.invoke({})

    def should_skip_approval(self, _: WorkflowState) -> str:
        return "skip"  # Auto-skip in demo

    def post_job_to_linkedin(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.job_posting:
            return {"current_step": "no_job_to_post"}

        job_data = {
            "title": state.job_posting.title,
            "description": state.job_posting.description,
            "requirements": state.job_posting.requirements,
            "salary_range": state.job_posting.salary_range,
            "location": state.job_posting.location,
            "department": state.job_posting.department,
        }

        print(f"\n📱 Posting to LinkedIn...")
        post_id = self.linkedin.post_job(job_data)
        
        if post_id:
            state.job_posting.linkedin_post_id = post_id
            state.job_posting.status = JobStatus.POSTED
            state.job_posting.posted_at = datetime.now()
            
            if self.linkedin.mock_mode:
                print(f"✅ Mock LinkedIn post created (ID: {post_id})")
                print(f"   In real mode, this would be posted to your LinkedIn profile")
            else:
                print(f"✅ LinkedIn post created successfully! (ID: {post_id})")
                print(f"   Check your LinkedIn profile to see the post")
            
            return {"job_posting": state.job_posting, "current_step": "job_posted"}
        else:
            print(f"❌ Failed to post to LinkedIn")
            if not self.linkedin.mock_mode:
                print(f"   This might be due to API permissions or network issues")
                print(f"   Check your LinkedIn API configuration")
            return {"current_step": "post_failed"}

    def should_continue_after_posting(self, state: WorkflowState) -> str:
        # Stop the workflow after posting the JD to LinkedIn
        return "end"

    def check_applicants(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.job_posting or not state.job_posting.linkedin_post_id:
            return {"error_message": "No job posting to check applicants for"}

        applicants = self.linkedin.get_applicants(state.job_posting.linkedin_post_id)
        candidates = [Candidate(**a) for a in applicants]

        state.job_posting.applicant_count = len(candidates)
        return {"candidates": candidates, "job_posting": state.job_posting, "current_step": "applicants_checked"}

    def should_modify_job_posting(self, state: WorkflowState) -> str:
        return "modify" if state.job_posting and state.job_posting.applicant_count < Config.MIN_APPLICANTS else "continue"

    def modify_job_posting(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.job_posting:
            return {"error_message": "No job posting to modify"}

        emp = state.employee_who_quit
        new_job = self.ai.generate_job_posting(vars(emp))
        state.job_posting.title = new_job["title"]
        state.job_posting.description = new_job["description"]
        state.job_posting.requirements = new_job["requirements"]
        state.job_posting.salary_range = new_job["salary_range"]
        state.job_posting.status = JobStatus.MODIFIED

        if state.job_posting.linkedin_post_id:
            self.linkedin.update_job_posting(state.job_posting.linkedin_post_id, {
                "title": state.job_posting.title,
                "description": state.job_posting.description
            })
        return {"job_posting": state.job_posting, "current_step": "job_modified"}

    def select_top_candidates(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.candidates or not state.job_posting:
            return {"error_message": "No candidates or job posting"}

        rankings = self.ai.analyze_candidates(
            [{"id": c.id, "name": c.name, "experience_years": c.experience_years, "skills": c.skills}
             for c in state.candidates],
            state.job_posting.requirements
        )

        scores = {r["candidate_id"]: r["score"] for r in rankings}
        sorted_candidates = sorted(state.candidates, key=lambda c: scores.get(c.id, 0), reverse=True)
        top_candidates = sorted_candidates[:Config.TOP_CANDIDATES_COUNT]

        for c in top_candidates:
            c.status = CandidateStatus.SELECTED
        return {"selected_candidates": top_candidates, "current_step": "candidates_selected"}

    def schedule_interviews(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.selected_candidates:
            return {"error_message": "No candidates selected"}

        base_date = datetime.now() + timedelta(days=7)
        for i, c in enumerate(state.selected_candidates):
            c.interview_scheduled = base_date + timedelta(days=i * 2)
            self.email.send_interview_invitation({"name": c.name, "email": c.email}, c.interview_scheduled, state.job_posting.title)
        return {"selected_candidates": state.selected_candidates, "current_step": "interviews_scheduled"}

    def conduct_interviews(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.selected_candidates:
            return {"error_message": "No candidates"}

        for c in state.selected_candidates:
            questions = self.ai.generate_interview_questions({"name": c.name, "experience_years": c.experience_years, "skills": c.skills}, state.job_posting.requirements)
            score = min(10, c.experience_years + len(c.skills))
            c.interview_feedback = f"Score: {score}/10"
            c.status = CandidateStatus.INTERVIEWED
        return {"selected_candidates": state.selected_candidates, "current_step": "interviews_completed"}

    def make_salary_offers(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.selected_candidates:
            return {"error_message": "No candidates"}

        for c in state.selected_candidates:
            if c.status == CandidateStatus.INTERVIEWED:
                offer = self.ai.generate_salary_offer(vars(c), state.job_posting.salary_range)
                c.offer_salary = offer["offer_amount"]
                c.status = CandidateStatus.OFFERED
                self.email.send_salary_offer({"name": c.name, "email": c.email}, c.offer_salary, state.job_posting.title)
        return {"selected_candidates": state.selected_candidates, "current_step": "offers_made"}

    def handle_offer_responses(self, state: WorkflowState) -> Dict[str, Any]:
        if not state.selected_candidates:
            return {"error_message": "No candidates"}

        for c in state.selected_candidates:
            if c.status == CandidateStatus.OFFERED:
                response = random.choice(["accept", "reject", "counter"])
                if response == "accept":
                    c.status, c.offer_status = CandidateStatus.ACCEPTED, "accepted"
                elif response == "reject":
                    c.status, c.offer_status = CandidateStatus.REJECTED, "rejected"
                else:
                    c.status, c.offer_status = CandidateStatus.COUNTER_OFFERED, "counter_offered"
        return {"selected_candidates": state.selected_candidates, "current_step": "responses_handled"}

    def should_make_counter_offer(self, state: WorkflowState) -> str:
        return "counter" if any(c.status == CandidateStatus.COUNTER_OFFERED for c in state.selected_candidates) else "complete"

    def send_rejection_emails(self, state: WorkflowState) -> Dict[str, Any]:
        for c in state.candidates:
            if c not in state.selected_candidates or c.status in [CandidateStatus.REJECTED, CandidateStatus.INTERVIEWED]:
                self.email.send_rejection_email({"name": c.name, "email": c.email}, state.job_posting.title)
        return {"current_step": "rejections_sent", "workflow_completed": True}

    # ----------------------------
    # Runner
    # ----------------------------
    def run_workflow(self, employee_data: Dict[str, Any]) -> WorkflowState:
        emp = Employee(**employee_data)
        state = WorkflowState(employee_who_quit=emp)
        try:
            final = self.workflow.invoke(state)
            if isinstance(final, WorkflowState):
                return final
            for k, v in (final or {}).items():
                setattr(state, k, v)
            return state
        except Exception as e:
            state.error_message = str(e)
            return state
