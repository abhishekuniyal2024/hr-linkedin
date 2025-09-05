#!/usr/bin/env python3
"""
Test LinkedIn Posting Functionality
"""

import os
from linkedin_service import LinkedInService
from ai_service import AIService
from models import Employee
import csv
from datetime import datetime

def test_linkedin_posting():
    """Test LinkedIn posting functionality"""
    print("🔗 Testing LinkedIn Posting")
    print("="*40)
    
    # Check configuration
    print("📋 Checking Configuration:")
    print(f"   MOCK_LINKEDIN_MODE: {os.getenv('MOCK_LINKEDIN_MODE', 'True')}")
    print(f"   LINKEDIN_ACCESS_TOKEN: {'Set' if os.getenv('LINKEDIN_ACCESS_TOKEN') and os.getenv('LINKEDIN_ACCESS_TOKEN') != 'your_linkedin_access_token' else 'Not Set'}")
    print(f"   LINKEDIN_CLIENT_ID: {'Set' if os.getenv('LINKEDIN_CLIENT_ID') and os.getenv('LINKEDIN_CLIENT_ID') != 'your_linkedin_client_id' else 'Not Set'}")
    
    # Initialize services
    linkedin_service = LinkedInService()
    ai_service = AIService()
    
    print(f"\n🔧 LinkedIn Service Mock Mode: {linkedin_service.mock_mode}")
    
    if linkedin_service.mock_mode:
        print("⚠️  LinkedIn is in MOCK mode. To enable real posting:")
        print("   1. Set MOCK_LINKEDIN_MODE=False in .env file")
        print("   2. Configure valid LinkedIn API credentials")
        print("   3. Run this test again")
    
    # Get employee data
    print("\n📝 Getting Employee Data:")
    csv_file_path = "employees2.csv"
    employees = []
    
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['salary'] = float(row['salary'])
            if row['last_working_day']:
                row['last_working_day'] = datetime.strptime(row['last_working_day'], '%Y-%m-%d')
            else:
                row['last_working_day'] = None
            row['reason_for_leaving'] = row.get('reason_for_leaving', 'Career growth opportunity')
            employees.append(row)

    # Find quitting employee
    quitting_employee = None
    for emp in employees:
        if emp['last_working_day'] is not None:
            quitting_employee = emp
            break

    if not quitting_employee:
        print("❌ No quitting employee found.")
        return

    print(f"   Employee: {quitting_employee['name']} ({quitting_employee['position']})")
    print(f"   Location: {quitting_employee['office_location']}")
    
    # Create employee object
    employee = Employee(
        id=quitting_employee['id'],
        name=quitting_employee['name'],
        position=quitting_employee['position'],
        department=quitting_employee['department'],
        salary=quitting_employee['salary'],
        last_working_day=quitting_employee['last_working_day'],
        reason_for_leaving=quitting_employee['reason_for_leaving']
    )
    
    # Generate job posting
    print("\n🤖 Generating Job Posting:")
    try:
        job_data = ai_service.generate_job_posting({
            "name": employee.name,
            "position": employee.position,
            "department": employee.department,
            "salary": employee.salary,
            "reason_for_leaving": employee.reason_for_leaving,
            "location": quitting_employee['office_location']
        })
        
        print("✅ Job posting generated successfully!")
        print(f"   Title: {job_data['title']}")
        print(f"   Location: {quitting_employee['office_location']}")
        
    except Exception as e:
        print(f"❌ Error generating job posting: {e}")
        return
    
    # Test LinkedIn posting
    print("\n📱 Testing LinkedIn Posting:")
    
    # Create job data for LinkedIn
    linkedin_job_data = {
        "title": job_data['title'],
        "description": job_data['description'],
        "requirements": job_data['requirements'],
        "salary_range": job_data['salary_range'],
        "location": quitting_employee['office_location'],
        "department": employee.department,
    }
    
    try:
        post_id = linkedin_service.post_job(linkedin_job_data)
        
        if post_id:
            print(f"✅ LinkedIn post created successfully!")
            print(f"   Post ID: {post_id}")
            
            if not linkedin_service.mock_mode:
                print("🎉 Real LinkedIn post created! Check your LinkedIn profile.")
            else:
                print("📝 Mock post created (not actually posted to LinkedIn)")
        else:
            print("❌ Failed to create LinkedIn post")
            
    except Exception as e:
        print(f"❌ Error posting to LinkedIn: {e}")
    
    print("\n" + "="*40)
    print("Test completed!")

if __name__ == "__main__":
    test_linkedin_posting()
