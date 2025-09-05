#!/usr/bin/env python3
"""
LinkedIn API Setup Script
This script helps you set up LinkedIn API credentials for automatic posting
"""

import os
import requests
import webbrowser
from urllib.parse import urlencode

def setup_linkedin_api():
    """Setup LinkedIn API credentials"""
    print("🔗 LinkedIn API Setup for Automatic Posting")
    print("="*50)
    
    print("To enable automatic LinkedIn posting, you need to:")
    print("1. Create a LinkedIn Developer App")
    print("2. Get API credentials")
    print("3. Configure the system")
    
    print("\n📋 Step 1: Create LinkedIn Developer App")
    print("1. Go to: https://developer.linkedin.com/")
    print("2. Sign in with your LinkedIn account")
    print("3. Click 'Create App'")
    print("4. Fill in the required information:")
    print("   - App name: 'Job Automation System'")
    print("   - LinkedIn Page: Select your company page")
    print("   - Privacy policy URL: Your website's privacy policy")
    print("   - App logo: Upload a logo")
    print("5. Submit the form")
    
    print("\n📋 Step 2: Configure App Permissions")
    print("1. In your app dashboard, go to 'Auth' tab")
    print("2. Add these OAuth 2.0 scopes:")
    print("   - w_member_social (to post on behalf of user)")
    print("   - r_liteprofile (to get user profile)")
    print("3. Add redirect URL: http://localhost:8000/callback")
    
    print("\n📋 Step 3: Get Your Credentials")
    print("1. In your app dashboard, go to 'Auth' tab")
    print("2. Copy your 'Client ID' and 'Client Secret'")
    
    # Get credentials from user
    client_id = input("\nEnter your LinkedIn Client ID: ").strip()
    client_secret = input("Enter your LinkedIn Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return
    
    print("\n📋 Step 4: Get Access Token")
    print("We'll now open your browser to get the access token...")
    
    # Generate authorization URL
    redirect_uri = "http://localhost:8000/callback"
    scopes = "w_member_social r_liteprofile"
    
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scopes.replace(' ', '%20')}"
    )
    
    print(f"\n🔗 Authorization URL: {auth_url}")
    print("\n1. Click the URL above or we'll try to open it in your browser")
    print("2. Authorize the app")
    print("3. Copy the 'code' parameter from the redirect URL")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except:
        print("⚠️  Could not open browser automatically")
    
    # Get authorization code
    code = input("\nEnter the authorization code from the redirect URL: ").strip()
    
    if not code:
        print("❌ Authorization code is required!")
        return
    
    # Exchange code for access token
    print("\n🔄 Exchanging code for access token...")
    
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
            access_token = token_data.get("access_token")
            
            if access_token:
                print("✅ Access token obtained successfully!")
                
                # Get user profile to get person URN
                print("🔄 Getting user profile...")
                profile_url = "https://api.linkedin.com/v2/me"
                profile_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                
                profile_response = requests.get(profile_url, headers=profile_headers)
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    person_urn = profile_data.get("id")
                    if person_urn and not person_urn.startswith("urn:li:person:"):
                        person_urn = f"urn:li:person:{person_urn}"
                    
                    print("✅ User profile retrieved successfully!")
                    
                    # Create .env file
                    create_env_file(client_id, client_secret, access_token, person_urn)
                    
                else:
                    print(f"⚠️  Could not get user profile: {profile_response.status_code}")
                    create_env_file(client_id, client_secret, access_token, None)
            else:
                print("❌ Failed to get access token from response")
        else:
            print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")

def create_env_file(client_id, client_secret, access_token, person_urn):
    """Create .env file with LinkedIn credentials"""
    env_content = f"""# LinkedIn API Configuration
LINKEDIN_CLIENT_ID={client_id}
LINKEDIN_CLIENT_SECRET={client_secret}
LINKEDIN_ACCESS_TOKEN={access_token}
LINKEDIN_PERSON_URN={person_urn or 'urn:li:person:your_linkedin_person_id'}
LINKEDIN_POST_MODE=feed

# Disable mock mode for LinkedIn
MOCK_LINKEDIN_MODE=False

# Groq API (if not already set)
GROQ_API_KEY=your_groq_api_key_here
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("\n📋 Next Steps:")
        print("1. Make sure your GROQ_API_KEY is set in the .env file")
        print("2. Run 'python main.py' to test automatic LinkedIn posting")
        print("3. The system will now automatically post job descriptions to LinkedIn!")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("\n📋 Manual Setup:")
        print("Create a .env file with the following content:")
        print(env_content)

if __name__ == "__main__":
    setup_linkedin_api()
