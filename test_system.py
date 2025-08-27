#!/usr/bin/env python3
"""
Test script for the Job Automation System
This script tests the system to ensure everything works correctly.
"""

import sys
import os
from datetime import datetime
from job_automation_workflow import JobAutomationWorkflow

def test_system():
    """Test the job automation system"""
    print("🧪 Testing Job Automation System")
    print("="*50)
    
    # Test data
    employee_data = {
        "id": "test_emp_001",
        "name": "Alice Johnson",
        "position": "Data Scientist",
        "department": "Analytics",
        "salary": 95000.0,
        "last_working_day": datetime.now(),
        "reason_for_leaving": "Relocating to another city"
    }
    
    print(f"📝 Test Employee: {employee_data['name']}")
    print(f"   Position: {employee_data['position']}")
    print(f"   Department: {employee_data['department']}")
    print(f"   Salary: ${employee_data['salary']:,.2f}")
    
    try:
        # Create workflow instance
        print("\n🔄 Creating workflow instance...")
        workflow = JobAutomationWorkflow()
        print("✅ Workflow created successfully")
        
        # Run the workflow
        print("\n🚀 Running workflow...")
        final_state = workflow.run_workflow(employee_data)
        
        # Display results
        print("\n📊 Test Results:")
        print("="*30)
        
        if final_state.error_message:
            print(f"❌ Error: {final_state.error_message}")
            return False
        
        if final_state.workflow_completed:
            print("✅ Workflow completed successfully!")
        else:
            print(f"⚠️  Workflow status: {final_state.current_step}")
        
        if final_state.job_posting:
            print(f"\n📋 Job Posting Created:")
            print(f"   Title: {final_state.job_posting.title}")
            print(f"   Status: {final_state.job_posting.status}")
            print(f"   Applicants: {final_state.job_posting.applicant_count}")
        
        if final_state.candidates:
            print(f"\n👥 Candidates Processed: {len(final_state.candidates)}")
            for i, candidate in enumerate(final_state.candidates[:3], 1):
                print(f"   {i}. {candidate.name} - {candidate.status}")
        
        if final_state.selected_candidates:
            print(f"\n⭐ Top Candidates Selected: {len(final_state.selected_candidates)}")
            for i, candidate in enumerate(final_state.selected_candidates, 1):
                print(f"   {i}. {candidate.name} - {candidate.status}")
                if candidate.offer_salary:
                    print(f"      Offer: ${candidate.offer_salary:,.2f}")
        
        print(f"\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components of the system"""
    print("\n🔧 Testing Individual Components")
    print("="*40)
    
    try:
        # Test AI Service
        print("Testing AI Service...")
        from ai_service import AIService
        ai_service = AIService()
        print("✅ AI Service created")
        
        # Test LinkedIn Service
        print("Testing LinkedIn Service...")
        from linkedin_service import LinkedInService
        linkedin_service = LinkedInService()
        print("✅ LinkedIn Service created")
        
        # Test Email Service
        print("Testing Email Service...")
        from email_service import EmailService
        email_service = EmailService()
        print("✅ Email Service created")
        
        # Test Models
        print("Testing Data Models...")
        from models import Employee, JobPosting, Candidate, WorkflowState
        print("✅ Data Models imported")
        
        print("\n✅ All components tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Job Automation System - Test Suite")
    print("="*60)
    
    # Test individual components first
    if not test_individual_components():
        print("\n❌ Component tests failed. Exiting.")
        sys.exit(1)
    
    # Test the full system
    if not test_system():
        print("\n❌ System test failed. Exiting.")
        sys.exit(1)
    
    print("\n🎉 All tests passed successfully!")
    print("The Job Automation System is ready to use.")

if __name__ == "__main__":
    main() 