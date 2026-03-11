"""
PhishGuard SOC — Session State Initialization Utilities
"""

import streamlit as st
import threading
from ui import monitor_state

def init_session_state():
    """Initializes all required session state keys immediately to prevent reset crashes."""
    defaults = {
        "history": [],
        "notifications": [],
        "vt_api_key": "",
        "current_page": "🏠 Dashboard",
        "uploaded_file_bytes": None,
        "tg_token": "",
        "tg_chat": "",
        "smtp_email": "",
        "smtp_pass": "",
        "smtp_recipient": "",
        "gmail_monitor": None,
        "background_thread_running": False,
        "monitoring_started": False
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Setup the background threading loop for the Monitor polling logic
    if not st.session_state["background_thread_running"] and monitor_state.connected:
        start_background_sync_thread()

def start_background_sync_thread():
    """Starts a background thread to sync monitor_state results into session_state so st.rerun is not needed."""
    def sync_loop():
        import time
        from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx, get_script_run_ctx
        ctx = get_script_run_ctx()
        while monitor_state.connected:
            # Although the background Gmail monitor feeds to `monitor_state.results`, we need the Streamlit state to pull these continuously.
            # Using fragment run_every avoids full reruns. We simply make sure this thread exists if doing complex operations.
            # Actually, instead of a thread trying to write to st.session_state (which Streamlit actively blocks outside contexts),
            # we will securely copy monitor_state lists to session_state natively inside the @st.fragment functions on their next poll.
            time.sleep(1)

    t = threading.Thread(target=sync_loop, daemon=True)
    try:
        from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx, get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx:
            add_script_run_ctx(t, ctx)
    except Exception:
        pass
    
    t.start()
    st.session_state["background_thread_running"] = True
