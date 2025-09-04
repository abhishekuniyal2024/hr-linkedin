import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime, timedelta
from config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        self.mock_mode = Config.MOCK_EMAIL_MODE  # Add mock mode
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email"""
        if self.mock_mode:
            print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            print(f"[MOCK EMAIL] Body: {body[:200]}...")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_interview_invitation(self, candidate: Dict[str, Any], interview_date: datetime, job_title: str) -> bool:
        """Send interview invitation email"""
        subject = f"Interview Invitation - {job_title}"
        
        body = f"""
        <html>
        <body>
            <h2>Interview Invitation</h2>
            <p>Dear {candidate['name']},</p>
            
            <p>We are pleased to invite you for an interview for the position of <strong>{job_title}</strong>.</p>
            
            <h3>Interview Details:</h3>
            <ul>
                <li><strong>Date:</strong> {interview_date.strftime('%B %d, %Y')}</li>
                <li><strong>Time:</strong> {interview_date.strftime('%I:%M %p')}</li>
                <li><strong>Duration:</strong> 45-60 minutes</li>
            </ul>
            
            <p>The interview will be conducted via video call. You will receive a meeting link 30 minutes before the scheduled time.</p>
            
            <h3>What to Prepare:</h3>
            <ul>
                <li>Your portfolio or work samples</li>
                <li>Questions about the role and company</li>
                <li>Be ready to discuss your experience and skills</li>
            </ul>
            
            <p>If you need to reschedule, please contact us at least 24 hours in advance.</p>
            
            <p>We look forward to meeting you!</p>
            
            <p>Best regards,<br>
            HR Team</p>
        </body>
        </html>
        """
        
        return self.send_email(candidate['email'], subject, body)
    
    def send_salary_offer(self, candidate: Dict[str, Any], offer_amount: float, job_title: str) -> bool:
        """Send salary offer email"""
        subject = f"Job Offer - {job_title}"
        
        body = f"""
        <html>
        <body>
            <h2>Congratulations! Job Offer</h2>
            <p>Dear {candidate['name']},</p>
            
            <p>We are delighted to extend you an offer for the position of <strong>{job_title}</strong>.</p>
            
            <h3>Offer Details:</h3>
            <ul>
                <li><strong>Position:</strong> {job_title}</li>
                <li><strong>Annual Salary:</strong> ₹{offer_amount:,.2f}</li>
                <li><strong>Start Date:</strong> To be discussed</li>
            </ul>
            
            <h3>Benefits Package:</h3>
            <ul>
                <li>Health, dental, and vision insurance</li>
                <li>401(k) retirement plan with company match</li>
                <li>Paid time off and holidays</li>
                <li>Professional development opportunities</li>
            </ul>
            
            <p>Please review this offer carefully. You have <strong>5 business days</strong> to respond.</p>
            
            <p>To accept this offer, please reply to this email with "I accept" or contact us to discuss any questions.</p>
            
            <p>We are excited to have you join our team!</p>
            
            <p>Best regards,<br>
            HR Team</p>
        </body>
        </html>
        """
        
        return self.send_email(candidate['email'], subject, body)
    
    def send_counter_offer(self, candidate: Dict[str, Any], counter_offer_amount: float, job_title: str) -> bool:
        """Send counter offer email"""
        subject = f"Updated Job Offer - {job_title}"
        
        body = f"""
        <html>
        <body>
            <h2>Updated Job Offer</h2>
            <p>Dear {candidate['name']},</p>
            
            <p>Thank you for your feedback on our initial offer. We value your skills and experience, and we would like to present you with an updated offer.</p>
            
            <h3>Updated Offer Details:</h3>
            <ul>
                <li><strong>Position:</strong> {job_title}</li>
                <li><strong>Updated Annual Salary:</strong> ₹{counter_offer_amount:,.2f}</li>
                <li><strong>Start Date:</strong> To be discussed</li>
            </ul>
            
            <p>This offer reflects our commitment to bringing you on board and recognizes your valuable contributions to our team.</p>
            
            <p>Please review this updated offer. You have <strong>3 business days</strong> to respond.</p>
            
            <p>To accept this offer, please reply to this email with "I accept" or contact us to discuss any questions.</p>
            
            <p>We look forward to your response!</p>
            
            <p>Best regards,<br>
            HR Team</p>
        </body>
        </html>
        """
        
        return self.send_email(candidate['email'], subject, body)
    
    def send_rejection_email(self, candidate: Dict[str, Any], job_title: str) -> bool:
        """Send rejection email"""
        subject = f"Application Update - {job_title}"
        
        body = f"""
        <html>
        <body>
            <h2>Application Update</h2>
            <p>Dear {candidate['name']},</p>
            
            <p>Thank you for your interest in the <strong>{job_title}</strong> position and for taking the time to interview with us.</p>
            
            <p>After careful consideration, we regret to inform you that we have decided to move forward with other candidates whose qualifications more closely match our current needs.</p>
            
            <p>We were impressed by your background and experience, and we appreciate the time you spent with us during the interview process.</p>
            
            <p>We will keep your resume on file for future opportunities that may be a better fit for your skills and experience.</p>
            
            <p>We wish you the best in your job search and future endeavors.</p>
            
            <p>Best regards,<br>
            HR Team</p>
        </body>
        </html>
        """
        
        return self.send_email(candidate['email'], subject, body)
    
    def send_human_approval_request(self, job_posting: Dict[str, Any], admin_email: str) -> bool:
        """Send human approval request for job posting"""
        subject = "Job Posting Approval Required"
        
        body = f"""
        <html>
        <body>
            <h2>Job Posting Approval Required</h2>
            <p>Dear HR Manager,</p>
            
            <p>A new job posting has been generated and requires your approval before being posted to LinkedIn.</p>
            
            <h3>Job Details:</h3>
            <ul>
                <li><strong>Title:</strong> {job_posting['title']}</li>
                <li><strong>Department:</strong> {job_posting['department']}</li>
                <li><strong>Salary Range:</strong> ${job_posting['salary_range']['min']:,.2f} - ${job_posting['salary_range']['max']:,.2f}</li>
            </ul>
            
            <h3>Job Description:</h3>
            <p>{job_posting['description']}</p>
            
            <h3>Requirements:</h3>
            <ul>
                {''.join([f'<li>{req}</li>' for req in job_posting['requirements']])}
            </ul>
            
            <p>Please review this job posting and approve or request modifications.</p>
            
            <p>Best regards,<br>
            Job Automation System</p>
        </body>
        </html>
        """
        
        return self.send_email(admin_email, subject, body) 