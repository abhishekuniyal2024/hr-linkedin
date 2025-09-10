#!/usr/bin/env python3
"""
Job Automation System using LangGraph and Groq API
Unified workflow: posts JD on LinkedIn, then processes resumes from inbox.
This file is for testing the combined workflow. Original main.py and inbox_watcher.py are untouched.
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
    if Config.GROQ_API_KEY == "your_groq_api_key_here":
        print("⚠️  Warning: Please set your GROQ_API_KEY in the environment variables")
        print("   You can set it by running: export GROQ_API_KEY='your_actual_api_key'")
        print("   Or create a .env file with: GROQ_API_KEY=your_actual_api_key")
        return False
    if not Config.MOCK_LINKEDIN_MODE:
        if Config.LINKEDIN_CLIENT_ID == "your_linkedin_client_id":
            print("⚠️  Warning: LinkedIn integration requires CLIENT_ID and CLIENT_SECRET")
            print("   Set MOCK_LINKEDIN_MODE=true to use mock data")
            return False
    print("✅ Environment setup complete")
    return True

def read_employee_data_from_csv(file_path: str) -> list[dict]:
    """Reads employee data from a CSV file."""
    employees = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['salary'] = float(row['salary'])
                if row['last_working_day']:
                    row['last_working_day'] = datetime.strptime(row['last_working_day'], '%Y-%m-%d')
                else:
                    row['last_working_day'] = None
                row['reason_for_leaving'] = ""
                employees.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return employees

def display_workflow_status(state):
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
    print("🚀 Job Automation System (Unified Test)")
    print("Using LangGraph and Groq API")
    print("="*50)
    if not setup_environment():
        print("\n❌ Environment setup failed. Please check your configuration.")
        sys.exit(1)
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
    if employee_data.get('reason_for_leaving'):
        print(f"   Reason for leaving: {employee_data['reason_for_leaving']}")
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
        # Wait 5 minutes before scanning inbox for resumes (development phase)
        import time
        print("\n⏳ Waiting 5 minutes so colleagues can send resumes...")
        time.sleep(300)  # 5 minutes = 300 seconds
        print("\n📥 Scanning inbox for new resumes and processing them...")
        try:
            from inbox_watcher import run_inbox_scan
            run_inbox_scan()
        except Exception as e:
            print(f"\n⚠️  Resume processing failed: {e}")
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
