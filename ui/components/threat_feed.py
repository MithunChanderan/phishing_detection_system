import streamlit as st
import textwrap
from ui import monitor_state
from ui.utils.styles import ALERT, WARNING, PRIMARY, SUCCESS

@st.fragment(run_every=5)
def render_live_threat_feed(limit: int = 30):
    """
    Renders the live threat feed. Decorated with @st.fragment so it auto-refreshes 
    independently of the rest of the application.
    """
    # Sync monitor_state to session_state if needed, though reading directly 
    # from monitor_state.activity_feed is also fine here since @st.fragment 
    # executes inside the normal script run context.
    
    feed = monitor_state.activity_feed[-limit:]
    
    if not feed:
        st.markdown(textwrap.dedent(f"""
        <div class="empty-state" style="padding:40px 20px;">
            <div class="empty-icon" style="margin-bottom:8px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
            <div class="empty-title" style="font-size: 1rem;">No Recent Activity</div>
            <div class="empty-desc" style="font-size: 0.8rem;">Waiting for incoming monitoring events...</div>
        </div>
        """), unsafe_allow_html=True)
        return

    st.markdown('<div class="glass-panel" style="padding:20px 16px;"><div class="feed-container">', unsafe_allow_html=True)
    
    feed_html = ""
    for event in reversed(feed):
        evt_type = event.get("type", "info")
        
        severity_colors = {"critical": "#ff3c5f", "warning": "#ffb700", "safe": "#00ffa3"}
        border = severity_colors.get(event.get("severity", "safe"), "#475569")
        
        # Color & Badge mapping
        if evt_type == "threat":
            badge_class, badge_text = "pill-high", "HIGH"
        elif evt_type == "warning":
            badge_class, badge_text = "pill-medium", "WARN"
        elif evt_type == "safe":
            badge_class, badge_text = "pill-low", "SAFE"
        elif evt_type == "email":
            badge_class, badge_text = "pill-info", "INFO"
        else:
            badge_class, badge_text = "pill-info", "LOG"
            
        feed_html += textwrap.dedent(f"""
        <div class="feed-item" style="border-left: 3px solid {border};">
            <div class="feed-time">{event['time']}</div>
            <div class="feed-content">
                <div class="feed-header">
                    <span class="feed-msg">{event['message']}</span>
                    <span class="pill {badge_class}" style="font-size:0.65rem; padding: 2px 8px;">{badge_text}</span>
                </div>
            </div>
        </div>
        """)
        
    st.markdown(feed_html + '</div></div>', unsafe_allow_html=True)
