# Environment Configuration Template
# Copy this content to a .env file and replace the placeholder values with your actual API keys

"""
# Job Automation System Environment Variables

# Required: Groq API Key
# Get your API key from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Optional: LinkedIn API Configuration
# Get LinkedIn API credentials from https://developer.linkedin.com/
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Optional: Email SMTP Configuration
# For Gmail, you may need to use an app password instead of your regular password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password

# Job posting settings
MIN_APPLICANTS=10
TOP_CANDIDATES_COUNT=5
SALARY_RANGE_MIN=50000
SALARY_RANGE_MAX=100000

# Additional AI Services (for future expansion)
# OpenAI API Key (if you want to use OpenAI as an alternative)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (if you want to use Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google AI API Key (if you want to use Gemini)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Microsoft Azure OpenAI (if you want to use Azure OpenAI)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here

# Database Configuration (for future persistence)
DATABASE_URL=sqlite:///job_automation.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=job_automation.log
"""

def create_env_file():
    """Create a .env file with the template"""
    env_content = """# Job Automation System Environment Variables

# Required: Groq API Key
# Get your API key from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Optional: LinkedIn API Configuration
# Get LinkedIn API credentials from https://developer.linkedin.com/
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Optional: Email SMTP Configuration
# For Gmail, you may need to use an app password instead of your regular password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password

# Job posting settings
MIN_APPLICANTS=10
TOP_CANDIDATES_COUNT=5
SALARY_RANGE_MIN=50000
SALARY_RANGE_MAX=100000

# Additional AI Services (for future expansion)
# OpenAI API Key (if you want to use OpenAI as an alternative)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (if you want to use Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google AI API Key (if you want to use Gemini)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Microsoft Azure OpenAI (if you want to use Azure OpenAI)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here

# Database Configuration (for future persistence)
DATABASE_URL=sqlite:///job_automation.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=job_automation.log
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("📝 Please edit the .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file() 