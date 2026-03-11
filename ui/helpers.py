"""
PhishGuard SOC — Reusable UI helper/render functions.
"""
import streamlit as st
import plotly.graph_objects as go
from ui.utils.styles import *


def render_particles():
    """Floating background particles like modern AI dashboards."""
    particles = ""
    import random
    random.seed(42)
    for i in range(18):
        size = random.randint(2, 6)
        left = random.randint(0, 100)
        delay = round(random.uniform(0, 15), 1)
        dur = random.randint(12, 28)
        particles += (
            f'<div class="particle" style="width:{size}px;height:{size}px;'
            f'left:{left}%;animation-delay:{delay}s;animation-duration:{dur}s;"></div>'
        )
    st.markdown(f'<div class="particles">{particles}</div>', unsafe_allow_html=True)


def render_spotlight():
    """Mouse-following spotlight glow on cards and panels."""
    st.markdown("""
    <style>
    /* Spotlight overlay on interactive elements */
    .feat-card, .glass {
        position: relative;
        overflow: hidden;
    }
    .feat-card::after, .glass::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.4s ease;
        background: radial-gradient(
            300px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(0,229,255,0.07),
            transparent 60%
        );
    }
    .feat-card:hover::after, .glass:hover::after {
        opacity: 1;
    }

    /* Nav items spotlight — tighter radius */
    section[data-testid="stSidebar"] .stRadio > div > label {
        position: relative;
        overflow: hidden;
    }
    section[data-testid="stSidebar"] .stRadio > div > label::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.35s ease;
        background: radial-gradient(
            150px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(0,229,255,0.10),
            transparent 60%
        );
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover::after {
        opacity: 1;
    }
    </style>

    <script>
    // Attach spotlight tracking to interactive elements
    function initSpotlight() {
        const selectors = '.feat-card, .glass, section[data-testid="stSidebar"] .stRadio > div > label';
        document.querySelectorAll(selectors).forEach(el => {
            if (el.dataset.spotlightBound) return;
            el.dataset.spotlightBound = '1';
            el.addEventListener('mousemove', e => {
                const rect = el.getBoundingClientRect();
                el.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
                el.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
            });
        });
    }
    // Run on load and re-run when Streamlit re-renders
    initSpotlight();
    const observer = new MutationObserver(() => { initSpotlight(); });
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)


def sev_class(score: int) -> str:
    if score >= 75: return "critical"
    if score >= 50: return "high"
    if score >= 30: return "medium"
    return "low"


def pill(val, true_cls="p-alert", false_cls="p-success",
         true_text="⚠ Detected", false_text="✔ Clean"):
    if isinstance(val, str):
        m = {"fail": ("FAIL", "p-alert"), "softfail": ("SOFTFAIL", "p-warn"),
             "pass": ("PASS", "p-success"), "none": ("NONE", "p-info")}
        return m.get(val, (val.upper(), "p-info"))
    return (true_text, true_cls) if val else (false_text, false_cls)


def render_gauge(score: int, title: str = "Risk Score", height: int = 270):
    colors = {"low": SUCCESS, "medium": WARNING, "high": ALERT, "critical": ALERT}
    bar = colors[sev_class(score)]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        title={"text": title, "font": {"size": 14, "color": TEXT_DIM}},
        number={"font": {"size": 56, "color": TEXT, "family": "Poppins"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED,
                     "tickfont": {"color": TEXT_DIM, "size": 11}},
            "bar": {"color": bar, "thickness": 0.3},
            "bgcolor": PANEL, "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "rgba(0,200,83,0.06)"},
                {"range": [30, 50], "color": "rgba(255,200,87,0.06)"},
                {"range": [50, 75], "color": "rgba(255,77,77,0.06)"},
                {"range": [75, 100], "color": "rgba(255,77,77,0.10)"},
            ],
        },
    ))
    fig.update_layout(height=height, margin=dict(l=24, r=24, t=36, b=8),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": TEXT})
    return fig


def render_trust_gauge(score: int, height: int = 270):
    bar = SUCCESS if score >= 50 else ALERT
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        title={"text": "Trust Score", "font": {"size": 14, "color": TEXT_DIM}},
        number={"font": {"size": 56, "color": TEXT, "family": "Poppins"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_MUTED,
                     "tickfont": {"color": TEXT_DIM, "size": 11}},
            "bar": {"color": bar, "thickness": 0.3},
            "bgcolor": PANEL, "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "rgba(255,77,77,0.06)"},
                {"range": [30, 60], "color": "rgba(255,200,87,0.06)"},
                {"range": [60, 100], "color": "rgba(0,200,83,0.06)"},
            ],
        },
    ))
    fig.update_layout(height=height, margin=dict(l=24, r=24, t=36, b=8),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": TEXT})
    return fig


def signal_card(title: str, icon: str, items: list):
    rows = ""
    for label, value, cls in items:
        rows += f'''<div class="row">
            <span class="row-label">{label}</span>
            <span class="pill {cls}">{value}</span></div>'''
    st.markdown(f'''<div class="glass">
        <div class="sec-title">{icon} {title}</div>{rows}</div>''',
        unsafe_allow_html=True)


def ml_confidence_bar(prob: float):
    pct = round(prob * 100, 1)
    color = ALERT if pct >= 60 else (WARNING if pct >= 40 else SUCCESS)
    st.markdown(f'''<div class="glass" style="padding:18px 24px;">
        <div class="sec-title">🤖 ML Phishing Confidence</div>
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="flex:1;background:{PANEL};border-radius:12px;height:32px;
                        overflow:hidden;border:1px solid {GLASS_BORDER};">
                <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{color}CC,{color});
                    border-radius:12px;display:flex;align-items:center;justify-content:center;
                    font-weight:800;font-size:0.88rem;color:#fff;min-width:60px;
                    transition:width 1s cubic-bezier(.4,0,.2,1);">{pct}%</div>
            </div>
            <span style="font-family:Poppins;font-size:1.1rem;font-weight:800;color:{color};
                         min-width:60px;">{"THREAT" if pct >= 50 else "SAFE"}</span>
        </div></div>''', unsafe_allow_html=True)


def signal_radar(hs, us, ns):
    h = sum([30 if hs.get("spf") == "fail" else (15 if hs.get("spf") == "softfail" else 0),
             0 if hs.get("dkim_present", True) else 15,
             20 if hs.get("from_return_path_mismatch") else 0,
             10 if hs.get("display_name_spoofing") else 0])
    u = sum([20 if us.get("shortened") else 0, 15 if us.get("suspicious_tld") else 0,
             10 if us.get("heuristic_new_domain") else 0])
    n = (ns.get("urgency_score", 0)*5 + ns.get("fear_score", 0)*5 +
         ns.get("authority_score", 0)*5 + (10 if ns.get("imperative_language") else 0))
    cats = ["Header Auth", "URL Intel", "NLP Behavioral"]
    vals = [min(h/75*100, 100), min(u/45*100, 100), min(n/35*100, 100)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]], fill='toself',
        fillcolor='rgba(0,229,255,0.10)', line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=8, color=PRIMARY)))
    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor="rgba(255,255,255,0.05)",
                                   tickfont=dict(color=TEXT_DIM, size=10)),
                   angularaxis=dict(gridcolor="rgba(255,255,255,0.05)",
                                    tickfont=dict(color=TEXT_DIM, size=12))),
        paper_bgcolor="rgba(0,0,0,0)", height=300,
        margin=dict(l=60, r=60, t=30, b=30), showlegend=False, font=dict(color=TEXT))
    return fig


def attack_pie(attack_type: str, confidence: str):
    types = ["Credential Harvesting", "Business Email Compromise",
             "Malware Delivery", "Invoice Scam", "Impersonation", "Generic Phishing"]
    colors = [PRIMARY, SECONDARY, ALERT, WARNING, "#FF6B9D", TEXT_MUTED]
    cv = {"High": 0.85, "Medium": 0.55, "Low": 0.30}.get(confidence, 0.30)
    values = [cv if t == attack_type else (1-cv)/(len(types)-1) for t in types]
    fig = go.Figure(go.Pie(
        labels=types, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color=BG, width=2)),
        textinfo="none", hoverinfo="label+percent"))
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color=TEXT_DIM, size=10), orientation="h",
                    yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        annotations=[dict(text=f"<b>{attack_type.split()[0]}</b>", x=0.5, y=0.5,
                          font=dict(size=13, color=PRIMARY, family="Poppins"),
                          showarrow=False)],
        font=dict(color=TEXT))
    return fig


def plain_explanation(result: dict) -> str:
    score = result["combined_score"]
    attack = result["attack_type"]
    reasons = result.get("reasons", [])
    if score >= 60:
        intro = "⚠️ **This email is highly suspicious and likely a phishing attempt.**"
    elif score >= 35:
        intro = "⚡ **This email shows some warning signs that deserve caution.**"
    else:
        intro = "✅ **This email appears to be safe**, though it's always good to stay alert."
    explanation = intro + "\n\n"
    friendly = {
        "SPF authentication failed": "The email's return address doesn't match the server that sent it.",
        "SPF softfail detected": "The email server couldn't fully verify the sender.",
        "DKIM signature missing": "The email lacks a digital seal of authenticity.",
        "From and Return-Path domain mismatch": "The reply-to address differs from the from address — a common phishing trick.",
        "Possible display-name spoofing": "The sender name might be faked.",
        "Shortened URL detected": "The email contains a shortened link hiding the real destination.",
        "Suspicious top-level domain": "A link uses an unusual domain ending (.xyz, .click).",
        "Domain appears newly registered": "A linked website was created very recently.",
        "Imperative social-engineering language": "Pushy language trying to force immediate action.",
        "Strong negative sentiment detected": "Threatening or alarming language.",
    }
    if reasons:
        explanation += "**Here's why:**\n\n"
        for r in reasons:
            explanation += f"• {friendly.get(r, r)}\n\n"
    if attack != "Generic Phishing":
        explanation += f"🎯 This appears to be a **{attack}** attack.\n\n"
    return explanation


# ═══════════════════════════════════════════════════════════════════════════ #
#  PHISHING ALERT BANNER (shown when score >= threshold)
# ═══════════════════════════════════════════════════════════════════════════ #

def render_phishing_alert(result: dict, alert_obj=None):
    """Prominent red alert banner for high-risk emails."""
    score = int(result.get("combined_score", 0))
    sender = result.get("sender", "Unknown")
    attack = result.get("attack_type", "Generic Phishing")
    recs = result.get("recommendations", [])
    rec_text = recs[0] if recs else "Do not click any links or provide credentials."

    sev = "CRITICAL" if score >= 75 else "HIGH"
    sev_cls = "critical" if score >= 75 else "high"

    st.markdown(f'''<div class="phishing-alert alert-{sev_cls}">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
            <div style="font-size:2.2rem;">🚨</div>
            <div>
                <div style="font-family:Poppins;font-size:1.3rem;font-weight:900;
                            color:{ALERT};text-transform:uppercase;letter-spacing:1.5px;">
                    ⚠ Phishing Alert — {sev}</div>
                <div style="font-size:0.85rem;color:{TEXT_DIM};margin-top:3px;">
                    Automated threat detection triggered</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px 24px;margin-bottom:16px;">
            <div class="row" style="border:none;padding:6px 0;">
                <span class="row-label">Sender</span>
                <span style="font-weight:700;color:{WARNING};font-size:0.92rem;
                             word-break:break-all;">{sender}</span></div>
            <div class="row" style="border:none;padding:6px 0;">
                <span class="row-label">Threat Type</span>
                <span class="pill p-alert">{attack}</span></div>
            <div class="row" style="border:none;padding:6px 0;">
                <span class="row-label">Risk Score</span>
                <span style="font-family:Poppins;font-weight:900;font-size:1.2rem;
                             color:{ALERT};">{score}%</span></div>
            <div class="row" style="border:none;padding:6px 0;">
                <span class="row-label">Verdict</span>
                <span class="pill p-alert">{result.get("verdict","HIGH RISK")}</span></div>
        </div>
        <div style="background:rgba(255,77,77,0.08);border:1px solid rgba(255,77,77,0.20);
                    border-radius:12px;padding:14px 18px;">
            <div style="font-size:0.78rem;color:{TEXT_MUTED};text-transform:uppercase;
                        letter-spacing:1.5px;font-weight:700;margin-bottom:8px;">
                💡 Recommendation</div>
            <div style="color:{TEXT};font-size:0.95rem;line-height:1.6;">{rec_text}</div>
        </div>
    </div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════ #
#  DETECTED PHISHING TECHNIQUES
# ═══════════════════════════════════════════════════════════════════════════ #

def render_detected_techniques(result: dict):
    """Show detected phishing techniques as tagged pills."""
    hs = result.get("header_signals", {})
    us = result.get("url_signals", {})
    ns = result.get("nlp_signals", {})
    techniques = []

    # Header checks
    if hs.get("spf") in ("fail", "softfail"):
        techniques.append(("🔓", "SPF Authentication Failure", ALERT))
    if not hs.get("dkim_present", True):
        techniques.append(("🔏", "DKIM Signature Missing", ALERT))
    if hs.get("from_return_path_mismatch"):
        techniques.append(("🔀", "Domain Mismatch", WARNING))
    if hs.get("display_name_spoofing"):
        techniques.append(("🎭", "Authority Impersonation", ALERT))

    # URL checks
    if us.get("shortened"):
        techniques.append(("🔗", "Suspicious Shortened URL", WARNING))
    if us.get("suspicious_tld"):
        techniques.append(("🌐", "Suspicious TLD", WARNING))
    if us.get("heuristic_new_domain"):
        techniques.append(("🆕", "Newly Registered Domain", WARNING))

    # NLP checks
    if ns.get("urgency_score", 0) >= 2:
        techniques.append(("⏰", "Urgency Manipulation", ALERT))
    if ns.get("fear_score", 0) >= 2:
        techniques.append(("😨", "Fear-Based Language", ALERT))
    if ns.get("authority_score", 0) >= 2:
        techniques.append(("👔", "Authority Impersonation Language", WARNING))
    if ns.get("imperative_language"):
        techniques.append(("📢", "Imperative Social Engineering", WARNING))

    if not techniques:
        st.markdown(f'''<div class="glass" style="text-align:center;padding:28px;">
            <div style="font-size:2rem;margin-bottom:8px;">✅</div>
            <div style="color:{SUCCESS};font-weight:700;">No phishing techniques detected</div>
        </div>''', unsafe_allow_html=True)
        return

    tags_html = ""
    for icon, name, color in techniques:
        tags_html += f'''<div class="technique-tag" style="--tag-color:{color};">
            <span style="font-size:1.1rem;">{icon}</span>
            <span>{name}</span>
        </div>'''

    st.markdown(f'''<div class="glass">
        <div class="sec-title">🔍 Detected Phishing Techniques
            <span class="pill p-alert" style="font-size:0.78rem;margin-left:8px;">
                {len(techniques)} found</span></div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;">{tags_html}</div>
    </div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════ #
#  THREAT TIMELINE (Plotly chart)
# ═══════════════════════════════════════════════════════════════════════════ #

def render_threat_timeline(history: list):
    """Plotly area chart showing email scans and phishing detections over time."""
    from collections import defaultdict

    if not history:
        return

    # Group by hour
    hourly_total = defaultdict(int)
    hourly_threat = defaultdict(int)

    import ui.monitor_state as ms
    for ts in ms.timestamps:
        hour_key = ts["datetime"].strftime("%H:00")
        hourly_total[hour_key] += 1
        if ts["is_threat"]:
            hourly_threat[hour_key] += 1

    if not hourly_total:
        # Fallback: use current hour for all history items
        from datetime import datetime
        now = datetime.now().strftime("%H:00")
        hourly_total[now] = len(history)
        hourly_threat[now] = sum(1 for h in history if h.get("combined_score", 0) >= 50)

    hours = sorted(hourly_total.keys())
    totals = [hourly_total[h] for h in hours]
    threats = [hourly_threat.get(h, 0) for h in hours]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=totals, mode="lines+markers",
        name="Emails Scanned",
        line=dict(color=PRIMARY, width=3, shape="spline"),
        marker=dict(size=8, color=PRIMARY),
        fill="tozeroy", fillcolor="rgba(0,229,255,0.06)"))
    fig.add_trace(go.Scatter(
        x=hours, y=threats, mode="lines+markers",
        name="Phishing Detected",
        line=dict(color=ALERT, width=3, shape="spline"),
        marker=dict(size=8, color=ALERT),
        fill="tozeroy", fillcolor="rgba(255,77,77,0.06)"))
    fig.update_layout(
        xaxis=dict(title="Hour", gridcolor="rgba(255,255,255,0.03)",
                   tickfont=dict(color=TEXT_DIM)),
        yaxis=dict(title="Count", gridcolor="rgba(255,255,255,0.03)",
                   tickfont=dict(color=TEXT_DIM)),
        height=300, margin=dict(l=50, r=20, t=10, b=50),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_DIM),
        legend=dict(font=dict(color=TEXT_DIM, size=11), orientation="h",
                    yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.markdown(f'<div class="sec-title">📈 Threat Timeline</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
