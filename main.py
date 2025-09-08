#!/usr/bin/env python3
"""
Job Automation System using LangGraph and Groq API
This system automates the entire job posting and hiring process.
"""

import os
import sys
import csv
import requests
from datetime import datetime
from job_automation_workflow import JobAutomationWorkflow
from config import Config

def setup_environment():
    """Setup environment variables and check configuration"""
    print("Setting up Job Automation System...")
    
    # Check if Groq API key is set
    if Config.GROQ_API_KEY == "your_groq_api_key_here":
        print("⚠️  Warning: Please set your GROQ_API_KEY in the environment variables")
        print("   You can set it by running: export GROQ_API_KEY='your_actual_api_key'")
        print("   Or create a .env file with: GROQ_API_KEY=your_actual_api_key")
        return False
    
    # Check LinkedIn configuration
    if not Config.MOCK_LINKEDIN_MODE:
        if Config.LINKEDIN_CLIENT_ID == "your_linkedin_client_id":
            print("⚠️  Warning: LinkedIn integration requires CLIENT_ID and CLIENT_SECRET")
            print("   Set MOCK_LINKEDIN_MODE=true to use mock data")
            return False
    
    print("✅ Environment setup complete")
    return True

def get_linkedin_auth_url():
    """Generate LinkedIn OAuth URL with required scopes"""
    client_id = Config.LINKEDIN_CLIENT_ID
    redirect_uri = "http://localhost:8000/callback"
    scopes = "openid profile email w_member_social"
    
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scopes.replace(' ', '%20')}"
    )
    return auth_url

def exchange_code_for_token(code: str):
    """Exchange authorization code for access token"""
    client_id = Config.LINKEDIN_CLIENT_ID
    client_secret = Config.LINKEDIN_CLIENT_SECRET
    redirect_uri = "http://localhost:8000/callback"
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Token exchange failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error exchanging code for token: {e}")
        return None

def get_example_employee_data():
    """Get example employee data for testing"""
    return {
        "id": "emp_001",
        "name": "Abhishek Uniyal",
        "position": "Python AI Developer",
        "department": "Developer",
        "salary": 25000.0,
        "last_working_day": datetime.now(),
        "reason_for_leaving": "Career growth opportunity at another company"
    }

def get_custom_employee_data():
    """Get custom employee data from user input"""
    print("\n" + "="*50)
    print("ENTER EMPLOYEE INFORMATION")
    print("="*50)

    employee_data = {}

    employee_data["id"] = input("Employee ID: ").strip() or "emp_001"
    employee_data["name"] = input("Employee Name: ").strip() or "John Doe"
    employee_data["position"] = input("Position: ").strip() or "Software Engineer"
    employee_data["department"] = input("Department: ").strip() or "Engineering"

    while True:
        try:
            salary = input("Salary (annual): ").strip()
            employee_data["salary"] = float(salary) if salary else 75000.0
            break
        except ValueError:
            print("Please enter a valid number for salary")

    employee_data["last_working_day"] = datetime.now()
    employee_data["reason_for_leaving"] = input("Reason for leaving: ").strip() or "Career growth opportunity"

    return employee_data

def read_employee_data_from_csv(file_path: str) -> list[dict]:
    """Reads employee data from a CSV file."""
    employees = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert salary to float and last_working_day to datetime
                row['salary'] = float(row['salary'])
                if row['last_working_day']:
                    row['last_working_day'] = datetime.strptime(row['last_working_day'], '%Y-%m-%d')
                else:
                    row['last_working_day'] = None  # Set to None if empty
                row['reason_for_leaving'] = "" # Placeholder since column is removed
                employees.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return employees

def display_job_description(state):
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
                        print(f"  • Experience Level: {row.get('years_of_experience', row.get('experience_years', 'N/A'))} years")
                        print(f"  • Education: {row.get('education_level', row.get('education', 'N/A'))}")
                        if row.get('certifications'):
                            print(f"  • Certifications: {row['certifications']}")
                        if row.get('projects_handled') or row.get('projects'):
                            print(f"  • Projects Handled: {row.get('projects_handled', row.get('projects', ''))}")
                        break
        except Exception as e:
            print(f"  (Additional details not available: {e})")

