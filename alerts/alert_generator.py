"""
Alert Generator — produces structured alerts with human-readable
security recommendations when a high-risk email is detected.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Alert:
    severity: str  # LOW / MEDIUM / HIGH / CRITICAL
    sender: str
    subject: str
    risk_score: int
    verdict: str
    attack_type: str
    message: str
    recommendations: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# --------------------------------------------------------------------------- #
#  Recommendation templates
# --------------------------------------------------------------------------- #

_RECOMMENDATIONS: dict[str, list[str]] = {
    "HIGH": [
        "Do NOT click any links or download attachments from this email.",
        "Do NOT reply or provide any personal information.",
        "Report this email to your IT security team immediately.",
        "If you already clicked a link, change your passwords right away.",
        "Mark this email as phishing in your mail client.",
    ],
    "MEDIUM": [
        "Treat this email with caution — verify the sender through a different channel.",
        "Avoid clicking links until you confirm the sender's identity.",
        "Check the sender's email address carefully for misspellings.",
        "If the email asks for sensitive data, contact the organisation directly.",
    ],
    "LOW": [
        "This email appears to be low-risk, but stay vigilant.",
        "Always double-check links before clicking.",
    ],
}


class AlertGenerator:
    """
    Creates an ``Alert`` from a completed analysis result dict.
    """

    def generate(self, analysis: dict) -> Alert:
        verdict = analysis.get("verdict", "LOW RISK")
        risk_score = analysis.get("risk_score", 0)

        if risk_score >= 75:
            severity = "CRITICAL"
        elif risk_score >= 50:
            severity = "HIGH"
        elif risk_score >= 30:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        rec_key = "HIGH" if severity in ("HIGH", "CRITICAL") else severity
        recs = list(_RECOMMENDATIONS.get(rec_key, _RECOMMENDATIONS["LOW"]))

        sender = analysis.get("sender", "Unknown")
        subject = analysis.get("subject", "(no subject)")
        attack_type = analysis.get("attack_type", "Generic Phishing")

        message = (
            f"⚠ Phishing Alert\n"
            f"Sender: {sender}\n"
            f"Risk Level: {severity}\n"
            f"Attack Type: {attack_type}\n"
            f"Recommendation: {recs[0]}"
        )

        return Alert(
            severity=severity,
            sender=sender,
            subject=subject,
            risk_score=risk_score,
            verdict=verdict,
            attack_type=attack_type,
            message=message,
            recommendations=recs,
        )
