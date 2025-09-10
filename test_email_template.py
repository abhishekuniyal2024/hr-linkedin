from datetime import datetime
from email_service import EmailService

if __name__ == "__main__":
    email_service = EmailService()
    candidate = {"name": "Test Candidate", "email": "abhishekuniyal2123@gmail.com"}
    interview_date = datetime.now().replace(hour=14, minute=0)  # today at 2:00 PM
    job_title = "Software Engineer"
    print("Sending test interview invitation email...")
    email_service.send_interview_invitation(candidate, interview_date, job_title)
    print("Done. Check your inbox for the template.")
