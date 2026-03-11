"""
Run this script ONCE locally to generate token.json for Gmail OAuth.
After running, copy token.json contents into Streamlit Cloud Secrets.

Usage:
    python generate_token.py

Requirements:
    pip install google-auth-oauthlib
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Same scopes your app uses
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to your credentials.json — must be in project root
CREDENTIALS_PATH = "credentials.json"
TOKEN_OUTPUT_PATH = "token.json"


def main():
    # Check credentials.json exists
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"ERROR: {CREDENTIALS_PATH} not found in project root.")
        print("Download it from Google Cloud Console:")
        print("  Console → APIs & Services → Credentials → OAuth 2.0 Client → Download JSON")
        return

    print("Opening browser for Gmail authentication...")
    print("Log in with the Gmail account you want to monitor.\n")

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save token.json
    with open(TOKEN_OUTPUT_PATH, "w") as f:
        f.write(creds.to_json())

    print(f"\nSUCCESS! token.json generated at: {os.path.abspath(TOKEN_OUTPUT_PATH)}")
    print("\nNext steps:")
    print("1. Open token.json in VSCode")
    print("2. Copy ALL contents")
    print("3. Go to Streamlit Cloud → App Settings → Secrets")
    print("4. Replace token_json value with the copied contents")
    print("5. Click Save")
    print("\nDO NOT commit token.json to GitHub!")


if __name__ == "__main__":
    main()