from __future__ import annotations
import time
from datetime import datetime
import streamlit as st

ICONS = {
    "leaf": '<svg width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22c4.97-1.46 9-6.38 9-11 0-4.42-3.58-8-8-8s-8 3.58-8 8c0 4.62 4.03 9.54 9 11z"/><path d="M12 22V11"/></svg>',
    "link": '<svg width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "user": '<svg width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
}

def render_header(theme: str = "Light") -> None:
    st.markdown(f'''
    <div class="app-header">
        <div style="font-size:2rem; margin-bottom:0.2rem; color:var(--accent);">{ICONS["leaf"]}</div>
        <div class="app-title">Eco Lifestyle Agent</div>
        <div class="app-subtitle">
            AI-powered sustainability guide using IBM Granite &amp; RAG
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_daily_tip(tip: str) -> None:
    st.markdown(f'''
    <div class="tip-banner">
        <div class="tip-label" style="display:flex;align-items:center;gap:4px;">{ICONS["leaf"]} Daily Eco Tip</div>
        <div class="tip-text">{tip}</div>
    </div>
    ''', unsafe_allow_html=True)

def render_user_bubble(message: str, timestamp: str = "") -> None:
    ts = timestamp or datetime.now().strftime("%H:%M")
    st.markdown(f'''
    <div class="msg-row-user">
        <div class="bubble-user">
            <div>{message}</div>
            <div class="bubble-meta bubble-meta-user">You · {ts}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_bot_bubble(message: str, sources: list[str] | None = None, timestamp: str = "", processing_ms: int = 0) -> None:
    ts = timestamp or datetime.now().strftime("%H:%M")
    sources_html = ""
    if sources:
        src_items = "".join(
            f'<span class="source-pill">{s}</span>' for s in sources[:3]
        )
        sources_html = f'<div style="margin-top:0.5rem;">{src_items}</div>'
    proc_str = f" · {processing_ms}ms" if processing_ms else ""
    st.markdown(f'''
    <div class="msg-row-bot">
        <div class="bot-avatar">{ICONS["leaf"]}</div>
        <div class="bubble-bot">
            <div style="font-size:0.85rem; font-weight:600; color:var(--accent); margin-bottom:0.3rem; display:flex; align-items:center; gap:4px;">
                Eco Agent
            </div>
            <div>{message}</div>   
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_thinking_indicator() -> None:
    st.markdown(f'''
    <div class="msg-row-bot">
        <div class="bot-avatar">{ICONS["leaf"]}</div>
        <div class="bubble-bot" style="padding:0.5rem 1rem;">
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
            <div class="bubble-meta">Eco Agent is thinking…</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_metric_card(value: str, label: str, icon_svg: str = "") -> None:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-icon" style="font-size:1.5rem;">{icon_svg}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    ''', unsafe_allow_html=True)

def render_eco_score(grade: str, description: str, total_tco2e: float) -> None:
    grade_class = f"score-{grade.replace('+', '-plus')}"
    st.markdown(f'''
    <div style="text-align:center; margin:1rem 0;">
        <div class="score-badge {grade_class}">{grade}</div>
        <div style="margin-top:0.75rem; font-size:1rem; font-weight:600;">
            {description}
        </div>
        <div style="color:var(--text-muted); font-size:0.88rem; margin-top:0.3rem;">
            Your annual footprint: <strong>{total_tco2e:.2f} tCO₂e</strong>
            &nbsp;|&nbsp; India average: <strong>1.9 tCO₂e</strong>
            &nbsp;|&nbsp; Paris target: <strong>2.5 tCO₂e</strong>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def section_header(title: str, icon_svg: str = "") -> None:
    st.markdown(f'''
    <div class="section-header">
        <div class="section-header-icon">{icon_svg}</div> {title}
    </div>
    ''', unsafe_allow_html=True)

def render_scheme_card(name: str, description: str, benefit: str, tag: str, link: str = "") -> None:
    link_html = f'<a href="{link}" class="scheme-link" target="_blank">{ICONS["link"]} Apply / Learn More</a>' if link else ""
    st.markdown(f'''
    <div class="scheme-card">
        <span class="scheme-tag">{tag}</span>
        <div class="scheme-name">{name}</div>
        <div class="scheme-desc">{description}</div>
        <div class="scheme-benefit">Benefit: {benefit}</div>
        <div>{link_html}</div>
    </div>
    ''', unsafe_allow_html=True)

def render_recycling_card(waste_type: str, color: str, bin_label: str, examples: str, instructions: str) -> None:
    st.markdown(f'''
    <div class="eco-card" style="border-left:5px solid {color};">
        <div class="eco-card-title" style="color:{color};">
            {bin_label}
        </div>
        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.4rem;">
            <strong>Examples:</strong> {examples}
        </div>
        <div style="font-size:0.88rem;">{instructions}</div>
    </div>
    ''', unsafe_allow_html=True)

def render_feedback_widget(message_id: str) -> None:
    st.markdown('<div style="margin-top:0.5rem;">', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 1, 1, 3])
    ratings = [f"{i} Star" for i in range(1, 6)]
    for i, (col, label) in enumerate(zip(cols[:5], ratings)):
        with col:
            if st.button(label, key=f"fb_{message_id}_{i}"):
                st.session_state[f"feedback_{message_id}"] = i + 1
                st.success("Thanks for your feedback!")
    st.markdown('</div>', unsafe_allow_html=True)

# def render_sidebar_profile() -> dict:
    # st.sidebar.markdown("---")
    # st.sidebar.markdown(f"<div style='display:flex;align-items:center;gap:4px;font-weight:bold;margin-bottom:10px;'>{ICONS['user']} Your Profile</div>", unsafe_allow_html=True)
    # location = st.sidebar.selectbox(
    #     "Location (City/State)",
    #     ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Other"],
    #     key="pref_location",
    # )
    # lifestyle = st.sidebar.selectbox(
    #     "Lifestyle",
    #     ["Urban Apartment", "Urban House", "Suburban", "Rural", "Student"],
    #     key="pref_lifestyle",
    # )
    # transport = st.sidebar.selectbox(
    #     "Primary Transport",
    #     ["Public Transit", "Car (Petrol)", "Car (Diesel)", "Electric Vehicle", "Motorbike", "Cycling", "Walking"],
    #     key="pref_transport",
    # )
    # diet = st.sidebar.selectbox(
    #     "Dietary Preference",
    #     ["Vegan", "Vegetarian", "Low Meat", "Medium Meat", "High Meat"],
    #     key="pref_diet",
    # )
    # household = st.sidebar.selectbox(
    #     "Household Type",
    #     ["1 Person", "2 People", "Small Family (3-4)", "Large Family (5+)"],
    #     key="pref_household",
    # )
    # return {
    #     "location": location,
    #     "lifestyle": lifestyle,
    #     "transport": transport,
    #     "dietary_preference": diet.lower().replace(" ", "_"),
    #     "household_type": household,
    # }
