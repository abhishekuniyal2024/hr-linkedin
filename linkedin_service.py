import requests
import json
from typing import List, Dict, Any, Optional
from config import Config

class LinkedInService:
    def __init__(self):
        self.access_token = Config.LINKEDIN_ACCESS_TOKEN
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def post_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Post a job to LinkedIn"""
        try:
            # LinkedIn job posting endpoint
            url = f"{self.base_url}/jobPostings"
            
            # Format job data for LinkedIn API
            linkedin_job = {
                "title": job_data["title"],
                "description": job_data["description"],
                "location": job_data.get("location", "Remote"),
                "employmentStatus": "FULL_TIME",
                "seniorityLevel": "MID_SENIOR",
                "jobFunctions": ["ENGINEERING"],  # Default, should be customized
                "salaryInsights": {
                    "currency": "USD",
                    "min": job_data["salary_range"]["min"],
                    "max": job_data["salary_range"]["max"]
                }
            }
            
            response = requests.post(url, headers=self.headers, json=linkedin_job)
            
            if response.status_code == 201:
                job_id = response.json().get("id")
                print(f"Job posted successfully with ID: {job_id}")
                return job_id
            else:
                print(f"Failed to post job: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error posting job to LinkedIn: {str(e)}")
            return None
    
    def get_applicants(self, job_id: str) -> List[Dict[str, Any]]:
        """Get applicants for a specific job posting"""
        try:
            url = f"{self.base_url}/jobPostings/{job_id}/applications"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                applications = response.json().get("elements", [])
                applicants = []
                
                for app in applications:
                    applicant = {
                        "id": app.get("id"),
                        "name": app.get("applicant", {}).get("firstName", "") + " " + app.get("applicant", {}).get("lastName", ""),
                        "email": app.get("applicant", {}).get("email"),
                        "phone": app.get("applicant", {}).get("phone"),
                        "resume_url": app.get("resume", {}).get("url"),
                        "applied_at": app.get("appliedAt"),
                        "status": app.get("status")
                    }
                    applicants.append(applicant)
                
                return applicants
            else:
                print(f"Failed to get applicants: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting applicants: {str(e)}")
            return []
    
    def update_job_posting(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing job posting"""
        try:
            url = f"{self.base_url}/jobPostings/{job_id}"
            response = requests.patch(url, headers=self.headers, json=updates)
            
            if response.status_code == 200:
                print(f"Job posting updated successfully")
                return True
            else:
                print(f"Failed to update job posting: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error updating job posting: {str(e)}")
            return False
    
    def close_job_posting(self, job_id: str) -> bool:
        """Close a job posting"""
        try:
            url = f"{self.base_url}/jobPostings/{job_id}"
            updates = {"status": "CLOSED"}
            response = requests.patch(url, headers=self.headers, json=updates)
            
            if response.status_code == 200:
                print(f"Job posting closed successfully")
                return True
            else:
                print(f"Failed to close job posting: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error closing job posting: {str(e)}")
            return False
    
    def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get statistics for a job posting"""
        try:
            url = f"{self.base_url}/jobPostings/{job_id}/statistics"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                stats = response.json()
                return {
                    "views": stats.get("views", 0),
                    "applications": stats.get("applications", 0),
                    "saves": stats.get("saves", 0)
                }
            else:
                print(f"Failed to get job statistics: {response.status_code}")
                return {"views": 0, "applications": 0, "saves": 0}
                
        except Exception as e:
            print(f"Error getting job statistics: {str(e)}")
            return {"views": 0, "applications": 0, "saves": 0}
    
    def post_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Post a job to LinkedIn"""
        try:
            # LinkedIn job posting endpoint
            url = f"{self.base_url}/jobPostings"
            
            # Format job data for LinkedIn API
            linkedin_job = {
                "title": job_data["title"],
                "description": job_data["description"],
                "location": job_data.get("location", "Remote"),
                "employmentStatus": "FULL_TIME",
                "seniorityLevel": "MID_SENIOR",
                "jobFunctions": ["ENGINEERING"],  # Default, should be customized
                "salaryInsights": {
                    "currency": "USD",
                    "min": job_data["salary_range"]["min"],
                    "max": job_data["salary_range"]["max"]
                }
            }
            
            response = requests.post(url, headers=self.headers, json=linkedin_job)
            
            if response.status_code == 201:
                job_id = response.json().get("id")
                print(f"Job posted successfully with ID: {job_id}")
                return job_id
            else:
                print(f"Failed to post job: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error posting job to LinkedIn: {str(e)}")
            return None 