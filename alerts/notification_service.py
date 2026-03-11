"""
Notification Service — delivers alerts through multiple channels:
dashboard (session_state), email (SMTP), and Telegram.
"""

import smtplib
from email.mime.text import MIMEText

import requests

from alerts.alert_generator import Alert


class NotificationService:
    """
    Multichannel notification dispatcher.
    Each channel is optional and fails silently when not configured.
    """

    # ------------------------------------------------------------------ #
    #  Dashboard notifications (Streamlit session_state)
    # ------------------------------------------------------------------ #

    @staticmethod
    def send_dashboard_notification(alert: Alert, session_state) -> None:
        """Append the alert to the Streamlit session-state notifications list."""
        if "notifications" not in session_state:
            session_state["notifications"] = []
        session_state["notifications"].append({
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "sender": alert.sender,
            "subject": alert.subject,
        })

    # ------------------------------------------------------------------ #
    #  Email (SMTP)
    # ------------------------------------------------------------------ #

    @staticmethod
    def send_email_alert(
        alert: Alert,
        recipient: str,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: str = "",
        sender_password: str = "",
    ) -> bool:
        """Send alert as a plain-text email via SMTP. Returns True on success."""
        if not all([recipient, sender_email, sender_password]):
            return False
        try:
            msg = MIMEText(alert.message)
            msg["Subject"] = f"[Phishing Alert] {alert.severity} — {alert.subject}"
            msg["From"] = sender_email
            msg["To"] = recipient

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    #  Telegram
    # ------------------------------------------------------------------ #

    @staticmethod
    def send_telegram_alert(
        alert: Alert,
        bot_token: str = "",
        chat_id: str = "",
    ) -> bool:
        """Send alert via Telegram Bot API. Returns True on success."""
        if not all([bot_token, chat_id]):
            return False
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": alert.message, "parse_mode": "HTML"}
            resp = requests.post(url, json=payload, timeout=10)
            return resp.ok
        except Exception:
            return False
