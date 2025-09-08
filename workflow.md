# Gmail-Based Agentic Hiring System - Complete Workflow

# ------------------------------------- SHORTER VERSION START HERE -------------------------------------

# Gmail-Based Hiring System - Short Workflow

## Quick Overview
Automated hiring pipeline: Employee departure → JD creation → LinkedIn posting → Gmail resume collection → ATS scoring → Interview → Hiring decision

## 8-Step Simplified Workflow

### 1. **Employee Monitor** 📊
- Check employee CSV for departures
- Extract departed employee's job details
- **Output**: Job role info

### 2. **JD Generator** 📝
- Use AI to create job description from role info
- Format for LinkedIn posting
- **Output**: Professional JD + LinkedIn post

### 3. **Gmail Scanner** 📧
- Monitor Gmail for resume emails
- Extract PDF/DOC attachments
- Parse resume text
- **Output**: Candidate data with resume content

### 4. **ATS Scorer** 🎯
- Score resumes against job requirements (0-100)
  - Keywords (30%) + Skills (25%) + Experience (20%) + Education (15%) + Format (10%)
- Rank all candidates
- **Output**: Top 5 candidates with ATS scores

### 5. **Interview Scheduler** 📅
- Send interview invites to top 5
- Collect availability
- **Output**: Scheduled interviews

### 6. **Candidate Selector** ✅
- Combine ATS scores + interview feedback
- Select best candidate
- **Output**: Final candidate choice

### 7. **Offer Manager** 💰
- Generate salary offer
- Handle negotiations (max 3 rounds)
- **Output**: Accepted offer or move to backup

### 8. **Communication Hub** 📨
- Send rejection emails to unsuccessful candidates
- Send welcome email to selected candidate
- **Output**: Process complete

## LangGraph Flow
```
START → Monitor Employees → Generate JD → Scan Gmail → Score Resumes → Schedule Interviews → Select Candidate → Send Offer → Communicate Results → END
```

## Key Decision Points
- **Departure detected?** (Yes/No)
- **New resumes found?** (Yes/No) 
- **ATS score ≥ 60?** (Qualified/Reject)
- **Top 5 candidates available?** (Interview/Wait)
- **Offer accepted?** (Hire/Negotiate/Next candidate)

## Core Components
- **Gmail API** for resume collection
- **AI/LLM** for JD generation and ATS scoring
- **PDF/DOC parsers** for resume extraction
- **Email automation** for communications
- **SQLite** for candidate tracking

## Timeline
- **Setup**: 2 weeks
- **Per hiring cycle**: 7-10 days
- **Resume processing**: 1-2 hours for 50+ resumes

## Tech Stack
- **LangGraph** - Workflow orchestration
- **OpenAI/Local LLM** - AI tasks
- **Gmail API** - Email handling
- **PyPDF2/python-docx** - Resume parsing
- **Pandas** - Data processing

# --------------------------------------------SHORTER VERSION END HERE ---------------------------------------




#-----------------------------------------LONGER VERSION START HERE --------------------------------------

## Project Overview
An automated hiring system that monitors Gmail for resume submissions, uses ATS scoring for candidate evaluation, and manages the complete recruitment lifecycle through LangGraph.

## High-Level Architecture

```
Employee Data → Departure Detection → JD Generation → LinkedIn Post → Gmail Monitoring → ATS Scoring → Interview Process → Hiring Decision
```

## Detailed Workflow Breakdown

### Phase 1: Employee Departure Detection & JD Creation

#### Node 1: Monitor Employee Database
- **Input**: Local CSV/JSON employee file
- **Process**: Compare current data with previous snapshot
- **Decision Point**: Employee departed? (Yes → Continue, No → Wait)
- **Output**: Departed employee details (name, role, department, responsibilities)

#### Node 2: Generate Job Description
- **Input**: Departed employee role information
- **AI Task**: Use LLM to create professional JD based on:
  - Job title and level
  - Department requirements
  - Previous employee's responsibilities
  - Current market standards
- **Output**: Complete job description with requirements and benefits

#### Node 3: Create LinkedIn Post
- **Input**: Generated job description
- **Process**: 
  - Format JD for LinkedIn post (engaging, concise)
  - Add application instructions with your Gmail
  - Include relevant hashtags
