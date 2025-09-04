from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class JobStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    POSTED = "posted"
    MODIFIED = "modified"
    CLOSED = "closed"

class CandidateStatus(str, Enum):
    APPLIED = "applied"
    SELECTED = "selected"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTER_OFFERED = "counter_offered"

class Employee(BaseModel):
    id: str
    name: str
    position: str
    department: str
    salary: float
    last_working_day: datetime
    reason_for_leaving: str

class JobPosting(BaseModel):
    id: str
    title: str
    department: str
    description: str
    requirements: List[str]
    salary_range: Dict[str, float]
    location: str
    status: JobStatus = JobStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    posted_at: Optional[datetime] = None
    applicant_count: int = 0
    linkedin_post_id: Optional[str] = None

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    resume_url: str
    experience_years: int
    skills: List[str]
    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    status: CandidateStatus = CandidateStatus.APPLIED
    applied_at: datetime = Field(default_factory=datetime.now)
    interview_scheduled: Optional[datetime] = None
    interview_feedback: Optional[str] = None
    offer_salary: Optional[float] = None
    offer_status: Optional[str] = None

class WorkflowState(BaseModel):
    employee_who_quit: Optional[Employee] = None
    job_posting: Optional[JobPosting] = None
    candidates: List[Candidate] = Field(default_factory=list)
    selected_candidates: List[Candidate] = Field(default_factory=list)
    current_step: str = "start"
    human_approval_needed: bool = False
    approval_pending_content: Optional[str] = None
    workflow_completed: bool = False
    error_message: Optional[str] = None 