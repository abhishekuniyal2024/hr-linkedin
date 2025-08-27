# Job Automation System

An intelligent job automation system built with LangGraph and Groq API that automates the entire job posting and hiring process. The system uses agentic AI to create job postings, manage candidates, conduct interviews, and handle salary negotiations.

## Features

- 🤖 **AI-Powered Job Posting Generation**: Creates compelling job postings based on employee departure information
- 👥 **Human Approval Workflow**: Requests human intervention before posting jobs
- 📱 **LinkedIn Integration**: Posts jobs to LinkedIn and tracks applicants
- 🎯 **Smart Candidate Selection**: Uses AI to analyze and rank candidates
- 📅 **Automated Interview Scheduling**: Schedules interviews with top candidates
- 💰 **Intelligent Salary Negotiation**: Generates salary offers and handles counter-offers
- 📧 **Automated Email Communication**: Sends interview invitations, offers, and rejection emails
- 🔄 **Dynamic Job Posting Optimization**: Modifies job postings if insufficient applicants

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Employee      │    │   AI Service    │    │  LinkedIn       │
│   Departure     │───▶│   (Groq API)    │───▶│  Integration    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  LangGraph      │    │  Email Service  │    │  Candidate      │
│  Workflow       │    │  (SMTP)         │    │  Management     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- Groq API key
- LinkedIn API credentials (optional, for production use)
- SMTP email credentials (optional, for production use)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd job-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create a .env file or set environment variables
   export GROQ_API_KEY="your_groq_api_key_here"
   export LINKEDIN_CLIENT_ID="your_linkedin_client_id"
   export LINKEDIN_CLIENT_SECRET="your_linkedin_client_secret"
   export LINKEDIN_ACCESS_TOKEN="your_linkedin_access_token"
   export EMAIL_SMTP_SERVER="smtp.gmail.com"
   export EMAIL_SMTP_PORT="587"
   export EMAIL_USERNAME="your_email@gmail.com"
   export EMAIL_PASSWORD="your_email_password"
   ```

## Configuration

### Required Configuration

- **GROQ_API_KEY**: Your Groq API key (required for AI functionality)

### Optional Configuration

- **LinkedIn API**: For posting jobs to LinkedIn (uses mock data if not configured)
- **Email SMTP**: For sending emails (uses mock functionality if not configured)

## Usage

### Quick Start

1. **Run the main script**:
   ```bash
   python main.py
   ```

2. **Choose input method**:
   - Option 1: Use example data
   - Option 2: Enter custom employee data

3. **Follow the prompts** to complete the workflow

### Example Workflow

```python
from job_automation_workflow import JobAutomationWorkflow

# Create workflow instance
workflow = JobAutomationWorkflow()

# Employee data
employee_data = {
    "id": "emp_001",
    "name": "John Doe",
    "position": "Senior Software Engineer",
    "department": "Engineering",
    "salary": 85000.0,
    "last_working_day": datetime.now(),
    "reason_for_leaving": "Career growth opportunity"
}

# Run the workflow
final_state = workflow.run_workflow(employee_data)
```

## Workflow Steps

1. **Generate Job Posting**: AI creates a job posting based on employee departure
2. **Human Approval**: System requests approval before posting
3. **Post to LinkedIn**: Job is posted to LinkedIn
4. **Check Applicants**: System monitors applicant count
5. **Optimize if Needed**: Modifies job posting if insufficient applicants
6. **Select Top Candidates**: AI analyzes and ranks candidates
7. **Schedule Interviews**: Automatically schedules interviews
8. **Conduct Interviews**: Simulates interview process
9. **Make Offers**: AI generates salary offers
10. **Handle Responses**: Processes acceptances, rejections, and counter-offers
11. **Send Rejections**: Sends rejection emails to unsuccessful candidates

## File Structure

```
job-automation/
├── main.py                      # Main execution script
├── job_automation_workflow.py   # LangGraph workflow definition
├── ai_service.py               # Groq API integration
├── linkedin_service.py         # LinkedIn API integration
├── email_service.py            # Email functionality
├── models.py                   # Data models and schemas
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## API Integration

### Groq API

The system uses Groq's LLM API for:
- Job posting generation
- Candidate analysis and ranking
- Interview question generation
- Salary offer generation
- Counter-offer analysis

### LinkedIn API

For production use, configure LinkedIn API to:
- Post job listings
- Retrieve applicant data
- Update job postings
- Get job statistics

### Email Service

Configure SMTP settings to send:
- Interview invitations
- Salary offers
- Counter-offers
- Rejection emails

## Customization

### Modifying Job Requirements

Edit `config.py` to customize:
- Minimum applicant threshold
- Number of top candidates to select
- Salary ranges
- Email templates

### Adding New Workflow Steps

Extend the LangGraph workflow in `job_automation_workflow.py`:
1. Add new node functions
2. Update the workflow graph
3. Add conditional edges as needed

### Custom AI Prompts

Modify prompts in `ai_service.py` to customize:
- Job posting generation
- Candidate evaluation criteria
- Interview questions
- Salary negotiation logic

## Testing

The system includes mock functionality for testing:

```python
# Mock LinkedIn posting
linkedin_service.mock_post_job(job_data)

# Mock email sending
email_service.mock_send_email(to_email, subject, body)
```

## Error Handling

The system includes comprehensive error handling:
- API failures
- Invalid data
- Workflow interruptions
- Network issues

## Security Considerations

- Store API keys securely
- Use environment variables for sensitive data
- Implement proper authentication for production use
- Follow LinkedIn API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the example usage

## Roadmap

- [ ] Real LinkedIn API integration
- [ ] Advanced candidate scoring algorithms
- [ ] Interview scheduling with calendar integration
- [ ] Multi-language support
- [ ] Dashboard for workflow monitoring
- [ ] Integration with ATS systems
- [ ] Advanced analytics and reporting 