LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;1,14..32,400&display=swap');
:root {
    --bg: #F9FAFB;
    --surface: #FFFFFF;
    --surface-2: #F3F4F6;
    --border: #E5E7EB;
    --border-focus: #4D7C6F;
    --text: #111827;
    --text-2: #374151;
    --text-muted: #6B7280;
    --accent: #3D7A6B;
    --accent-hover: #2E6357;
    --accent-light: #EAF3F1;
    --accent-mid: #B2D4CE;
    --green-chip: #D1FAE5;
    --green-chip-text: #065F46;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.10), 0 4px 10px rgba(0,0,0,0.04);
    --radius-sm: 8px;
    --radius: 12px;
    --radius-lg: 16px;
    --font: 'Inter', -apple-system, system-ui, sans-serif;
    --transition: all 0.2s ease-in-out;
}
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"], .main {
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    -webkit-font-smoothing: antialiased;
}

/* Force the sidebar toggle button to be visible no matter what Streamlit version */
header, [data-testid="stHeader"] {
    visibility: visible !important;
    background: transparent !important;
}
header button, [data-testid="stHeader"] button, [data-testid*="collapsedControl"], [data-testid*="SidebarToggle"] {
    visibility: visible !important;
    display: inline-flex !important;
    z-index: 999999 !important;
    opacity: 1 !important;
    color: var(--accent) !important;
}
header svg, [data-testid="stHeader"] svg, [data-testid*="collapsedControl"] svg {
    stroke: var(--accent) !important;
}

/* Force the sidebar itself to remain open permanently and on-screen */
.stSidebar, [data-testid="stSidebar"], section[data-testid="stSidebar"], div[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    display: flex !important;
    visibility: visible !important;
    transform: translateX(0) !important;
    margin-left: 0 !important;
    left: 0 !important;
    right: auto !important;
    top: 0 !important;
    bottom: 0 !important;
    position: fixed !important;
    width: 336px !important;
    min-width: 336px !important;
    max-width: 336px !important;
    height: 100vh !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

#MainMenu, footer { visibility: hidden; }

.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1080px !important;
    background: var(--bg) !important;
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}
[data-testid="baseButton-header"] {
    color: var(--text) !important;
    fill: var(--text) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-2) !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    padding: 9px 12px !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-light) !important;
    color: var(--accent) !important;
    border-color: var(--accent-mid) !important;
    transform: translateX(4px) !important;
}
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
    background: var(--accent-light) !important;
    color: var(--accent) !important;
    border-color: var(--accent-mid) !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"]:hover {
    transform: none !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stTextInput label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 0.75rem 0 !important;
}
.app-wordmark {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.25rem 0 1rem;
}
.app-wordmark-icon {
    width: 36px;
    height: 36px;
    background: var(--accent);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.app-wordmark-text {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text) !important;
    line-height: 1.2;
}
.app-wordmark-sub {
    font-size: 0.7rem;
    color: var(--text-muted) !important;
    font-weight: 400;
}
.nav-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-muted) !important;
    padding: 0 0 6px;
    margin-top: 0.25rem;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: var(--transition);
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-2) !important;
    margin-bottom: 2px;
    border: 1px solid transparent;
    text-decoration: none;
}
.nav-item:hover {
    background: var(--accent-light);
    color: var(--accent) !important;
    border-color: var(--accent-mid);
    transform: translateX(4px);
}
.nav-item.active {
    background: var(--accent-light);
    color: var(--accent) !important;
    border-color: var(--accent-mid);
    font-weight: 600;
}
.nav-item svg { flex-shrink: 0; color: inherit; }
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.25rem !important;
    transition: var(--transition) !important;
    font-family: var(--font) !important;
    letter-spacing: 0.01em !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.btn-ghost {
    background: transparent !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent-mid) !important;
    box-shadow: none !important;
}
.btn-ghost:hover { background: var(--accent-light) !important; }
.stTextInput > div > input,
.stTextArea > div > textarea,
.stSelectbox > div > div {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
    transition: var(--transition) !important;
}
.stTextInput > div > input:focus,
.stTextArea > div > textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(61,122,107,0.12) !important;
    outline: none !important;
    transform: scale(1.01);
}
.stProgress > div > div > div {
    background: var(--accent) !important;
    border-radius: 999px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-2) !important;
    border-radius: var(--radius-sm) !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
    font-size: 0.875rem !important;
    transition: var(--transition) !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--accent) !important;
    background: rgba(255,255,255,0.5) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    background: var(--surface) !important;
    transition: var(--transition) !important;
}
[data-testid="stExpander"]:hover { border-color: var(--accent-mid) !important; }
.eco-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.875rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.eco-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
    border-color: var(--accent-mid);
}
.eco-card-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.5rem;
}
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.metric-card:hover {
    border-color: var(--accent-mid);
    box-shadow: var(--shadow-md);
    transform: scale(1.02);
}
.metric-icon {
    width: 40px;
    height: 40px;
    background: var(--accent-light);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.75rem;
    color: var(--accent);
}
.metric-value {
    font-size: 1.875rem;
    font-weight: 800;
    color: var(--accent);
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
    margin-top: 0.3rem;
}
.tip-banner {
    background: var(--accent-light);
    border: 1px solid var(--accent-mid);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 0.875rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}
