import streamlit as st
import textwrap
from ui.utils.styles import TEXT_MUTED, PRIMARY, ALERT, WARNING, SUCCESS

def metric_card(label, value, icon_svg, color):
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-top: 2px solid {color};
        border-radius: 14px;
        padding: 20px;
        transition: border-color 0.3s;
        position: relative;
        overflow: hidden;
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem;
                            color:#475569; text-transform:uppercase; letter-spacing:0.1em;
                            margin-bottom:10px;">{label}</div>
                <div style="font-family:'Syne',sans-serif; font-size:2rem;
                            font-weight:800; color:{color}; letter-spacing:-0.04em;
                            line-height:1;">{value}</div>
            </div>
            <div style="opacity:0.4;">{icon_svg}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
