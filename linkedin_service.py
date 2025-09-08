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
            "X-Restli-Protocol-Version": "2.0.0",
            # Use a stable, active API version
            "LinkedIn-Version": "202405",
            "Content-Language": "en_US"
        }
        self.mock_mode = Config.MOCK_LINKEDIN_MODE # Add mock mode
        # Config may provide a URN. We'll normalize and also compute both forms.
        self.person_urn = getattr(Config, "LINKEDIN_PERSON_URN", None)
        self.member_urn = None
        self.post_mode = getattr(Config, "LINKEDIN_POST_MODE", "feed")

    def _ensure_person_urn(self) -> Optional[str]:
        """Ensure we have both member and person URNs; fetch from /me if missing.

        LinkedIn posting endpoints expect a member URN in the form
        "urn:li:member:<id>" when posting as a user profile. If a config
        mistakenly supplies a person URN ("urn:li:person:<id>") or a placeholder,
        we normalize/ignore it and resolve the correct member URN via /me.
        """
        # Sanitize any configured value; normalize person->member or ignore placeholders/URLs
        if isinstance(self.person_urn, str):
            candidate = self.person_urn.strip()
            # Ignore placeholder values
            if "your_linkedin_person_id" in candidate:
                candidate = ""
            # If a person URN is provided, convert to member URN
            if candidate.startswith("urn:li:person:"):
                person_id = candidate.split(":")[-1]
                # Store both forms
                self.person_urn = f"urn:li:person:{person_id}"
                self.member_urn = f"urn:li:member:{person_id}"
                return self.member_urn
            # Accept valid member URN
            if candidate.startswith("urn:li:member:"):
                member_id = candidate.split(":")[-1]
                self.member_urn = candidate
                self.person_urn = f"urn:li:person:{member_id}"
                return self.member_urn
            # Ignore if it's a URL or not a proper URN to trigger /me resolution
            if "linkedin.com" in candidate or not candidate.startswith("urn:"):
                self.person_urn = None
        try:
            me_url = f"{self.base_url}/me"
            resp = requests.get(me_url, headers={
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            })
            if resp.status_code == 200:
                data = resp.json()
                # Prefer explicit URN if present (normalize to member)
                urn = data.get("urn") or data.get("entityUrn")
                if isinstance(urn, str) and urn.startswith("urn:li:person:"):
                    person_id = urn.split(":")[-1]
                    self.person_urn = f"urn:li:person:{person_id}"
                    self.member_urn = f"urn:li:member:{person_id}"
                    return self.member_urn
                # Fallback to id and normalize to member URN
                person_id = data.get("id")
                if isinstance(person_id, str):
                    self.person_urn = f"urn:li:person:{person_id}"
                    self.member_urn = f"urn:li:member:{person_id}"
                    return self.member_urn
            else:
                print(f"Failed to fetch LinkedIn profile: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Error fetching LinkedIn profile: {str(e)}")
        return None

    def post_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Post a job to LinkedIn as a feed share or via jobs API depending on config."""
        if self.mock_mode:
            print(f"[MOCK LINKEDIN] Posting job: {job_data['title']}")
            return "mock_linkedin_job_id_123"

        if self.post_mode == "feed":
            result = self._post_job_as_feed(job_data)
            if result is None:
                # Fallback to REST Posts API if UGC fails
                print("UGC post failed; attempting fallback via /rest/posts...")
                return self._post_job_via_rest_posts(job_data)
            return result
        elif self.post_mode == "rest":
            return self._post_job_via_rest_posts(job_data)
        else:
            return self._post_job_via_jobs_api(job_data)

    def _post_job_as_feed(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Create a LinkedIn feed post (ugcPosts) on behalf of the configured person URN."""
        if not self._ensure_person_urn():
            print("LinkedIn profile not resolved. Ensure your token is valid and has w_member_social.")
            return None
        # UGC requires a person URN when posting as a member profile
        author_urn = self.person_urn or self.member_urn
        print(f"Using LinkedIn author URN: {author_urn}")

        try:
            url = f"{self.base_url}/ugcPosts"

            title = job_data.get("title", "New Job Opportunity")
            location = job_data.get("location", "Remote")
            salary = job_data.get("salary_range", {})
            salary_text = ""
            if isinstance(salary, dict) and "min" in salary and "max" in salary:
                salary_text = f"\nSalary: ₹{salary['min']:,} - ₹{salary['max']:,}"

            description = job_data.get("description", "")
            requirements = job_data.get("requirements", [])
            req_lines = "\n".join([f"- {r}" for r in requirements]) if requirements else ""

            contact_line = "\n\nTo apply, email your resume to abhishekibyte2@gmail.com"
            commentary = (
                f"We're hiring! {title} ({location}){salary_text}\n\n"
                f"About the role:\n{description}\n\n"
                f"Requirements:\n{req_lines}"
                f"{contact_line}"
            ).strip()

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": commentary[:1300]},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code in (201, 200):
                data = response.json() if response.content else {}
                post_urn = data.get("id") or data.get("urn") or data.get("entity")
                print(f"Feed post created successfully as your profile: {post_urn}")
                return post_urn or "linkedin_feed_post_created"
            else:
                print(f"Failed to create feed post: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating LinkedIn feed post: {str(e)}")
            return None

    def _post_job_via_rest_posts(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Create a LinkedIn post via the newer REST Posts API."""
        if not self._ensure_person_urn():
            print("LinkedIn profile not resolved. Ensure your token is valid and has w_member_social.")
            return None

        # REST Posts API accepts member/person; prefer member
        author_urn = self.member_urn or self.person_urn
        print(f"Using LinkedIn author URN (REST): {author_urn}")

        try:
            url = "https://api.linkedin.com/rest/posts"
            # Explicitly set a valid LinkedIn-Version
            rest_headers = dict(self.headers)
            rest_headers["LinkedIn-Version"] = "202405"

            title = job_data.get("title", "New Job Opportunity")
            location = job_data.get("location", "Remote")
            salary = job_data.get("salary_range", {})
            salary_text = ""
            if isinstance(salary, dict) and "min" in salary and "max" in salary:
                salary_text = f"\nSalary: ₹{salary['min']:,} - ₹{salary['max']:,}"

            description = job_data.get("description", "")
            requirements = job_data.get("requirements", [])
            req_lines = "\n".join([f"- {r}" for r in requirements]) if requirements else ""

            contact_line = "\n\nTo apply, email your resume to abhishekibyte2@gmail.com"
            commentary = (
                f"We're hiring! {title} ({location}){salary_text}\n\n"
                f"About the role:\n{description}\n\n"
                f"Requirements:\n{req_lines}"
                f"{contact_line}"
            ).strip()[:1300]

            payload = {
                "author": author_urn,
                "commentary": commentary,
                "visibility": "PUBLIC",
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                },
                "lifecycleState": "PUBLISHED",
                "isReshareable": True
            }

            response = requests.post(url, headers=rest_headers, json=payload)

            if response.status_code in (201, 200):
                data = response.json() if response.content else {}
                post_urn = data.get("id") or data.get("urn") or data.get("entity")
                print(f"REST post created successfully as your profile: {post_urn}")
                return post_urn or "linkedin_rest_post_created"
            else:
                print(f"Failed to create REST post: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating LinkedIn REST post: {str(e)}")
            return None

    def _post_job_via_jobs_api(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Attempt to create a job posting via LinkedIn Jobs API (requires special partner access)."""
        try:
            url = f"{self.base_url}/jobPostings"

            linkedin_job = {
                "title": job_data.get("title"),
                "description": job_data.get("description"),
                "location": job_data.get("location", "Remote"),
                "employmentStatus": "FULL_TIME",
                "seniorityLevel": "MID_SENIOR",
                "jobFunctions": ["ENGINEERING"],
                "salaryInsights": {
                    "currency": "USD",
                    "min": job_data.get("salary_range", {}).get("min"),
                    "max": job_data.get("salary_range", {}).get("max")
                }
            }

            response = requests.post(url, headers=self.headers, json=linkedin_job)

            if response.status_code in (201, 200):
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
        if self.mock_mode:
            print(f"[MOCK LINKEDIN] Getting applicants for job ID: {job_id}")
            return [
                {"id": "cand_001", "name": "Alice Smith", "email": "alice@example.com", "phone": "111-222-3333", "resume_url": "http://example.com/alice_resume.pdf", "applied_at": "2023-01-01", "status": "APPLIED", "experience_years": 7, "skills": ["Python", "Machine Learning"]},
                {"id": "cand_002", "name": "Bob Johnson", "email": "bob@example.com", "phone": "444-555-6666", "resume_url": "http://example.com/bob_resume.pdf", "applied_at": "2023-01-02", "status": "APPLIED", "experience_years": 4, "skills": ["Java", "Spring Boot"]},
                {"id": "cand_003", "name": "Charlie Brown", "email": "charlie@example.com", "phone": "777-888-9999", "resume_url": "http://example.com/charlie_resume.pdf", "applied_at": "2023-01-03", "status": "APPLIED", "experience_years": 10, "skills": ["C++", "Embedded Systems"]}
            ]

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
                        "status": app.get("status"),
                        "experience_years": 5,  # Mock data
                        "skills": ["Python", "SQL", "Cloud"] # Mock data
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
        if self.mock_mode:
            print(f"[MOCK LINKEDIN] Updating job ID: {job_id} with: {updates}")
            return True

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
        if self.mock_mode:
            print(f"[MOCK LINKEDIN] Closing job ID: {job_id}")
            return True

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
        if self.mock_mode:
            print(f"[MOCK LINKEDIN] Getting job statistics for job ID: {job_id}")
            return {"views": 100, "applications": 20, "saves": 5}

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