- **Output**: LinkedIn post content with Gmail application instructions

### Phase 2: Application Collection & Processing

#### Node 4: Monitor Gmail for Applications
- **Input**: Your Gmail inbox
- **Process**: 
  - Scan for emails with job-related subjects
  - Filter by keywords: "application", "resume", "job", etc.
  - Identify new applications since last check
- **Decision Point**: New applications found? (Yes → Process, No → Wait)
- **Output**: List of new application emails

#### Node 5: Extract & Validate Resumes
- **Input**: Application emails
- **Process**: 
  - Download PDF/DOC attachments
  - Validate file types and sizes
  - Extract candidate contact info from email
  - Parse resume text content
- **Quality Check**: Resume readable and valid?
- **Output**: Structured candidate data with parsed resume text

### Phase 3: ATS Scoring & Candidate Ranking

#### Node 6: ATS Score Calculation
- **Input**: Parsed resume text + job requirements
- **AI Processing**: 
  - **Keyword Matching**: Score based on job-specific keywords
  - **Skill Assessment**: Match technical skills with requirements
  - **Experience Analysis**: Years of experience vs requirement
  - **Education Verification**: Degree requirements met
  - **Format Quality**: Resume structure and readability
- **Scoring Components**:
  - Keywords (30 points)
  - Skills Match (25 points)
  - Experience Level (20 points)
  - Education (15 points)
  - Format Quality (10 points)
- **Output**: Each candidate gets ATS score (0-100)

#### Node 7: Rank & Filter Candidates
- **Input**: All candidates with ATS scores
- **Process**: 
  - Rank candidates by ATS score (highest first)
  - Apply minimum threshold (e.g., score ≥ 60)
  - Select top 5 qualified candidates
- **Decision Point**: Enough qualified candidates? (Yes → Continue, No → Wait for more applications)
- **Output**: Top 5 ranked candidates with detailed analysis

### Phase 4: Interview Scheduling & Management

#### Node 8: Send Interview Invitations
- **Input**: Top 5 candidates
- **Process**: 
  - Generate personalized interview invitation emails
  - Include interview format (video/in-person)
  - Provide available time slots
  - Send calendar invites
- **Output**: Interview schedules with candidate confirmations

#### Node 9: Collect Interview Feedback
- **Input**: Completed interviews
- **Process**: 
  - Gather feedback from interviewers
  - Score technical performance
  - Evaluate cultural fit
  - Rate communication skills
- **Decision Point**: Any candidate meets hiring bar?
- **Output**: Final candidate rankings with interview scores

### Phase 5: Decision Making & Offer Management

#### Node 10: Select Final Candidate
- **Input**: Combined ATS scores + interview feedback
- **AI Decision**: 
  - Weight ATS score (40%) + Interview score (60%)
  - Select highest combined score
  - Verify candidate still interested
- **Output**: Selected candidate + rejection list

#### Node 11: Generate & Send Offer
- **Input**: Selected candidate info
- **AI Task**: 
  - Create salary offer based on:
    - Market research
    - Candidate experience
    - Company budget
    - Previous employee salary (as baseline)
- **Process**: Send professional offer letter via email
- **Output**: Offer details and candidate response tracking

#### Node 12: Handle Offer Response
- **Decision Points**: 
  - **Accepted**: → Send welcome package + onboarding
  - **Declined**: → Move to backup candidate
  - **Counter-offer**: → Negotiate (max 3 rounds)
- **Negotiation Logic**: 
  - Compare counter-offer with budget
  - Use AI to generate counter-proposal
  - Track negotiation rounds
- **Output**: Final hiring decision

### Phase 6: Communication & Closure

#### Node 13: Send Status Updates
- **Input**: Final hiring decision
- **Process**: 
  - Send rejection emails to unsuccessful candidates
  - Include personalized feedback based on ATS scores
  - Send welcome email to selected candidate
  - Update employee database with new hire
- **Output**: Complete communication log

#### Node 14: Archive & Learn
- **Input**: Complete hiring process data
- **Process**: 
  - Store all resumes and scores for future reference
  - Analyze process metrics (time to hire, success rate)
  - Update ATS scoring model based on successful hires
- **Output**: Process completion report

## LangGraph State Structure

