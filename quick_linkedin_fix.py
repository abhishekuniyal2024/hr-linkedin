#!/usr/bin/env python3
"""
Quick LinkedIn Fix - Enable automatic posting
"""

import os
import subprocess
import sys

def quick_fix():
    """Quick fix for LinkedIn posting"""
    print("🚀 Quick LinkedIn Fix")
    print("="*30)
    
    print("To enable automatic LinkedIn posting in your LangGraph workflow:")
    print()
    
    print("📋 Option 1: Fix Current Token (Recommended)")
    print("Run: python fix_linkedin_token.py")
    print("This will help you get a new access token with correct permissions.")
    print()
    
    print("📋 Option 2: Complete Setup")
    print("Run: python setup_linkedin.py")
    print("This will guide you through the complete LinkedIn API setup.")
    print()
    
    print("📋 Option 3: Test Current Setup")
    print("Run: python test_linkedin_posting.py")
    print("This will test your current LinkedIn configuration.")
    print()
    
    print("📋 Option 4: Use Mock Mode (For Testing)")
    print("The system is already working in mock mode.")
    print("To see the job description generation, run: python main.py")
    print()
    
    # Check current status
    print("🔍 Current Status:")
    mock_mode = os.getenv('MOCK_LINKEDIN_MODE', 'True').lower() == 'true'
    has_token = os.getenv('LINKEDIN_ACCESS_TOKEN') and os.getenv('LINKEDIN_ACCESS_TOKEN') != 'your_linkedin_access_token'
    has_client_id = os.getenv('LINKEDIN_CLIENT_ID') and os.getenv('LINKEDIN_CLIENT_ID') != 'your_linkedin_client_id'
    
    print(f"   Mock Mode: {'ON' if mock_mode else 'OFF'}")
    print(f"   Access Token: {'Set' if has_token else 'Not Set'}")
    print(f"   Client ID: {'Set' if has_client_id else 'Not Set'}")
    
    if mock_mode:
        print("\n✅ System is working in mock mode - job descriptions are generated but not posted to LinkedIn")
    elif has_token and has_client_id:
        print("\n⚠️  LinkedIn is configured but may need permission fix")
    else:
        print("\n❌ LinkedIn needs to be configured")
    
    print("\n" + "="*30)
    print("Choose an option above to proceed!")

if __name__ == "__main__":
    quick_fix()
