#!/usr/bin/env python3
"""
Fix LinkedIn Access Token Permissions
"""

import os
import requests
import webbrowser
from urllib.parse import urlencode

def fix_linkedin_token():
    """Get a new LinkedIn access token with correct permissions"""
    print("🔧 Fixing LinkedIn Access Token Permissions")
    print("="*50)
    
    # Check current configuration
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    if not client_id or client_id == 'your_linkedin_client_id':
        print("❌ LinkedIn Client ID not configured!")
        print("Please run: python setup_linkedin.py")
        return
    
    if not client_secret or client_secret == 'your_linkedin_client_secret':
        print("❌ LinkedIn Client Secret not configured!")
        print("Please run: python setup_linkedin.py")
        return
    
    print("✅ LinkedIn credentials found")
    print(f"   Client ID: {client_id[:10]}...")
    
    print("\n📋 The issue is that your access token doesn't have the required permissions.")
    print("We need to get a new token with 'w_member_social' permission.")
    
    # Generate new authorization URL with correct scopes
    redirect_uri = "http://localhost:8000/callback"
    scopes = "w_member_social r_liteprofile"  # w_member_social is required for posting
    
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scopes.replace(' ', '%20')}"
    )
    
    print(f"\n🔗 New Authorization URL (with correct permissions):")
    print(auth_url)
    
    print("\n📋 Steps to fix:")
    print("1. Click the URL above (we'll try to open it in your browser)")
    print("2. Authorize the app with the new permissions")
    print("3. Copy the 'code' parameter from the redirect URL")
    print("4. Paste it below")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except:
        print("⚠️  Could not open browser automatically")
    
    # Get new authorization code
    code = input("\nEnter the NEW authorization code: ").strip()
    
    if not code:
        print("❌ Authorization code is required!")
        return
    
    # Exchange code for new access token
    print("\n🔄 Getting new access token with correct permissions...")
    
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
            new_access_token = token_data.get("access_token")
            
            if new_access_token:
                print("✅ New access token obtained successfully!")
                
                # Test the new token
                print("🔄 Testing new token permissions...")
                test_token(new_access_token)
                
                # Update .env file
                update_env_file(new_access_token)
                
            else:
                print("❌ Failed to get access token from response")
        else:
            print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")

def test_token(access_token):
    """Test if the new token has the required permissions"""
    try:
        # Test /me endpoint
        me_url = "https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        response = requests.get(me_url, headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            person_id = profile_data.get("id")
            print(f"✅ Token works! Person ID: {person_id}")
            return person_id
        else:
            print(f"❌ Token test failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return None

def update_env_file(new_access_token):
    """Update .env file with new access token"""
    try:
        # Read current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update or add LINKEDIN_ACCESS_TOKEN
        updated = False
        for i, line in enumerate(env_lines):
            if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                env_lines[i] = f'LINKEDIN_ACCESS_TOKEN={new_access_token}\n'
                updated = True
                break
        
        if not updated:
            env_lines.append(f'LINKEDIN_ACCESS_TOKEN={new_access_token}\n')
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        print("✅ .env file updated with new access token!")
        print("\n🎉 LinkedIn posting should now work!")
        print("Run 'python test_linkedin_posting.py' to test it.")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        print(f"\n📋 Manual update: Set LINKEDIN_ACCESS_TOKEN={new_access_token} in your .env file")

if __name__ == "__main__":
    fix_linkedin_token()
