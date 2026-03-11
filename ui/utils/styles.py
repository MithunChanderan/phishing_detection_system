"""
PhishGuard SOC — Design Tokens and CSS Style Injection
Premium SaaS cybersecurity dashboard aesthetics based on Space Grotesk and Inter.
"""

# ═══════════════════════════════════════════════════════════════════════════ #
#  DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════════════════ #
BG          = "#0A0E1A"
SURFACE     = "#0D1117"
CARD_BG     = "rgba(255,255,255,0.04)"
CARD_BORDER = "rgba(255,255,255,0.08)"
PANEL       = "#111C34"
PANEL_LIGHT = "#162040"
GLASS       = "rgba(255,255,255,0.05)"
GLASS_BORDER= "rgba(0,212,255,0.1)"
PRIMARY     = "#00D4FF"  # Cyan
SECONDARY   = "#7C3AED"  # Purple
ALERT       = "#EF4444"  # Danger
WARNING     = "#F59E0B"  # Warning
SUCCESS     = "#10B981"  # Success
TEXT        = "#F9FAFB"  # Primary Text
TEXT_DIM    = "#9CA3AF"  # Secondary Text
TEXT_MUTED  = "#4B5563"  # Muted Text

def load_styles() -> str:
    return f"""
<style>
/* ══════════════════════════════════════════════════════
   GOOGLE FONTS
   ══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

* {{ font-family: 'Syne', sans-serif; }}
code, .mono, .nav-status, .pill {{ font-family: 'JetBrains Mono', monospace; }}

/* ══════════════════════════════════════════════════════
   GLOBAL RESETS
   ══════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {BG} !important;
    background-image: radial-gradient(circle at 15% 50%, rgba(124,58,237,0.03), transparent 25%),
                      radial-gradient(circle at 85% 30%, rgba(0,212,255,0.03), transparent 25%);
    color: {TEXT}; 
    font-family: 'JetBrains Mono', sans-serif;
}}
.stApp {{ background: transparent !important; }}
h1,h2,h3,h4,h5,h6 {{ font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }}
code, pre {{ font-family: 'JetBrains Mono', monospace !important; }}

/* ══════════════════════════════════════════════════════
   HIDE SIDEBAR
   ══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    display: none !important; width: 0 !important;
}}
[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}
header[data-testid="stHeader"] {{
    display: none !important;
}}
.stDeployButton {{ display: none !important; }}

/* ══════════════════════════════════════════════════════
   ANIMATED BG GRID
   ══════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}}

/* ══════════════════════════════════════════════════════
   TOP NAV BAR
   ══════════════════════════════════════════════════════ */
.top-nav {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 32px;
    background: rgba(13, 17, 23, 0.85); /* {SURFACE} with opacity */
    backdrop-filter: blur(12px);
    border-bottom: 1px solid {CARD_BORDER};
    position: sticky; top: 0; z-index: 999;
    margin: -1rem -1rem 0 -1rem;
}}
.nav-logo {{
    display: flex; align-items: center; gap: 12px;
}}
.nav-logo-icon {{
    display: flex; align-items: center; justify-content: center;
    width: 36px; height: 36px;
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15));
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 8px;
    color: {PRIMARY};
}}
.nav-logo-icon svg {{ width: 20px; height: 20px; fill: currentColor; }}

.nav-brand {{
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700;
    color: {TEXT}; letter-spacing: 0.5px;
}}
.nav-status {{
    display: flex; align-items: center; gap: 16px;
}}
.nav-status-item {{
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 6px;
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    font-size: 0.8rem; color: {TEXT_DIM}; font-weight: 500;
}}
.status-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}}
.status-dot.online {{ background: {SUCCESS}; box-shadow: 0 0 8px {SUCCESS}88; }}
.status-dot.offline {{ background: {TEXT_MUTED}; animation: none; }}

/* ══════════════════════════════════════════════════════
   STREAMLIT TABS → NAV STYLE
   ══════════════════════════════════════════════════════ */
div[data-testid="stTabs"] {{
    position: sticky; top: 65px; z-index: 998;
    background: rgba(10, 14, 26, 0.85); /* {BG} with opacity */
    backdrop-filter: blur(12px);
    padding: 0 24px;
    border-bottom: 1px solid {CARD_BORDER};
    margin: 0 -1rem;
}}
div[data-testid="stTabs"] > div[role="tablist"] {{
    gap: 0 !important;
    justify-content: flex-start;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 600 !important;
    color: {TEXT_DIM} !important;
    padding: 16px 20px !important;
    border: none !important; border-radius: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
    display: flex !important; align-items: center !important; gap: 8px !important;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button p {{
    display: flex; align-items: center; gap: 8px; margin: 0;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button:hover {{
    color: {TEXT} !important;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button[aria-selected="true"] {{
    color: {PRIMARY} !important;
    border-bottom: 2px solid {PRIMARY} !important;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button svg {{
    width: 16px; height: 16px; fill: currentColor;
    margin-right: -4px;
}}
div[data-testid="stTabs"] > div[role="tablist"] > button[aria-selected="true"] svg {{
    filter: drop-shadow(0 0 4px rgba(0,212,255,0.4));
}}
[data-testid="stTabsContentContainer"] {{
    padding-top: 36px !important;
}}

/* ══════════════════════════════════════════════════════
   KEYFRAME ANIMATIONS
   ══════════════════════════════════════════════════════ */
@keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes pulse-dot {{
    0%,100% {{ opacity: 1; transform: scale(1); }}
    50%     {{ opacity: 0.6; transform: scale(0.85); }}
}}

/* ══════════════════════════════════════════════════════
   HERO SECTION
   ══════════════════════════════════════════════════════ */
.hero-wrap {{
    text-align: center;
    padding: 60px 20px;
    animation: fadeSlideIn 0.5s ease backwards;
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    background: rgba(0,212,255,0.1);
    border: 1px solid rgba(0,212,255,0.2);
    font-size: 0.75rem; color: {PRIMARY}; font-weight: 600;
    margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif; font-size: 3rem; font-weight: 700;
    margin-bottom: 12px; color: {TEXT};
    text-shadow: 0 0 40px rgba(0,212,255,0.2);
}}
.hero-title span {{
    background: linear-gradient(135deg, {PRIMARY}, {SECONDARY});
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero-desc {{
    font-size: 1.1rem; color: {TEXT_DIM}; line-height: 1.6;
    max-width: 600px; margin: 0 auto 30px;
}}

/* ══════════════════════════════════════════════════════
   FEATURE CARDS
   ══════════════════════════════════════════════════════ */
.features-grid {{
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 20px; margin-top: 20px;
}}
.feature-card {{
    background: {CARD_BG};
    backdrop-filter: blur(12px);
    border: 1px solid {CARD_BORDER};
    border-radius: 16px; padding: 24px;
    position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeSlideIn 0.5s ease backwards;
    text-align: left; background-color: {SURFACE};
}}
.feature-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(0,212,255,0.4);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(0,212,255,0.05);
}}
.feat-icon-badge {{
    display: flex; align-items: center; justify-content: center;
    width: 48px; height: 48px; border-radius: 12px;
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15));
    border: 1px solid rgba(0,212,255,0.2);
    color: {PRIMARY}; margin-bottom: 16px;
}}
.feat-icon-badge svg {{ width: 24px; height: 24px; fill: currentColor; }}
.feature-card h3 {{
    font-size: 1.1rem; margin: 0 0 8px 0; color: {TEXT}; font-weight: 600;
}}
.feature-card p {{
    font-size: 0.9rem; color: {TEXT_DIM}; margin: 0 0 16px 0; line-height: 1.5;
}}
.feature-link {{
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.85rem; font-weight: 600; color: {PRIMARY};
    text-decoration: none; transition: gap 0.2s;
}}
.feature-card:hover .feature-link {{ gap: 8px; }}

/* ══════════════════════════════════════════════════════
   GLASS CONTAINER & PANELS
   ══════════════════════════════════════════════════════ */
.glass-panel {{
    background: {CARD_BG};
    backdrop-filter: blur(12px);
    border: 1px solid {CARD_BORDER};
    border-radius: 16px; padding: 24px;
    margin-bottom: 20px;
    background-color: {SURFACE};
}}

.sec-title {{
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600;
    color: {TEXT}; margin-bottom: 16px; margin-top: 0;
    display: flex; align-items: center; gap: 8px;
}}
.sec-title svg {{ width: 18px; height: 18px; fill: {TEXT_DIM}; }}

/* ══════════════════════════════════════════════════════
   PILLS / BADGES
   ══════════════════════════════════════════════════════ */
.pill {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px; border-radius: 12px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;
}}
.pill-high     {{ background: rgba(239,68,68,0.15); color: {ALERT}; border: 1px solid rgba(239,68,68,0.3); }}
.pill-medium   {{ background: rgba(245,158,11,0.15); color: {WARNING}; border: 1px solid rgba(245,158,11,0.3); }}
.pill-low      {{ background: rgba(16,185,129,0.15); color: {SUCCESS}; border: 1px solid rgba(16,185,129,0.3); }}
.pill-info     {{ background: rgba(0,212,255,0.15); color: {PRIMARY}; border: 1px solid rgba(0,212,255,0.3); }}

/* ══════════════════════════════════════════════════════
   FEED ITEMS
   ══════════════════════════════════════════════════════ */
.feed-container {{ max-height: 400px; overflow-y: auto; padding-right: 8px; }}
.feed-item {{
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 16px; border-radius: 8px;
    background: rgba(255,255,255,0.02);
    border-left: 3px solid transparent;
    margin-bottom: 8px;
    animation: slideInLeft 0.4s ease forwards;
    transition: background 0.2s;
}}
.feed-item:hover {{ background: rgba(255,255,255,0.04); }}
.feed-item.sev-high {{ border-left-color: {ALERT}; }}
.feed-item.sev-medium {{ border-left-color: {WARNING}; }}
.feed-item.sev-info {{ border-left-color: {PRIMARY}; }}

.feed-time {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    color: {TEXT_MUTED}; min-width: 60px; padding-top: 2px;
}}
.feed-content {{ flex: 1; display: flex; flex-direction: column; gap: 4px; }}
.feed-header {{ display: flex; justify-content: space-between; align-items: center; }}
.feed-msg {{ font-size: 0.85rem; color: {TEXT}; font-weight: 500; margin: 0; }}
.feed-desc {{ font-size: 0.8rem; color: {TEXT_DIM}; margin: 0; }}

/* ══════════════════════════════════════════════════════
   PAGE HEADER
   ══════════════════════════════════════════════════════ */
.page-header {{
    margin-bottom: 24px; padding-bottom: 16px;
    border-bottom: 1px solid {CARD_BORDER};
    animation: fadeSlideIn 0.4s ease backwards;
}}
.page-header h1 {{
    font-family: 'Space Grotesk', sans-serif !important; font-size: 1.8rem !important;
    font-weight: 700 !important; color: {TEXT} !important;
    margin: 0 0 4px 0 !important;
}}
.page-header p {{
    font-size: 0.95rem; color: {TEXT_DIM}; margin: 0;
}}

/* ══════════════════════════════════════════════════════
   EMPTY STATES
   ══════════════════════════════════════════════════════ */
.empty-state {{
    border: 1px dashed rgba(255,255,255,0.08);
    background: radial-gradient(ellipse at center, rgba(0,212,255,0.03) 0%, transparent 70%);
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    margin: 20px 0;
}}
.empty-icon {{ opacity: 0.3; margin-bottom: 16px; }}
.empty-title {{ font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:#f1f5f9; margin-bottom:8px; }}
.empty-desc {{ font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#475569; max-width:400px; margin:0 auto; line-height:1.6; }}

/* ══════════════════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
   ══════════════════════════════════════════════════════ */
div[data-testid="stMetricValue"] {{ font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; }}
.stButton > button {{
    background: {CARD_BG} !important; border: 1px solid {CARD_BORDER} !important;
    color: {TEXT} !important; font-family: 'JetBrains Mono', sans-serif !important; font-weight: 600 !important;
    border-radius: 8px !important; transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background: rgba(0,212,255,0.1) !important; border-color: {PRIMARY} !important;
    color: {PRIMARY} !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,0.2); }}

</style>
"""

def get_svg_icon(name: str, size: int = 16, color: str = "currentColor") -> str:
    """Returns SVG string for named icons (to replace emojis)."""
    icons = {
        "shield": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        "mail": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>',
        "activity": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
        "clock": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        "bar-chart": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
        "brain": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>',
        "settings": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
        "home": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
        "list": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>',
        "arrow-right": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'
    }
    return icons.get(name, "")