.tip-banner-icon { flex-shrink: 0; margin-top: 1px; color: var(--accent); }
.tip-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 3px;
}
.tip-text {
    font-size: 0.875rem;
    color: var(--text-2);
    line-height: 1.55;
}
.app-header {
    padding: 0.5rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 14px;
}
.app-header-icon {
    width: 48px;
    height: 48px;
    background: var(--accent);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(61,122,107,0.25);
    color: #fff;
}
.app-title {
    font-size: 1.625rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1.15;
}
.app-subtitle { font-size: 0.825rem; color: var(--text-muted); margin-top: 2px; }
.chat-viewport {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    min-height: 120px;
    box-shadow: var(--shadow-sm);
}
.msg-row-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.5rem 0;
    animation: msgIn 0.22s ease-out both;
}
.msg-row-bot {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 10px;
    margin: 0.5rem 0;
    animation: msgIn 0.22s ease-out both;
}
.bot-avatar {
    width: 32px;
    height: 32px;
    background: var(--accent);
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
    color: #fff;
}
.bubble-user {
    background: var(--accent);
    color: #ffffff;
    border-radius: 16px 16px 4px 16px;
    padding: 0.7rem 1rem;
    max-width: 72%;
    font-size: 0.9rem;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(61,122,107,0.22);
}
.bubble-bot {
    background: var(--surface);
    color: var(--text);
    border-radius: 4px 16px 16px 16px;
    padding: 0.7rem 1rem;
    max-width: 78%;
    font-size: 0.9rem;
    line-height: 1.6;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
}
.bubble-bot p { margin: 0 0 0.4em; }
.bubble-bot ul, .bubble-bot ol { padding-left: 1.25em; margin: 0.3em 0; }
.bubble-bot li { margin-bottom: 0.2em; }
.bubble-bot strong { color: var(--accent); }
.bubble-meta {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.4rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.bubble-meta-user { color: rgba(255,255,255,0.65); justify-content: flex-end; }
.source-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--accent-light);
    color: var(--accent);
    border: 1px solid var(--accent-mid);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-weight: 500;
    margin: 2px 3px 2px 0;
    line-height: 1.6;
}
.thinking-dots {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 4px 4px;
}
.thinking-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent-mid);
    display: inline-block;
    animation: dotBounce 1.2s infinite ease-in-out both;
}
.thinking-dots span:nth-child(1) { animation-delay: 0s; }
.thinking-dots span:nth-child(2) { animation-delay: 0.18s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.36s; }
.section-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.01em;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent-light);
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header-icon {
    width: 30px;
    height: 30px;
    background: var(--accent-light);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: var(--accent);
}
.score-badge {
    display: inline-block;
    font-size: 3rem;
    font-weight: 800;
    padding: 0.5rem 1.5rem;
    border-radius: var(--radius);
    letter-spacing: -0.02em;
    line-height: 1;
}
.score-A-plus { background: #D1FAE5; color: #065F46; border: 2px solid #6EE7B7; }
.score-A      { background: #ECFDF5; color: #047857; border: 2px solid #A7F3D0; }
.score-B      { background: #FEF9C3; color: #854D0E; border: 2px solid #FDE047; }
.score-C      { background: #FFF7ED; color: #9A3412; border: 2px solid #FDBA74; }
.score-D      { background: #FEF2F2; color: #991B1B; border: 2px solid #FCA5A5; }
.scheme-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.scheme-card:hover {
    border-color: var(--accent-mid);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.scheme-tag {
    background: var(--accent-light);
    color: var(--accent);
    border: 1px solid var(--accent-mid);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.scheme-name {
    font-weight: 700;
    font-size: 0.9375rem;
    color: var(--text);
    margin-bottom: 0.25rem;
}
.scheme-desc { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem; }
.scheme-benefit { font-size: 0.85rem; color: var(--accent); font-weight: 500; }
.scheme-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: var(--accent) !important;
    font-size: 0.8rem;
    font-weight: 600;
    text-decoration: none;
    margin-top: 0.5rem;
    transition: var(--transition);
}
.scheme-link:hover {
    color: var(--accent-hover) !important;
    text-decoration: underline;
}
.sidebar-footer {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-align: center;
    padding: 0.5rem 0;
    line-height: 1.6;
}
.sugg-btn-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 1rem; }
.sugg-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-2);
    cursor: pointer;
    transition: var(--transition);
    display: inline-block;
}
.sugg-pill:hover {
    background: var(--accent-light);
    border-color: var(--accent-mid);
    color: var(--accent);
    transform: translateY(-1px);
}
.chat-input-row {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 6px 8px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.chat-input-row:focus-within {
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px rgba(61,122,107,0.1);
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22C55E;
    display: inline-block;
    box-shadow: 0 0 0 2px rgba(34,197,94,0.25);
}
@keyframes msgIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes dotBounce {
    0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
    40%            { transform: scale(1.1); opacity: 1; }
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateX(-8px); }
    to   { opacity: 1; transform: translateX(0); }
}
@media (max-width: 768px) {
    .main .block-container { padding: 1rem 1rem 2rem !important; }
    .bubble-user, .bubble-bot { max-width: 92%; }
    .app-title { font-size: 1.25rem; }
    .sugg-btn-row { gap: 5px; }
}
</style>
"""
DARK_CSS = LIGHT_CSS \
    .replace("--bg: #F9FAFB;", "--bg: #0F1712;") \
    .replace("--surface: #FFFFFF;", "--surface: #1A2620;") \
    .replace("--surface-2: #F3F4F6;", "--surface-2: #1F2E29;") \
    .replace("--border: #E5E7EB;", "--border: #2D3E38;") \
    .replace("--border-focus: #4D7C6F;", "--border-focus: #5A9E8E;") \
    .replace("--text: #111827;", "--text: #F3F4F6;") \
    .replace("--text-2: #374151;", "--text-2: #D1D5DB;") \
    .replace("--text-muted: #6B7280;", "--text-muted: #9CA3AF;") \
    .replace("--accent-light: #EAF3F1;", "--accent-light: #1E3530;") \
    .replace("--accent-mid: #B2D4CE;", "--accent-mid: #3D6B60;") \
    .replace("--green-chip: #D1FAE5;", "--green-chip: #14532D;") \
    .replace("--green-chip-text: #065F46;", "--green-chip-text: #6EE7B7;") \
    .replace("--shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);", "--shadow-sm: 0 1px 3px rgba(0,0,0,0.3);") \
    .replace("--shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);", "--shadow-md: 0 4px 12px rgba(0,0,0,0.4);") \
    .replace("--shadow-lg: 0 8px 24px rgba(0,0,0,0.10), 0 4px 10px rgba(0,0,0,0.04);", "--shadow-lg: 0 8px 24px rgba(0,0,0,0.5);")

ECOTHEME_CSS = LIGHT_CSS \
    .replace("--bg: #F9FAFB;", "--bg: #E8F5E9;") \
    .replace("--surface: #FFFFFF;", "--surface: #F1F8E9;") \
    .replace("--surface-2: #F3F4F6;", "--surface-2: #DCEDC8;") \
    .replace("--border: #E5E7EB;", "--border: #C5E1A5;") \
    .replace("--border-focus: #4D7C6F;", "--border-focus: #558B2F;") \
    .replace("--text: #111827;", "--text: #0A2E10;") \
    .replace("--text-2: #374151;", "--text-2: #1B5E20;") \
    .replace("--text-muted: #6B7280;", "--text-muted: #2E7D32;") \
    .replace("--accent: #3D7A6B;", "--accent: #2E7D32;") \
    .replace("--accent-hover: #2E6357;", "--accent-hover: #1B5E20;") \
    .replace("--accent-light: #EAF3F1;", "--accent-light: #C8E6C9;") \
    .replace("--accent-mid: #B2D4CE;", "--accent-mid: #A5D6A7;")

def inject_css(theme: str = "Light") -> str:
    if theme == "Eco Theme":
        return ECOTHEME_CSS
    elif theme == "Dark":
        return DARK_CSS
    return LIGHT_CSS
