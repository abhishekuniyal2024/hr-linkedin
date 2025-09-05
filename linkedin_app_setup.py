#!/usr/bin/env python3
"""
LinkedIn App Setup for Job Posting
"""

def show_linkedin_setup():
    """Show LinkedIn app setup instructions"""
    print("🔗 LinkedIn App Setup for Job Posting")
    print("="*50)
    
    print("📋 Step 1: Create LinkedIn Developer App")
    print("1. Go to: https://developer.linkedin.com/")
    print("2. Sign in with your LinkedIn account")
    print("3. Click 'Create App'")
    print("4. Fill in the form:")
    print("   - App name: 'Job Automation System'")
    print("   - LinkedIn Page: Select your company page")
    print("   - Privacy policy URL: Your website's privacy policy")
    print("   - App logo: Upload a logo (optional)")
    print("5. Click 'Create app'")
    
    print("\n📋 Step 2: Configure App Permissions")
    print("1. In your app dashboard, go to 'Auth' tab")
    print("2. Under 'OAuth 2.0 scopes', add these permissions:")
    print("   ✅ w_member_social (Write member social actions)")
    print("   ✅ r_liteprofile (Read basic profile)")
    print("3. Under 'Redirect URLs', add:")
    print("   http://localhost:8000/callback")
    
    print("\n📋 Step 3: Get Your Credentials")
    print("1. In the 'Auth' tab, copy:")
    print("   - Client ID")
    print("   - Client Secret")
    
    print("\n📋 Step 4: Create .env File")
    print("Create a .env file with this content:")
    print("-" * 40)
    print("LINKEDIN_CLIENT_ID=your_client_id_here")
    print("LINKEDIN_CLIENT_SECRET=your_client_secret_here")
    print("LINKEDIN_ACCESS_TOKEN=your_access_token_here")
    print("LINKEDIN_PERSON_URN=urn:li:person:your_person_id")
    print("LINKEDIN_POST_MODE=feed")
    print("MOCK_LINKEDIN_MODE=False")
    print("GROQ_API_KEY=your_groq_api_key_here")
    print("-" * 40)
    
    print("\n📋 Step 5: Get Access Token")
    print("After creating the .env file, run:")
    print("python fix_linkedin_token.py")
    print("This will help you get the access token with correct permissions.")
    
    print("\n🎯 Key Points:")
    print("• w_member_social is REQUIRED for posting")
    print("• r_liteprofile is REQUIRED for user identification")
    print("• Make sure to add the redirect URL")
    print("• The app needs to be approved by LinkedIn (usually instant)")
    
    print("\n✅ Once set up, your job descriptions will be posted to LinkedIn!")

if __name__ == "__main__":
    show_linkedin_setup()
