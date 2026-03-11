import streamlit as st
import plotly.graph_objects as go
from ui.utils.styles import BG, ALERT, WARNING, SUCCESS, PRIMARY, TEXT

def render_risk_gauge(score: int) -> go.Figure:
    """
    Renders a circular Plotly gauge for the combined risk score.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 42, "color": TEXT, "family": "Syne"}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#475569", tickfont=dict(color="#475569", size=10)),
            bar=dict(color="#ff3c5f" if score >= 70 else "#ffb700" if score >= 40 else "#00ffa3", thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                {"range": [0, 40],  "color": "rgba(0,255,163,0.07)"},
                {"range": [40, 70], "color": "rgba(255,183,0,0.07)"},
                {"range": [70, 100],"color": "rgba(255,60,95,0.07)"},
            ],
            threshold=dict(
                line=dict(color="#ff3c5f" if score >= 70 else "#ffb700", width=3),
                thickness=0.8, value=score
            )
        )
    ))
    fig.update_layout(
        paper_bgcolor="#030712",
        plot_bgcolor="#030712",
        font=dict(color="#e8eaf2"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=220
    )
    return fig

def render_threat_level_label(score: int):
    """
    Renders the THREAT LEVEL label below the gauge.
    """
    if score >= 70:
        level, color = "HIGH RISK", ALERT
    elif score >= 40:
        level, color = "ELEVATED RISK", WARNING
    else:
        level, color = "LOW RISK", SUCCESS

    st.markdown(f"""
    <div style="text-align: center; margin-top: -15px;">
        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5); letter-spacing: 2px; text-transform: uppercase; font-weight: 600;">Threat Level</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: {color}; margin-top: 4px; letter-spacing: 0.5px;">
            {level}
        </div>
    </div>
    """, unsafe_allow_html=True)
