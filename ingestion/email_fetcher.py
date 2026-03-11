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
        import json
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
        token_path = os.path.join(tempfile.gettempdir(), "token.json")

        # 1. Try loading token from temp path (written by secrets_helper)
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # 2. If token is expired but has refresh token — refresh silently
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token back to temp path
                with open(token_path, "w") as f:
                    f.write(creds.to_json())
            except Exception as e:
                creds = None

        # 3. If no valid creds and running on Streamlit Cloud — FAIL GRACEFULLY
        #    Never attempt browser OAuth flow on server
        if not creds or not creds.valid:
            try:
                import streamlit as st
                is_cloud = "gmail_credentials" in st.secrets if hasattr(st, "secrets") else False
            except Exception:
                is_cloud = False

            if is_cloud:
                import streamlit as st
                st.error("""
                    ❌ Gmail authentication failed on Streamlit Cloud.
                    Your token.json in Secrets is missing or expired.
                    Steps to fix:
                    1. Run the app locally and connect Gmail once
                    2. Copy the fresh token.json contents
                    3. Paste into Streamlit Cloud → App Settings → Secrets → token_json
                    4. Save and reboot the app
                """)
                st.stop()
            else:
                # Local only — safe to open browser
                if not os.path.exists(self.credentials_path):
                    return False
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