```python
class HiringState(TypedDict):
    # Employee monitoring
    employee_data: Dict
    departed_employee: Dict
    departure_detected: bool
    
    # Job creation
    job_description: str
    job_requirements: List[str]
    linkedin_post_content: str
    
    # Gmail monitoring
    new_applications: List[Dict]
    all_applications: List[Dict]
    
    # Resume processing
    parsed_resumes: List[Dict]
    valid_resumes: List[Dict]
    
    # ATS scoring
    ats_scores: List[Dict]
    top_candidates: List[Dict]
    score_threshold: int
    
    # Interview process
    interview_invites_sent: List[Dict]
    interview_feedback: List[Dict]
    interview_scores: List[Dict]
    
    # Final selection
    selected_candidate: Dict
    backup_candidates: List[Dict]
    rejected_candidates: List[Dict]
    
    # Offer management
    current_offer: Dict
    negotiation_rounds: int
    final_decision: str
    
    # Communication
    emails_sent: List[str]
    process_complete: bool
```

## ATS Scoring Algorithm Details

### Keyword Scoring (30 points)
- Extract keywords from JD (skills, tools, technologies)
- Count exact matches in resume
- Calculate percentage match
- Bonus for rare/important keywords

### Skills Assessment (25 points)
- Technical skills matching
- Programming languages
- Frameworks and tools
- Certifications and credentials

### Experience Analysis (20 points)
- Years of relevant experience
- Industry experience
- Leadership/management experience
- Career progression pattern

### Education Scoring (15 points)
- Degree requirements met
- Relevant field of study
- Institution reputation (optional)
- Additional certifications

### Format Quality (10 points)
- Resume structure and organization
- Grammar and spelling
- Professional presentation
- Contact information completeness

## Conditional Logic & Decision Points

### Primary Decisions:
1. **Departure Detected?** → Continue or wait
2. **New Applications?** → Process or wait
3. **Valid Resumes?** → Score or request resubmission
4. **Minimum Score Met?** → Interview or reject
5. **Enough Candidates?** → Proceed or wait for more
6. **Interview Pass?** → Offer or reject
7. **Offer Response?** → Welcome, negotiate, or next candidate

### Fallback Scenarios:
- **No qualified candidates**: Lower threshold or repost job
- **All candidates reject**: Increase salary range
- **Technical issues**: Human intervention alerts
- **Email parsing failures**: Manual review queue

## Process Automation Schedule

### Real-time Monitoring:
- **Gmail check**: Every 30 minutes
- **Employee data check**: Every 6 hours
- **LinkedIn post engagement**: Every 2 hours

### Batch Processing:
- **ATS scoring**: Process all new resumes every hour
- **Ranking updates**: Recalculate scores every 4 hours
- **Communication**: Send emails in batches

## Success Metrics & KPIs

### Efficiency Metrics:
- Time from departure to job posting: < 4 hours
- Time from application to ATS score: < 1 hour
- Time to screen 100 resumes: < 2 hours
- Overall hiring cycle: < 10 days

### Quality Metrics:
- ATS score accuracy: > 85% correlation with hire success
- Interview show rate: > 80%
- Offer acceptance rate: > 70%
- New hire retention: > 90% at 6 months

## Risk Management

### Error Handling:
- Gmail API rate limits → Queue management
- Resume parsing failures → Manual review
- ATS scoring errors → Human validation
- Email delivery issues → Retry logic

### Human Oversight Points:
- Final candidate selection review
- Salary offer approval
- Negotiation limit approval
- Process intervention triggers

## Implementation Phases

### Phase 1: Core Pipeline (Week 1-2)
- Employee monitoring + JD generation
- Gmail integration + resume parsing
- Basic ATS scoring algorithm

### Phase 2: Intelligence Layer (Week 3-4)
- Advanced ATS scoring with AI
- Interview scheduling automation
- Email template generation

### Phase 3: Decision Making (Week 5-6)
- Offer generation and negotiation
- Advanced ranking algorithms
- Process optimization

### Phase 4: Polish & Scale (Week 7-8)
- Error handling and monitoring
- Performance optimization
- Analytics and reporting

This workflow gives you a production-ready system that handles the entire hiring pipeline automatically while keeping you in control of the final decisions!


# ------------------------------------------ LONGER VERSION END HERE --------------------------------------