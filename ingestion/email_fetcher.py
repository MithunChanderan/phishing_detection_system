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

    # ------------------------------------------------------------------ #
    #  Authentication
    # ------------------------------------------------------------------ #

    def authenticate(self) -> bool:
        """
        Run the OAuth2 flow (or load an existing token).
        Returns True on success, False if dependencies are missing.
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError:
            return False

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w") as tok:
                tok.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        return True

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
