"""
Email Fetcher — retrieves emails from Gmail via the Gmail API.

Requires a ``credentials.json`` OAuth2 client file (downloadable from
the Google Cloud Console).  On first authentication a ``token.json``
is saved so subsequent runs don't require the browser flow.
"""

import os
import base64
import email
from email import policy
from email.parser import BytesParser


class GmailFetcher:
    """
    Authenticates with the Gmail API and fetches messages as
    ``email.message.EmailMessage`` objects.
    """

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_path: str = "credentials.json",
                 token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    @classmethod
    def from_secrets(cls):
        from ingestion.secrets_helper import get_gmail_credential_paths
        credentials_path, token_path = get_gmail_credential_paths()
        return cls(credentials_path=credentials_path, token_path=token_path)

    # ------------------------------------------------------------------ #
    #  Authentication
    # ------------------------------------------------------------------ #

    def authenticate(self):
        import os
        import tempfile
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError:
            return False

        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None

        # Step 1 — Always try to load from secrets first (cloud + local)
        # This writes credentials.json and token.json to /tmp
        try:
            from ingestion.secrets_helper import get_gmail_credential_paths
            _, token_path = get_gmail_credential_paths()
        except Exception:
            # Fallback to instance token_path if secrets_helper fails
            token_path = self.token_path

        # Step 2 — Load token from the path secrets_helper just wrote
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception:
                creds = None

        # Step 3 — Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, "w") as f:
                    f.write(creds.to_json())
            except Exception:
                creds = None

        # Step 4 — If still no valid creds, check if on cloud or local
        if not creds or not creds.valid:
            # Detect Streamlit Cloud (no display/browser available)
            is_cloud = os.environ.get("HOME", "") == "/home/adminuser"

            if is_cloud:
                import streamlit as st
                st.error("""
                    ❌ Gmail token missing or expired in Streamlit Secrets.
                    
                    Fix steps:
                    1. Run the app locally: streamlit run ui/app.py
                    2. Connect Gmail in the Threat Monitoring tab
                    3. Open the generated token.json from your project root
                    4. Copy ALL contents
                    5. Go to Streamlit Cloud → App Settings → Secrets
                    6. Replace the token_json value with the copied content
                    7. Click Save — app will restart automatically
                """)
                st.stop()
            else:
                # Local — safe to open browser for OAuth
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, "w") as f:
                    f.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        self.creds = creds
        return creds is not None and creds.valid

    # ------------------------------------------------------------------ #
    #  Fetching
    # ------------------------------------------------------------------ #

    def fetch_recent(self, max_results: int = 10) -> list:
        """
        Return the most recent *max_results* **unread** messages as
        ``(gmail_msg_id, email.message.EmailMessage)`` tuples.
        """
        if self.service is None:
            return []

        results = (
            self.service.users()
            .messages()
            .list(userId="me", q="is:unread", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        parsed: list = []
        for msg_meta in messages:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_meta["id"], format="raw")
                .execute()
            )
            raw = base64.urlsafe_b64decode(msg["raw"])
            email_msg = BytesParser(policy=policy.default).parsebytes(raw)
            parsed.append((msg_meta["id"], email_msg))

        return parsed