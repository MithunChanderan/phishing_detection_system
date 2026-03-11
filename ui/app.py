"""
PhishGuard SOC — Security Operations Center Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Launch:  streamlit run ui/app.py
"""
import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import ui.monitor_state as monitor_state
import tempfile
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go

from dashboard.pipeline import AnalysisPipeline
from reports.report_generator import ReportGenerator
from alerts.notification_service import NotificationService
from alerts.alert_generator import AlertGenerator

# New UI Modules
from ui.utils.styles import load_styles, get_svg_icon, PRIMARY, SECONDARY, ALERT, SUCCESS, WARNING, TEXT, TEXT_DIM, TEXT_MUTED, CARD_BORDER, BG
from ui.utils.session import init_session_state
from ui.components.metric_card import metric_card
from ui.components.threat_feed import render_live_threat_feed
from ui.components.risk_gauge import render_risk_gauge, render_threat_level_label
from ui.helpers import *

def _connect_gmail(creds_file, polling: int, max_emails: int):
    import json as _j
    from ingestion.email_fetcher import GmailFetcher
    from ingestion.gmail_monitor import GmailMonitor
    from ui.utils.session import start_background_sync_thread

    if creds_file:
        cp = os.path.join(tempfile.gettempdir(), "gmail_credentials.json")
        with open(cp, "w") as f:
            _j.dump(_j.loads(creds_file.read()), f)
        fe = GmailFetcher(credentials_path=cp)
    else:
        from ingestion.secrets_helper import get_gmail_credential_paths
        try:
            credentials_path, token_path = get_gmail_credential_paths()
            fe = GmailFetcher(credentials_path=credentials_path, token_path=token_path)
        except Exception:
            st.stop()

    if not fe.authenticate():
        st.error("❌ Authentication failed.")
        return

    st.success("✅ Authenticated with Gmail!")
    pipeline = AnalysisPipeline(vt_api_key=st.session_state.vt_api_key or None)

    def process_email(msg_id: str, msg):
        try:
            result = pipeline.analyze_message(msg)
            monitor_state.add_result(result, msg_id)
        except Exception as exc:
            print(f"Pipeline error for {msg_id}: {exc}")

    monitor = GmailMonitor(fetcher=fe, interval_seconds=polling, max_emails=max_emails)
    monitor_state.mark_connected(interval=polling)
    monitor.start_monitoring(process_email)
    st.session_state["gmail_monitor"] = monitor
    st.session_state["monitoring_started"] = True
    start_background_sync_thread()
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════ #
st.set_page_config(page_title="PhishGuard SOC", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="collapsed")

# 1. Inject Styles
st.markdown(load_styles(), unsafe_allow_html=True)
if "particles_rendered" not in st.session_state:
    render_particles()
    st.session_state["particles_rendered"] = True

# 2. Session Initialization
init_session_state()

# Sync results from the background monitor to session state history
if monitor_state.connected and monitor_state.results:
    for r in list(monitor_state.results):
        st.session_state.history.append(r)
    monitor_state.results.clear()

# ── Pre-calculated stats ──
total = len(st.session_state.history)
threats = sum(1 for h in st.session_state.history if h.get("combined_score", 0) >= 50)
avg = round(sum(h.get("combined_score", 0) for h in st.session_state.history) / total, 1) if total else 0
safe = total - threats

# ═══════════════════════════════════════════════════════════════════════════ #
#  TOP NAVIGATION BAR
# ═══════════════════════════════════════════════════════════════════════════ #
_monitor_cls = "online" if monitor_state.connected else "offline"
_monitor_lbl = "Monitoring Active" if monitor_state.connected else "Monitoring Off"
_time_str = datetime.now().strftime("%H:%M")

