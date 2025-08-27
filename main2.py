from fastapi import FastAPI, Request
import requests

app = FastAPI()

CLIENT_ID = "86k2ybh998gtba"   # your client id
CLIENT_SECRET = "WPL_AP1.rCIKXcKW0vEdiCnx.ZRCQqA=="  # <-- your real client secret
REDIRECT_URI = "http://localhost:8000/callback"

@app.get("/")
def home():
    # Step 1: Send user to LinkedIn Auth
    linkedin_auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=w_member_social"
    )
    return {"login_url": linkedin_auth_url}

@app.get("/callback")
def callback(request: Request, code: str = None, error: str = None):
    if error:
        return {"error": error}

    # Step 2: Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)
    token_data = response.json()

    return {"token_response": token_data}
