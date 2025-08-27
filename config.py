import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "your_linkedin_client_id")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "your_linkedin_client_secret")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "your_linkedin_access_token")
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your_email@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_password")
    
    # Job posting settings
    MIN_APPLICANTS = 10
    TOP_CANDIDATES_COUNT = 5
    SALARY_RANGE_MIN = 50000
    SALARY_RANGE_MAX = 100000 