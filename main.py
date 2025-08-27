#!/usr/bin/env python3
"""
Job Automation System using LangGraph and Groq API
This system automates the entire job posting and hiring process.
"""

import os
import sys
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
    
    print("✅ Environment setup complete")
    return True

def get_example_employee_data():
    """Get example employee data for testing"""
    return {
        "id": "emp_001",
        "name": "John Doe",
        "position": "Senior Software Engineer",
        "department": "Engineering",
        "salary": 85000.0,
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
                print(f"      Offer: ${candidate.offer_salary:,.2f}")

def main():
    """Main function to run the job automation system"""
    print("🚀 Job Automation System")
    print("Using LangGraph and Groq API")
    print("="*50)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Create workflow instance
    workflow = JobAutomationWorkflow()
    
    # Get employee data
    print("\nChoose input method:")
    print("1. Use example data")
    print("2. Enter custom employee data")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "2":
        employee_data = get_custom_employee_data()
    else:
        employee_data = get_example_employee_data()
        print(f"\nUsing example data for: {employee_data['name']}")
    
    # Display employee information
    print(f"\n📝 Employee Information:")
    print(f"   Name: {employee_data['name']}")
    print(f"   Position: {employee_data['position']}")
    print(f"   Department: {employee_data['department']}")
    print(f"   Salary: ${employee_data['salary']:,.2f}")
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