st.markdown(f"""
<div class="top-nav">
    <div class="nav-logo">
        <div class="nav-logo-icon">{get_svg_icon("shield", 20)}</div>
        <div>
            <div class="nav-brand">PhishGuard SOC</div>
            <div style="font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px;
                        text-transform:uppercase;margin-top:1px;font-family:'JetBrains Mono',sans-serif;">Threat Intelligence Platform</div>
        </div>
    </div>
    <div class="nav-status">
        <div class="nav-status-item" style="border-color: {SUCCESS if monitor_state.connected else CARD_BORDER}">
            <span class="status-dot {_monitor_cls}"></span>{_monitor_lbl}
        </div>
        <div class="nav-status-item">
            {get_svg_icon("mail", 14, TEXT_DIM)} analyst@phishguard.io
        </div>
        <div class="nav-status-item">
            {get_svg_icon("clock", 14, TEXT_DIM)} {_time_str}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════ #
#  NAVIGATION TABS
# ═══════════════════════════════════════════════════════════════════════════ #
tabs = st.tabs([
    "Dashboard",
    "Email Analysis",
    "Threat Monitoring",
    "Threat History",
    "Analytics",
    "Machine Learning",
    "Settings",
])

# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[0]:
    # ── Hero Section ──
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            AI-Powered Cybersecurity
        </div>
        <div class="hero-title">PhishGuard <span>SOC</span></div>
        <div class="hero-desc">Real-time email threat intelligence using behavioral analysis, machine learning, and multi-engine detection. Protect users from phishing attacks before they cause damage.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── NEW: Feature Cards Grid (2x2) ──
    st.markdown('<div class="features-grid">', unsafe_allow_html=True)
    f_cols = st.columns(2)
    
    with f_cols[0]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feat-icon-badge">{get_svg_icon('mail', 24)}</div>
            <h3>Email Analysis</h3>
            <p>Upload .eml files to run a comprehensive 7-engine detection pipeline scoring headers, URLs, and NLP cues.</p>
            <a href="#" class="feature-link">Analyze Email {get_svg_icon('arrow-right', 14)}</a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="feature-card">
            <div class="feat-icon-badge">{get_svg_icon('brain', 24)}</div>
            <h3>ML Detection</h3>
            <p>12+ engineered features powering a RandomForest classifier trained on thousands of known phishing samples.</p>
            <a href="#" class="feature-link">View Model Insights {get_svg_icon('arrow-right', 14)}</a>
        </div>
        """, unsafe_allow_html=True)
        
    with f_cols[1]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feat-icon-badge">{get_svg_icon('activity', 24)}</div>
            <h3>Threat Monitoring</h3>
            <p>Connect your Workspace inbox via OAuth2 for real-time background polling and instant threat blocking.</p>
            <a href="#" class="feature-link">Setup Monitor {get_svg_icon('arrow-right', 14)}</a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="feature-card">
            <div class="feat-icon-badge">{get_svg_icon('bar-chart', 24)}</div>
            <h3>Analytics</h3>
            <p>Visualize attack distributions, gauge average risk scores, and track detection trends over time.</p>
            <a href="#" class="feature-link">View Dashboard {get_svg_icon('arrow-right', 14)}</a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div><br>', unsafe_allow_html=True)

    # ── Glassmorphism Metric Cards ──
    st.markdown(f'<div class="sec-title">{get_svg_icon("activity", 18)} Platform Metrics</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: metric_card("Scanned", str(total), get_svg_icon("mail", 24), PRIMARY)
    with m2: metric_card("Threats", str(threats), get_svg_icon("shield", 24), ALERT)
    with m3: metric_card("Safe", str(safe), get_svg_icon("shield", 24), SUCCESS)
    with m4: metric_card("Avg Score", str(avg), get_svg_icon("bar-chart", 24), WARNING)

    st.markdown('<br>', unsafe_allow_html=True)

    # ── Live Activity Feed (Using @st.fragment) ──
    st.markdown(f'<div class="sec-title">{get_svg_icon("list", 18)} Live Threat Activity Feed</div>', unsafe_allow_html=True)
    if monitor_state.connected:
        render_live_threat_feed()
    else:
        st.markdown(f"""<div class="empty-state">
        <div class="empty-icon">{get_svg_icon("activity", 32)}</div>
        <div class="empty-title">Monitoring Offline</div>
        <div class="empty-desc">Connect your Gmail inbox in the Threat Monitoring tab to see live events.</div>
        </div>""", unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(f"""
    <div style="text-align:center;margin-top:48px;padding:24px;">
        <div style="font-size:0.75rem;color:{TEXT_MUTED};letter-spacing:2px;text-transform:uppercase;font-weight:600;">Powered by</div>
        <div style="font-family:'Syne';font-size:1.2rem;font-weight:700;margin-top:6px;color:{TEXT};">PhishGuard <span style="color:{PRIMARY};">SOC</span></div>
        <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:4px;">Security Operations Center · {datetime.now().strftime("%b %d, %Y")}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: EMAIL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[1]:
    st.markdown(f"""<div class="page-header">
        <h1>Email Threat Analysis</h1>
        <p>Upload an <code style="background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:6px;
            color:{PRIMARY};">.eml</code> file for deep phishing detection</p>
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("upload", type=["eml"], label_visibility="collapsed")

    if uploaded:
        # BUG FIX: Store bytes in session_state immediately to survive any re-renders
        st.session_state['uploaded_file_bytes'] = uploaded.getvalue()

    if st.session_state.get('uploaded_file_bytes'):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
            tmp.write(st.session_state['uploaded_file_bytes'])
            eml_path = tmp.name
            
        with st.spinner("🔍 Running detection pipeline…"):
            pipeline = AnalysisPipeline(vt_api_key=st.session_state.vt_api_key or None)
            result = pipeline.analyze_file(eml_path)
            
        st.session_state.history.append(result)
        alert_obj = AlertGenerator().generate(result)
        NotificationService.send_dashboard_notification(alert_obj, st.session_state)
        monitor_state.add_upload_result(result)

        score = int(result["combined_score"])
        sev = sev_class(score)

        # ── Phishing Alert Banner ──
        if score >= monitor_state.ALERT_THRESHOLD:
            render_phishing_alert(result, alert_obj)
            
        st.markdown(f'<div class="sec-title">{get_svg_icon("shield", 18)} Threat Overview</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.plotly_chart(render_risk_gauge(score), use_container_width=True, config={"displayModeBar": False})
            render_threat_level_label(score)
            
        with c2:
            st.markdown(f"""<div class="glass-panel" style="height:100%; display:flex; flex-direction:column; justify-content:center; align-items:center;">
<div style="font-size:0.75rem;color:{TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;font-weight:700;margin-bottom:16px;">Verdict</div>
<div class="pill pill-{'high' if sev in ['high','critical'] else 'medium' if sev == 'medium' else 'low'}">{result["verdict"].upper()}</div>
<div style="display:flex; gap:32px; margin-top:32px;">
<div style="text-align:center;">
<div style="font-family:'Syne';font-weight:700;color:{TEXT};font-size:1.4rem;">{result["risk_score"]}</div>
<div style="font-size:0.7rem;color:{TEXT_MUTED};letter-spacing:1px;text-transform:uppercase;">Rule Score</div>
</div>
<div style="width:1px;background:{CARD_BORDER};"></div>
<div style="text-align:center;">
<div style="font-family:'Syne';font-weight:700;color:{TEXT};font-size:1.4rem;">{round(result["ml_phishing_probability"]*100,1)}%</div>
<div style="font-size:0.7rem;color:{TEXT_MUTED};letter-spacing:1px;text-transform:uppercase;">ML Conf</div>
</div>
</div>
</div>""", unsafe_allow_html=True)
            
        with c3:
            at = result.get("attack_type","Generic Phishing")
            ac = result.get("attack_confidence","Low")
            ai = result.get("attack_indicators",[])
            
            icon = get_svg_icon("shield", 32, PRIMARY)
            if "Credential" in at: icon = get_svg_icon("mail", 32, WARNING)
            elif "Malware" in at: icon = get_svg_icon("activity", 32, ALERT)
                
            cc = "pill-high" if ac=="High" else ("pill-medium" if ac=="Medium" else "pill-info")
            ih = "".join(f'<div style="font-size:0.85rem;color:{TEXT_DIM};padding:4px 0;">• {x}</div>' for x in ai[:4])
            
            st.markdown(f"""
            <div class="glass-panel" style="height:100%;">
                <div style="text-align:center;padding:10px 0;">
                    <div style="margin-bottom:12px;">{icon}</div>
                    <div style="font-family:'Syne';font-size:1.1rem;font-weight:700;color:{TEXT};">{at}</div>
                    <div style="margin-top:8px;margin-bottom:16px;"><span class="pill {cc}">Conf: {ac}</span></div>
                </div>
                {ih}
            </div>""", unsafe_allow_html=True)

        # Clear the uploaded bytes so another can be uploaded next time
        if st.button("Clear Scan Results"):
            st.session_state['uploaded_file_bytes'] = None
            st.rerun()

    else:
        # Empty state
        st.markdown(f"""<div class="empty-state">
            <div class="empty-icon">{get_svg_icon("mail", 32)}</div>
            <div class="empty-title">Ready to Analyze</div>
            <div class="empty-desc">Drag and drop an <code style="background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:4px;color:{PRIMARY};">.eml</code> file above to run the full 7-engine detection pipeline</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: THREAT MONITORING
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[2]:
    st.markdown(f"""<div class="page-header">
        <h1>Threat Monitoring</h1>
        <p>Connect your Gmail inbox and monitor for phishing threats in real time</p>
    </div>""", unsafe_allow_html=True)

    if monitor_state.connected:
        st.markdown(f"""
        <div class="glass-panel" style="border-left: 4px solid {SUCCESS};">
            <div style="display:flex;align-items:center;gap:14px;">
                <span class="status-dot online" style="width:12px;height:12px;"></span>
                <div>
                    <div style="font-family:'Syne';font-size:1.2rem;font-weight:700;color:{SUCCESS};">Gmail Monitor Active</div>
                    <div style="font-size:0.9rem;color:{TEXT_DIM};margin-top:2px;">
                        Polling every {monitor_state.polling_interval}s · {monitor_state.emails_scanned} scanned · {monitor_state.threats_detected} blocked
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Companion metric cards
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: metric_card("Scanned Today", str(monitor_state.emails_scanned), get_svg_icon("mail", 20), PRIMARY)
        with mc2: metric_card("Threats Blocked", str(monitor_state.threats_detected), get_svg_icon("shield", 20), ALERT)
        with mc3: metric_card("Last Scan", monitor_state.last_scan or "N/A", get_svg_icon("clock", 20), TEXT_DIM)
        with mc4: metric_card("Interval", f"{monitor_state.polling_interval}s", get_svg_icon("activity", 20), SECONDARY)
        
        st.markdown(f'<div class="sec-title">{get_svg_icon("list", 18)} Live Feed</div>', unsafe_allow_html=True)
        render_live_threat_feed(limit=15)

    else:
        st.markdown(f"""<div class="glass-panel">
        <div class="sec-title">{get_svg_icon("settings", 18)} Quick Setup</div>
        <ol style="color:{TEXT_DIM};line-height:2.4;font-size:0.95rem;">
            <li>Visit <a href="https://console.cloud.google.com/" style="color:{PRIMARY};" target="_blank">Google Cloud Console</a></li>
            <li>Create project → Enable <strong style="color:{TEXT};">Gmail API</strong></li>
            <li>Create <strong style="color:{TEXT};">OAuth 2.0</strong> credentials → Download <code style="background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:4px;color:{PRIMARY};">credentials.json</code></li>
            <li>Upload below and click Connect</li>
        </ol></div>""", unsafe_allow_html=True)
        
        # Detect if running on Streamlit Cloud
        is_cloud = "gmail_credentials" in st.secrets if hasattr(st, "secrets") else False

        if is_cloud:
            st.markdown(f"""
            <div class="glass-panel" style="border-left: 3px solid {WARNING};">
                <div style="font-weight:700; color:{TEXT}; margin-bottom:8px;">
                    Cloud Deployment Detected
                </div>
                <div style="color:{TEXT_DIM}; font-size:0.9rem; line-height:1.8;">
                    Credentials are loaded from <code>Streamlit Secrets</code>.<br>
                    No file upload needed. Click Connect below to start monitoring.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            ca, cb = st.columns(2)
            with ca: polling = st.number_input("Polling Interval (s)", 30, 600, 60)
            with cb: max_f = st.number_input("Max Emails/Check", 1, 50, 10)
            
            if st.button("🔗 Connect & Start Monitoring", use_container_width=True):
                if st.session_state.get("monitoring_started"):
                    st.info("Monitoring already running. Refresh to reconnect.")
                    st.stop()
                _connect_gmail(None, int(polling), int(max_f))
        else:
            creds = st.file_uploader("Upload credentials.json", type=["json"], key="gmail_creds")
            ca, cb = st.columns(2)
            with ca: polling = st.number_input("Polling Interval (s)", 30, 600, 60)
            with cb: max_f = st.number_input("Max Emails/Check", 1, 50, 10)
            
            if creds and st.button("🔗 Connect & Start Monitoring", use_container_width=True):
                if st.session_state.get("monitoring_started"):
                    st.info("Monitoring already running. Refresh to reconnect.")
                    st.stop()
                _connect_gmail(creds, int(polling), int(max_f))


# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: THREAT HISTORY
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[3]:
    st.markdown(f"""<div class="page-header">
        <h1>Threat History</h1>
        <p>All emails analyzed during this session</p>
    </div>""", unsafe_allow_html=True)
    
    hist = st.session_state.history
    if not hist:
        st.markdown(f"""<div class="empty-state">
            <div class="empty-icon">{get_svg_icon("list", 32)}</div>
            <div class="empty-title">No emails analyzed yet</div>
            <div class="empty-desc">Upload an email or connect Gmail to get started</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sec-title">{get_svg_icon("list", 18)} Analysis History</div>', unsafe_allow_html=True)
        for i, e in enumerate(reversed(hist)):
            idx = len(hist) - i
            score = int(e.get("combined_score", 0))
            s = sev_class(score)
            dc = {"low": SUCCESS, "medium": WARNING, "high": ALERT, "critical": ALERT}[s]
            pc = "pill-high" if s in ("high","critical") else ("pill-medium" if s=="medium" else "pill-low")
            border_color = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444", "critical": "#ef4444"}[s]
            
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.07);
                border-left: 3px solid {border_color};
                border-radius: 0 12px 12px 0;
                padding: 16px 20px;
                margin-bottom: 10px;
                transition: background 0.2s;
            ">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:14px;">
                        <div style="width:12px;height:12px;border-radius:50%;background:{dc};box-shadow:0 0 10px {dc}55;flex-shrink:0;"></div>
                        <div>
                            <div style="font-weight:600;color:{TEXT};font-size:1rem;">#{idx} — {e.get("subject","(no subject)")}</div>
                            <div style="font-size:0.8rem;color:{TEXT_DIM};margin-top:4px;">{e.get("sender","Unknown")}</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:12px;align-items:center;">
                        <span class="pill {pc}">Score: {score}</span>
                        <span class="pill pill-info" style="background:rgba(124,58,237,0.15);color:{SECONDARY};border-color:rgba(124,58,237,0.3);">{e.get("attack_type","N/A")}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[4]:
    st.markdown(f"""<div class="page-header">
        <h1>Threat Analytics</h1>
        <p>Visualize threat patterns and detection trends over time</p>
    </div>""", unsafe_allow_html=True)
    
    hist = st.session_state.history
    if not hist:
        # SAMPLE DATA FALLBACK
        st.info("💡 Showing Sample Data. Analyze real emails to see your actual metrics.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="sec-title">{get_svg_icon("activity", 18)} Threat Trend (Last 7 Days)</div>', unsafe_allow_html=True)
            fig1 = go.Figure(go.Scatter(
                x=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], y=[12, 18, 15, 29, 22, 10, 35],
                mode="lines+markers", line=dict(color=ALERT, width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(239, 68, 68, 0.05)"
            ))
            fig1.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM, family="Inter"))
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
            
        with c2:
            st.markdown(f'<div class="sec-title">{get_svg_icon("bar-chart", 18)} Threat Distribution by Type</div>', unsafe_allow_html=True)
            fig2 = go.Figure(go.Pie(
                labels=["Credential Harvesting", "Brand Impersonation", "Malware Delivery", "Extortion"],
                values=[45, 25, 20, 10], hole=0.7,
                marker=dict(colors=[ALERT, WARNING, SECONDARY, PRIMARY]),
                textinfo="percent"
            ))
            fig2.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, family="Inter"), showlegend=False)
            
            # Central Text for Donut
            fig2.add_annotation(text="Threats", x=0.5, y=0.55, font_size=12, font_color=TEXT_DIM, showarrow=False)
            fig2.add_annotation(text="142", x=0.5, y=0.45, font_size=28, font_color=TEXT, font_family="Space Grotesk", showarrow=False)
            
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    else:
        # REAL DATA
        m1, m2, m3, m4 = st.columns(4)
        with m1: metric_card("Scanned", str(len(hist)), get_svg_icon("mail", 20), PRIMARY)
        with m2: metric_card("Threats", str(threats), get_svg_icon("shield", 20), ALERT)
        with m3: metric_card("Safe", str(len(hist)-threats), get_svg_icon("shield", 20), SUCCESS)
        with m4: metric_card("Avg Score", str(avg), get_svg_icon("bar-chart", 20), WARNING)
        
        scores = [h.get("combined_score",0) for h in hist]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1,len(scores)+1)), y=scores, mode="lines+markers",
            line=dict(color=PRIMARY, width=3, shape="spline"),
            marker=dict(size=8, color=[ALERT if s>=70 else WARNING if s>=40 else SUCCESS for s in scores]),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.05)"))
        fig.update_layout(xaxis=dict(title="Email #", gridcolor=CARD_BORDER),
                          yaxis=dict(title="Risk Score", range=[0,105], gridcolor=CARD_BORDER),
                          height=320, margin=dict(l=30,r=10,t=10,b=30),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM, family="Inter"))
        
        st.markdown(f'<div class="sec-title">{get_svg_icon("activity", 18)} Risk Score Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: MACHINE LEARNING
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[5]:
    st.markdown(f"""<div class="page-header">
        <h1>Machine Learning Insights</h1>
        <p>Model performance, feature importance, and classification details</p>
    </div>""", unsafe_allow_html=True)
    try:
        from ml_detection.phishing_classifier import PhishingClassifier
        from ml_detection.feature_extractor import FeatureExtractor
        clf = PhishingClassifier()
        feat_names = FeatureExtractor.feature_names()
        if clf.model is not None and hasattr(clf.model, 'feature_importances_'):
            imp = clf.model.feature_importances_
            sorted_idx = sorted(range(len(imp)), key=lambda i: imp[i], reverse=True)
            names = [feat_names[i].replace("_"," ").title() for i in sorted_idx]
            vals = [round(imp[i]*100, 1) for i in sorted_idx]
            
            # Gradient color scale for ML bars: Top->Red, Mid->Amber, Low->Cyan
            colors = []
            for v in vals:
                if v > 15: colors.append(ALERT)
                elif v > 5: colors.append(WARNING)
                else: colors.append(PRIMARY)
                
            fig = go.Figure(go.Bar(
                x=vals, y=names, orientation="h",
                text=[f"{v}%" for v in vals], textposition="outside",
                marker=dict(color=colors)
            ))
            fig.update_layout(height=480, margin=dict(l=10,r=40,t=10,b=30),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="Importance (%)", gridcolor=CARD_BORDER),
                yaxis=dict(autorange="reversed", tickfont=dict(color=TEXT, family="Inter", size=12)),
                font=dict(color=TEXT_DIM, family="Inter"))
                
            st.markdown(f'<div class="sec-title">{get_svg_icon("brain", 18)} Feature Importance (RandomForest)</div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Model not loaded yet. Waiting for initialization.")
            
        st.markdown(f"""<div class="glass-panel" style="margin-top:20px;"><div class="sec-title">{get_svg_icon("settings", 18)} Model Details</div><div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid {CARD_BORDER};"><span style="color:{TEXT_DIM};font-size:0.9rem;">Algorithm</span><span class="pill pill-info">RandomForest</span></div><div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid {CARD_BORDER};"><span style="color:{TEXT_DIM};font-size:0.9rem;">Estimators</span><span class="pill" style="background:rgba(124,58,237,0.15);color:{SECONDARY};border:1px solid rgba(124,58,237,0.3);">150 Trees</span></div><div style="display:flex; justify-content:space-between; padding:12px 0;"><span style="color:{TEXT_DIM};font-size:0.9rem;">Training Data</span><span class="pill pill-low">Synthetic (2000 samples)</span></div></div>""", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Model file not found. Train the model first by running `python ml_detection/train.py`.")
    except AttributeError:
        st.info("ℹ️ Model loaded but not yet trained. No feature importances available.")
    except ImportError as e:
        st.error(f"❌ Missing ML dependency: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error loading ML model: {type(e).__name__}: {e}")

# ═══════════════════════════════════════════════════════════════════════════ #
#  TAB: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════ #
with tabs[6]:
    st.markdown(f"""<div class="page-header">
        <h1>Settings</h1>
        <p>Configure API keys, notification channels, and alert preferences</p>
    </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="sec-title">{get_svg_icon("shield", 18)} Integrations</div>', unsafe_allow_html=True)
        with st.container(border=True):
            vk = st.text_input("VirusTotal API Key", value=st.session_state.vt_api_key, type="password")
            if vk != st.session_state.vt_api_key:
                st.session_state.vt_api_key = vk
                st.success("API key saved.")
                
    with col2:
        st.markdown(f'<div class="sec-title">{get_svg_icon("mail", 18)} Notifications</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.text_input("Telegram Bot Token", type="password", key="tg_token")
            st.text_input("Telegram Chat ID", key="tg_chat")
