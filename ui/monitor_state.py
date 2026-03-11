"""
Monitor State — thread-safe singleton shared between the background
GmailMonitor thread and the Streamlit UI.

The monitor thread *writes* scan results here; Streamlit *reads* them
on each re-render.  Upload results are also recorded here so the
activity feed and timeline cover ALL analysed emails.
"""

import threading
from datetime import datetime


_lock = threading.Lock()

# ── Connection ──
connected: bool = False
polling_interval: int = 60

# ── Counters ──
emails_scanned: int = 0
threats_detected: int = 0
last_scan: str = ""

# ── Feed & Results ──
activity_feed: list[dict] = []   # [{time, message, type}, ...]
results: list[dict] = []         # full analysis dicts (synced to session_state)
processed_ids: set[str] = set()  # Gmail message IDs already analysed

# ── Timeline data (for charts) ──
timestamps: list[dict] = []      # [{datetime, score, is_threat}, ...]

ALERT_THRESHOLD: int = 70  # trigger phishing alert above this score


# ── Thread-safe mutators ──

def reset():
    """Clear all state (called on disconnect)."""
    global connected, emails_scanned, threats_detected, last_scan
    with _lock:
        connected = False
        emails_scanned = 0
        threats_detected = 0
        last_scan = ""
        activity_feed.clear()
        results.clear()
        processed_ids.clear()
        timestamps.clear()


def mark_connected(interval: int = 60):
    global connected, polling_interval
    with _lock:
        connected = True
        polling_interval = interval
        _push_event("Gmail connected — monitoring started", "info")


def _record_analysis(result: dict):
    """Shared logic to log an analysis result (must be called under _lock)."""
    global emails_scanned, threats_detected, last_scan

    emails_scanned += 1
    last_scan = datetime.now().strftime("%H:%M:%S")

    score = result.get("combined_score", 0)
    subject = result.get("subject", "(no subject)")
    sender = result.get("sender", "Unknown")
    is_threat = score >= 50

    # ── Activity feed entries ──
    _push_event(f'Email scanned: "{subject}"', "email")

    # Detected techniques
    hs = result.get("header_signals", {})
    us = result.get("url_signals", {})
    ns = result.get("nlp_signals", {})

    if hs.get("spf") in ("fail", "softfail"):
        _push_event("SPF authentication failed", "warning")
    if not hs.get("dkim_present", True):
        _push_event("DKIM signature missing", "warning")
    if hs.get("from_return_path_mismatch"):
        _push_event("Domain mismatch detected (From ≠ Return-Path)", "warning")
    if hs.get("display_name_spoofing"):
        _push_event("Authority impersonation detected", "warning")
    if us.get("shortened"):
        _push_event("Suspicious shortened URL detected", "warning")
    if us.get("suspicious_tld"):
        _push_event("Suspicious TLD detected", "warning")
    if us.get("heuristic_new_domain"):
        _push_event("Newly registered domain detected", "warning")
    if ns.get("urgency_score", 0) >= 2:
        _push_event("Urgency manipulation detected", "warning")
    if ns.get("fear_score", 0) >= 2:
        _push_event("Fear-based language detected", "warning")
    if ns.get("authority_score", 0) >= 2:
        _push_event("Authority impersonation language", "warning")

    # Risk score summary
    sev = "HIGH" if score >= 50 else ("MEDIUM" if score >= 30 else "LOW")
    _push_event(f"Risk Score: {score}% ({sev})",
                "threat" if score >= 50 else "safe")

    if is_threat:
        threats_detected += 1

    # ── Timeline data ──
    timestamps.append({
        "datetime": datetime.now(),
        "score": score,
        "is_threat": is_threat,
    })

    results.append(result)


def add_result(result: dict, msg_id: str = ""):
    """Record a completed analysis result from Gmail monitor."""
    with _lock:
        if msg_id and msg_id in processed_ids:
            return  # already seen
        if msg_id:
            processed_ids.add(msg_id)
        _record_analysis(result)


def add_upload_result(result: dict):
    """Record a completed analysis result from manual upload."""
    with _lock:
        _record_analysis(result)


def _push_event(message: str, event_type: str = "info"):
    """Append an event to the activity feed (must be called under _lock)."""
    activity_feed.append({
        "time": datetime.now().strftime("%H:%M"),
        "message": message,
        "type": event_type,
    })
    # keep last 100 events
    if len(activity_feed) > 100:
        activity_feed[:] = activity_feed[-100:]