def display_workflow_status(state):
    """Display the current status of the workflow"""
    print("\n" + "="*50)
    print("WORKFLOW STATUS")
    print("="*50)
    
    if state.error_message:
        print(f"❌ Error: {state.error_message}")
        return
    
    if state.workflow_completed:
        print("✅ Workflow completed successfully!")
    else:
        print(f"🔄 Current step: {state.current_step}")
    
    if state.job_posting:
        print(f"\n📋 Job Posting:")
        print(f"   Title: {state.job_posting.title}")
        print(f"   Department: {state.job_posting.department}")
        print(f"   Status: {state.job_posting.status}")
        print(f"   Applicants: {state.job_posting.applicant_count}")
        if state.job_posting.linkedin_post_id:
            print(f"   LinkedIn ID: {state.job_posting.linkedin_post_id}")
    
    if state.candidates:
        print(f"\n👥 Candidates: {len(state.candidates)} total")
        for i, candidate in enumerate(state.candidates[:3], 1):
            print(f"   {i}. {candidate.name} ({candidate.status})")
        if len(state.candidates) > 3:
            print(f"   ... and {len(state.candidates) - 3} more")
    
    if state.selected_candidates:
        print(f"\n⭐ Selected Candidates: {len(state.selected_candidates)}")
        for i, candidate in enumerate(state.selected_candidates, 1):
            print(f"   {i}. {candidate.name} - {candidate.status}")
            if candidate.offer_salary:
                print(f"      Offer: ₹{candidate.offer_salary:,.2f}")

def main():
    """Main function to run the job automation system"""
    print("🚀 Job Automation System")
    print("Using LangGraph and Groq API")
    print("="*50)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed. Please check your configuration.")
        sys.exit(1)
    
    # LinkedIn OAuth setup (if not in mock mode)
    if not Config.MOCK_LINKEDIN_MODE:
        print("\n🔗 LinkedIn Integration Setup")
        print("="*30)
        
        # Check if we have an access token
        if Config.LINKEDIN_ACCESS_TOKEN == "your_linkedin_access_token":
            print("📋 To post to LinkedIn, you need to authenticate:")
            print("1. Visit this URL to authorize:")
            auth_url = get_linkedin_auth_url()
            print(f"   {auth_url}")
            print("\n2. After authorization, LinkedIn will redirect you with a 'code' parameter")
            print("3. Enter that code below to get your access token")
            
            code = input("\nEnter the authorization code from LinkedIn: ").strip()
            if code:
                access_token = exchange_code_for_token(code)
                if access_token:
                    print(f"✅ Access token obtained successfully!")
                    print(f"   Add this to your .env file: LINKEDIN_ACCESS_TOKEN={access_token}")
                    print("   Then restart the application.")
                    sys.exit(0)
                else:
                    print("❌ Failed to get access token. Please try again.")
                    sys.exit(1)
            else:
                print("❌ No authorization code provided. Exiting.")
                sys.exit(1)
        else:
            print("✅ LinkedIn access token found in configuration")
    
    # Create workflow instance
    workflow = JobAutomationWorkflow()
    
    # Get employee data from CSV
    csv_file_path = "employees.csv"
    all_employee_data = read_employee_data_from_csv(csv_file_path)

    if not all_employee_data:
        print("\n❌ No employee data found in CSV. Exiting.")
        sys.exit(1)

    # Find the employee who is quitting (has a last_working_day)
    quitting_employee = None
    for emp in all_employee_data:
        if emp['last_working_day'] is not None:
            quitting_employee = emp
            break

    if not quitting_employee:
        print("\n❌ No quitting employee found in CSV. Exiting.")
        sys.exit(1)

    employee_data = quitting_employee
    print(f"Processing employee: {employee_data['name']} (ID: {employee_data['id']})")
    
    # Display employee information
    print(f"\n📝 Employee Information:")
    print(f"   Name: {employee_data['name']}")
    print(f"   Position: {employee_data['position']}")
    print(f"   Department: {employee_data['department']}")
    print(f"   Salary: ₹{employee_data['salary']:,.2f}")
    # Display reason for leaving only if it exists
    if employee_data.get('reason_for_leaving'):
        print(f"   Reason for leaving: {employee_data['reason_for_leaving']}")
    
    # Confirm to proceed
    print(f"\nThis will start the automated job posting and hiring process.")
    confirm = input("Proceed? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        sys.exit(0)
    
    # Run the workflow
    print(f"\n🔄 Starting job automation workflow...")
    print("This may take a few moments...")
    
    try:
        final_state = workflow.run_workflow(employee_data)
        display_workflow_status(final_state)
        
        if final_state.workflow_completed:
            print(f"\n🎉 Job automation completed successfully!")
            print(f"   - Job posted to LinkedIn")
            print(f"   - {len(final_state.candidates)} candidates processed")
            print(f"   - {len(final_state.selected_candidates)} candidates interviewed")
            print(f"   - Offers and rejections sent")
        else:
            print(f"\n⚠️  Workflow completed with issues. Check the status above.")
            
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 