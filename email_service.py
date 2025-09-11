import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime, timedelta
from config import Config
import imaplib
import email
import os
from pypdf import PdfReader
import pypdfium2 as pdfium
import pytesseract
from PIL import Image

class EmailService:
    def __init__(self):
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.username = Config.EMAIL_USERNAME
        self.password = Config.EMAIL_PASSWORD
        self.mock_mode = Config.MOCK_EMAIL_MODE  # Add mock mode
        self.imap_host = getattr(Config, 'GMAIL_IMAP_HOST', 'imap.gmail.com')
    
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
    
    def send_interview_invitation(self, candidate: Dict[str, Any], job_title: str) -> bool:
        """Send congratulation email and ask for availability (template-based)"""
        subject = f"Congratulations - Next Steps for {job_title}"
        # Commented out the old inline template code below to prevent accidental use:
        # body = f"""
        # <html>...</html>
        # """
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'congratulations_ask_availability.html')
        with open(template_path, encoding='utf-8') as f:
            template = f.read()
        body = template.replace('{{ name }}', candidate['name']).replace('{{ job_title }}', job_title)
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
        """Send rejection email using template"""
        subject = f"Application Update - {job_title}"
        # Commented out the old inline template code below to prevent accidental use:
        # body = f"""
        # <html>...</html>
        # """
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'rejection_email.html')
        with open(template_path, encoding='utf-8') as f:
            template = f.read()
        body = template.replace('{{ name }}', candidate['name']).replace('{{ job_title }}', job_title)
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

    # ==============================
    # IMAP Resume Processing
    # ==============================
    def _extract_pdf_text(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            parts: List[str] = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
            text = "\n".join(parts).strip()
            if text:
                return text
        except Exception:
            pass
        # OCR fallback for scanned PDFs
        try:
            pdf = pdfium.PdfDocument(file_path)
            ocr_parts: List[str] = []
            for i in range(len(pdf)):
                page = pdf.get_page(i)
                pil_image = page.render(scale=2).to_pil()
                ocr_text = pytesseract.image_to_string(pil_image)
                if ocr_text:
                    ocr_parts.append(ocr_text)
            return "\n".join(ocr_parts)
        except Exception:
            return ""

    def fetch_resumes_from_inbox(self, since_uid: str | None = None) -> List[Dict[str, Any]]:
        """Fetch unread emails with PDF attachments and return parsed resumes.

        Returns list of {from_email, subject, filename, text}
        """
        results: List[Dict[str, Any]] = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.username, self.password)
            mail.select('inbox')

            status, data = mail.search(None, '(UNSEEN)')
            if status != 'OK':
                mail.logout()
                return results

            for num in data[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                from_email = email.utils.parseaddr(msg.get('From'))[1]
                subject = msg.get('Subject', '')

                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if not filename or not filename.lower().endswith('.pdf'):
                        continue
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    os.makedirs('inbox_resumes', exist_ok=True)
                    file_path = os.path.join('inbox_resumes', filename)
                    with open(file_path, 'wb') as f:
                        f.write(payload)
                    text = self._extract_pdf_text(file_path)
                    results.append({
                        'from_email': from_email,
                        'subject': subject,
                        'filename': filename,
                        'file_path': file_path,
                        'text': text,
                    })

            mail.logout()
        except Exception as e:
            print(f"Error fetching resumes: {e}")
        return results

    def fetch_interview_replies(self) -> List[Dict[str, Any]]:
        """Fetch unread emails that look like replies to interview scheduling.

        Returns: list of {from_email, subject, body}
        """
        messages: List[Dict[str, Any]] = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.username, self.password)
            mail.select('inbox')
            status, data = mail.search(None, '(UNSEEN)')
            if status != 'OK':
                mail.logout()
                return messages
            for num in data[0].split():
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                from_email = email.utils.parseaddr(msg.get('From'))[1]
                subject = msg.get('Subject', '')
                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == 'text/plain':
                            body_text += part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body_text = msg.get_payload(decode=True).decode(errors='ignore')
                messages.append({
                    'from_email': from_email,
                    'subject': subject,
                    'body': body_text.strip(),
                })
                # leave unread so the system can re-check if needed, or mark as seen
                try:
                    mail.store(num, '+FLAGS', '\\Seen')
                except Exception:
                    pass
            mail.logout()
        except Exception:
            return messages
        return messages

    def send_confirmation_email(self, to_email: str, confirmed_iso: str) -> bool:
        subject = "Interview Confirmed"
        body = (
            f"<html><body>"
            f"<p>Dear Candidate,</p>"
            f"<p>Your interview has been scheduled for <strong>{confirmed_iso}</strong>.</p>"
            f"<p>We look forward to speaking with you.</p>"
            f"<p>Best regards,<br>Hiring Team</p>"
            f"</body></html>"
        )
        return self.send_email(to_email, subject, body)