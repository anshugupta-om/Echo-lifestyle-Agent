from __future__ import annotations
import os
import sys
import json
import time
import socket
import random
import datetime
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from frontend.styles import inject_css
from frontend.components import (
    render_header,
    render_daily_tip,
    render_user_bubble,
    render_bot_bubble,
    render_thinking_indicator,
    render_metric_card,
    render_eco_score,
    section_header,
    render_scheme_card,
    render_recycling_card,
    render_feedback_widget,
    # render_sidebar_profile,
    ICONS
)
from utils.helpers import (
    get_daily_eco_tip,
    get_random_tip,
    calculate_carbon_footprint,
    get_eco_score_label,
)
from prompts.agent_instructions import DAILY_ECO_TIPS

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Eco Lifestyle Agent",
    page_icon="leaf",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/eco-lifestyle-agent",
        "About": "AI-powered Eco Lifestyle Agent using IBM Granite + RAG",
    },
)

def init_session_state() -> None:
    defaults = {
        "chat_history": [],
        "theme": "Light",
        "eco_score": None,
        "carbon_result": None,
        "user_preferences": {},
        "conversation_history": [],
        "daily_tip": get_daily_eco_tip(),
        "tip_refresh_count": 0,
        "uploaded_filename": None,
        "page": "chat",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def _check_backend_alive(url: str) -> bool:
    host = url.replace("http://", "").replace("https://", "").split("/")[0]
    if ":" in host:
        hostname, port = host.split(":")
        port = int(port)
    else:
        hostname = host
        port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    result = s.connect_ex((hostname, port))
    s.close()
    return result == 0

def call_chat_api(question: str, prefs: dict) -> dict:
    if not _check_backend_alive(BACKEND_URL):
        return _direct_pipeline_call(question, prefs)
    payload = {
        "question": question,
        "conversation_history": st.session_state.conversation_history[-10:],
        "user_preferences": prefs,
    }
    resp = requests.post(f"{BACKEND_URL}/api/v1/chat", json=payload, timeout=60)
    if resp.status_code != 200:
        return {"answer": f"Error: Status code {resp.status_code}", "sources": [], "retrieved_chunks": 0, "retrieval_scores": [], "processing_time_ms": 0}
    return resp.json()

def _direct_pipeline_call(question: str, prefs: dict) -> dict:
    from rag.pipeline import get_pipeline
    pipeline = get_pipeline()
    start = time.perf_counter()
    result = pipeline.query(
        question=question,
        conversation_history=st.session_state.conversation_history,
        user_preferences=prefs,
    )
    result["processing_time_ms"] = int((time.perf_counter() - start) * 1000)
    return result

def call_carbon_api(data: dict) -> dict:
    if not _check_backend_alive(BACKEND_URL):
        result = calculate_carbon_footprint(**data)
        grade, desc = get_eco_score_label(result["total_tco2e"])
        return {**result, "eco_grade": grade, "eco_description": desc, "india_average_tco2e": 1.9, "paris_target_tco2e": 2.5}
    resp = requests.post(f"{BACKEND_URL}/api/v1/carbon/calculate", json=data, timeout=15)
    if resp.status_code != 200:
        result = calculate_carbon_footprint(**data)
        grade, desc = get_eco_score_label(result["total_tco2e"])
        return {**result, "eco_grade": grade, "eco_description": desc, "india_average_tco2e": 1.9, "paris_target_tco2e": 2.5}
    return resp.json()

def render_sidebar() -> None:
    st.markdown(
        """
        <div style="padding: 0.35rem 0.2rem 0.8rem; border-right: 1px solid var(--border); min-height: 100%;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'''
    <div style="text-align:center; padding:1rem 0 0.5rem;">
        <div style="font-size:2.8rem; color:var(--accent);">{ICONS["leaf"]}</div>
        <div style="font-size:1.1rem; font-weight:700; color:var(--text);">Eco Lifestyle</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">AI Agent v1.0</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")
    pages = {
        "Chat": "chat",
        "Eco Dashboard": "dashboard",
        "Carbon Calculator": "carbon",
        "Eco Score": "score",
        "Govt. Schemes": "schemes",
        "Recycling Guide": "recycling",
        "Eco Products": "products",
        "Upload Document": "upload",
    }
    for label, page_key in pages.items():
        is_active = (st.session_state.page == page_key)
        if st.button(label, key=f"nav_{page_key}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.page = page_key
            st.rerun()
    # prefs = render_sidebar_profile()
    # st.session_state.user_preferences = prefs
    st.markdown("---")
    theme_sel = st.selectbox("Theme", ["Light", "Dark", "Eco Theme"], index=["Light", "Dark", "Eco Theme"].index(st.session_state.theme) if st.session_state.theme in ["Light", "Dark", "Eco Theme"] else 0)
    if theme_sel != st.session_state.theme:
        st.session_state.theme = theme_sel
        st.rerun()
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.conversation_history = []
        time.sleep(0.5)
        st.rerun()
    if st.button("Refresh Tip", use_container_width=True):
        st.session_state.daily_tip = get_random_tip()
        st.session_state.tip_refresh_count += 1
        st.rerun()
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; font-size:0.72rem; color:var(--text-muted);">'
        'Powered by IBM Granite & ChromaDB<br>'
        'Building a Greener Future'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

def page_chat() -> None:
    render_header(st.session_state.theme)
    render_daily_tip(st.session_state.daily_tip)
    section_header("AI Eco Chat", ICONS["leaf"])
    st.caption("Ask me anything about sustainability, waste management, energy saving, government schemes, carbon footprint, and more!")
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            welcome = (
                "Welcome to Eco Lifestyle Agent!\n\n"
                "I'm your AI-powered sustainability guide. Ask me about:\n"
                "- Waste segregation & recycling\n"
                "- Water conservation tips\n"
                "- Solar energy & government schemes\n"
                "- Eco-friendly transport options\n"
                "- Sustainable food choices\n"
                "- Reducing your carbon footprint\n\n"
                "*Type your question below to get started!*"
            )
            render_bot_bubble(welcome)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    render_user_bubble(msg["content"], msg.get("ts", ""))
                else:
                    render_bot_bubble(
                        msg["content"],
                        msg.get("sources", []),
                        msg.get("ts", ""),
                        msg.get("ms", 0),
                    )
    st.markdown("**Quick Questions:**")
    suggestions = [
        "How can I reduce plastic waste at home?",
        "What is PM Surya Ghar scheme?",
        "How do I calculate my carbon footprint?",
        "Best ways to save water in my apartment?",
        "Which EV is best for daily commuting in India?",
        "How to start composting at home?",
    ]
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                _process_question(suggestion)
    st.markdown("---")
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Your question",
            placeholder="Ask about eco-friendly living, sustainability tips, government schemes...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_send:
        send_clicked = st.button("Send", use_container_width=True, type="primary")
    if send_clicked and user_input.strip():
        _process_question(user_input.strip())
    if st.session_state.chat_history:
        with st.expander("Rate Last Response"):
            last_bot = next(
                (m for m in reversed(st.session_state.chat_history) if m["role"] == "bot"), None
            )
            if last_bot:
                render_feedback_widget(last_bot.get("id", "last"))

def _process_question(question: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M")
    msg_id = f"msg_{int(time.time())}"
    st.session_state.chat_history.append(
        {"role": "user", "content": question, "ts": ts, "id": f"user_{msg_id}"}
    )
    st.session_state.conversation_history.append(
        {"role": "user", "content": question}
    )
    with st.spinner("Eco Agent is thinking..."):
        result = call_chat_api(question, st.session_state.user_preferences)
    answer = result.get("answer", "Sorry, I couldn't generate a response.")
    sources = result.get("sources", [])
    ms = result.get("processing_time_ms", 0)
    st.session_state.chat_history.append({
        "role": "bot",
        "content": answer,
        "sources": sources,
        "ts": datetime.datetime.now().strftime("%H:%M"),
        "ms": ms,
        "id": f"bot_{msg_id}",
    })
    st.session_state.conversation_history.append(
        {"role": "assistant", "content": answer}
    )
    st.rerun()

def page_dashboard() -> None:
    section_header("Eco Dashboard", ICONS["leaf"])
    st.caption("Your sustainability metrics at a glance")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(str(len(st.session_state.chat_history) // 2), "Questions Asked", ICONS["leaf"])
    with col2:
        score = st.session_state.eco_score
        val = f"{score:.1f}" if score else "—"
        render_metric_card(val, "tCO2e / Year", ICONS["leaf"])
    with col3:
        render_metric_card(str(len(DAILY_ECO_TIPS)), "Eco Tips Available", ICONS["leaf"])
    with col4:
        render_metric_card("20+", "Knowledge Topics", ICONS["leaf"])
    st.markdown("---")
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.subheader("India vs. Global Carbon Context")
        categories = ["India Avg", "Your Footprint", "Paris Target", "World Avg", "US Avg"]
        values = [1.9, st.session_state.eco_score or 1.9, 2.5, 4.8, 14.5]
        colors = ["#16a34a", "#15803d", "#86efac", "#fbbf24", "#ef4444"]
        fig = go.Figure(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
        ))
        fig.update_layout(
            yaxis_title="tCO2e per person per year",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=12, color="var(--text)"),
            margin=dict(t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        st.subheader("Waste Composition (India Urban)")
        labels = ["Organic/Wet", "Paper", "Plastic", "Glass/Metal", "Other"]
        values_w = [55, 14, 10, 5, 16]
        fig2 = go.Figure(go.Pie(
            labels=labels,
            values=values_w,
            marker_colors=["#16a34a", "#86efac", "#4ade80", "#bbf7d0", "#d1fae5"],
            hole=0.45,
        ))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=12, color="var(--text)"),
            margin=dict(t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig2, use_container_width=True)
    if st.session_state.carbon_result:
        st.markdown("---")
        st.subheader("Your Carbon Footprint Breakdown")
        cr = st.session_state.carbon_result
        breakdown = {
            "Electricity": cr.get("electricity_tco2e", 0),
            "LPG/Cooking": cr.get("lpg_tco2e", 0),
            "Transport": cr.get("transport_tco2e", 0),
            "Diet": cr.get("diet_tco2e", 0),
            "Food Waste": cr.get("food_waste_tco2e", 0),
        }
        df_vals = list(breakdown.values())
        df_labels = list(breakdown.keys())
        fig3 = px.bar(
            x=df_labels, y=df_vals,
            color=df_labels,
            color_discrete_sequence=["#16a34a", "#15803d", "#86efac", "#4ade80", "#bbf7d0"],
            labels={"x": "Category", "y": "tCO2e/year"},
        )
        fig3.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="var(--text)"),
            margin=dict(t=20, b=20),
            height=300,
        )
        st.plotly_chart(fig3, use_container_width=True)

def page_carbon_calculator() -> None:
    section_header("Carbon Footprint Calculator", ICONS["leaf"])
    st.caption("Calculate your annual household carbon footprint and get personalised tips")
    with st.form("carbon_form"):
        st.markdown("#### Energy")
        col1, col2 = st.columns(2)
        with col1:
            electricity = st.slider("Monthly electricity (kWh)", 0, 1000, 200)
        with col2:
            lpg = st.slider("LPG cylinders per year", 0, 24, 6)
        st.markdown("#### Transport")
        col3, col4, col5 = st.columns(3)
        with col3:
            car_km = st.slider("Car km/day", 0, 200, 20)
            fuel_type = st.selectbox("Car fuel", ["petrol", "diesel", "electric"])
        with col4:
            bike_km = st.slider("Motorbike km/day", 0, 100, 5)
            bus_km = st.slider("Bus km/day", 0, 100, 10)
        with col5:
            metro_km = st.slider("Metro/rail km/day", 0, 100, 5)
            flights = st.number_input("Flights per year", 0, 50, 2)
        st.markdown("#### Diet & Lifestyle")
        col6, col7 = st.columns(2)
        with col6:
            diet = st.selectbox("Diet type", ["vegan", "vegetarian", "low_meat", "medium_meat", "high_meat"], index=3)
        with col7:
            food_waste = st.slider("Food waste (kg/week)", 0.0, 10.0, 1.0, step=0.5)
        submitted = st.form_submit_button("Calculate My Carbon Footprint", type="primary")
    if submitted:
        data = {
            "electricity_kwh_per_month": electricity,
            "lpg_cylinders_per_year": lpg,
            "car_km_per_day": car_km,
            "car_fuel_type": fuel_type,
            "bike_km_per_day": bike_km,
            "bus_km_per_day": bus_km,
            "metro_km_per_day": metro_km,
            "flights_per_year": flights,
            "avg_flight_km": 1500,
            "diet_type": diet,
            "food_waste_kg_per_week": food_waste,
        }
        with st.spinner("Calculating..."):
            result = call_carbon_api(data)
        st.session_state.carbon_result = result
        st.session_state.eco_score = result["total_tco2e"]
        render_eco_score(result["eco_grade"], result["eco_description"], result["total_tco2e"])
        st.markdown("#### Breakdown")
        categories = ["Electricity", "LPG/Cooking", "Transport", "Diet", "Food Waste"]
        values = [result["electricity_tco2e"], result["lpg_tco2e"], result["transport_tco2e"], result["diet_tco2e"], result["food_waste_tco2e"]]
        for cat, val in zip(categories, values):
            pct = val / result["total_tco2e"] * 100 if result["total_tco2e"] > 0 else 0
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(min(pct / 100, 1.0), text=f"{cat}")
            with col_b:
                st.markdown(f"**{val:.3f} t**")
        st.markdown("#### Priority Actions")
        action_map = {
            "Electricity": "Install rooftop solar — PM Surya Ghar gives up to Rs 78,000 subsidy.",
            "LPG/Cooking": "Switch to solar cooker or induction; consider PNG connection.",
            "Transport": "Use public transit 3x/week; consider an EV under FAME II scheme.",
            "Diet": "Try Meatless Monday — saves approx 2.5 kg CO2 per plant-based meal.",
            "Food Waste": "Set up a home compost bin — converts waste to garden fertiliser.",
        }
        sorted_cats = sorted(zip(values, categories), reverse=True)
        for val, cat in sorted_cats[:3]:
            st.info(action_map.get(cat, ""))

def page_eco_score() -> None:
    section_header("Eco Score Tracker", ICONS["leaf"])
    st.caption("Track your sustainability progress over time")
    if st.session_state.eco_score:
        grade, desc = get_eco_score_label(st.session_state.eco_score)
        render_eco_score(grade, desc, st.session_state.eco_score)
    else:
        st.info("You haven't calculated your carbon footprint yet. Go to the Carbon Calculator tab to get your Eco Score!")
    st.markdown("---")
    st.subheader("Improvement Milestones")
    milestones = [
        ("Eco Starter", "< 5 tCO2e/year", "Replace bulbs with LED, segregate waste"),
        ("Eco Aware", "< 3.5 tCO2e/year", "Reduce car trips, use public transit"),
        ("Eco Active", "< 2.5 tCO2e/year", "Install solar, switch to EV or cycling"),
        ("Eco Champion", "< 1.5 tCO2e/year", "Plant-based diet, near-zero waste lifestyle"),
        ("Eco Leader", "< 0.8 tCO2e/year", "Net-zero home, full circular lifestyle"),
    ]
    user_score = st.session_state.eco_score or 9.0
    for milestone, target, action in milestones:
        threshold = float(target.replace("< ", "").replace(" tCO2e/year", ""))
        achieved = user_score <= threshold
        icon = "[Done]" if achieved else "[ ]"
        color = "var(--accent)" if achieved else "var(--border)"
        st.markdown(f'''
        <div style="padding:0.5rem 0.75rem; border-left:3px solid {color}; margin-bottom:0.5rem; border-radius:0 8px 8px 0; background:{'var(--accent-light)' if achieved else 'var(--surface)'};">
            <strong>{icon} {milestone}</strong> — {target}<br>
            <span style="font-size:0.83rem; color:var(--text-muted);">{action}</span>
        </div>
        ''', unsafe_allow_html=True)

def page_schemes() -> None:
    section_header("Government Environmental Schemes", ICONS["leaf"])
    st.caption("Central & state government incentives for sustainable living — India 2024")
    tab1, tab2 = st.tabs(["Central Schemes", "State Schemes"])
    with tab1:
        schemes_central = [
            {"name": "PM Surya Ghar Muft Bijli Yojana", "desc": "Rooftop solar panel installation subsidy for households.", "benefit": "Up to Rs 78,000 subsidy for 3kW system + 300 units/month free electricity", "tag": "Solar", "link": "https://pmsuryaghar.gov.in"},
            {"name": "FAME India Phase II", "desc": "Faster Adoption and Manufacturing of Electric Vehicles scheme.", "benefit": "Subsidy of Rs 10,000-20,000 per electric 2-wheeler; Rs 1.5 lakh for electric cars", "tag": "EV", "link": "https://fame2.heavyindustries.gov.in"},
            {"name": "PM-KUSUM Scheme", "desc": "Solar pumps for farmers under Pradhan Mantri Kisan Urja Suraksha Yojana.", "benefit": "35-40% subsidy on solar pumps; 7.5 lakh solar pumps targeted", "tag": "Agriculture", "link": "https://mnre.gov.in/solar/schemes"},
            {"name": "National Biogas Programme", "desc": "MNRE support for setting up household and community biogas plants.", "benefit": "Rs 7,000-15,000 subsidy per unit; converts kitchen waste to cooking gas", "tag": "Biogas", "link": "https://mnre.gov.in/bio-energy"},
            {"name": "Jal Jeevan Mission", "desc": "Tap water connectivity to every rural household + water conservation.", "benefit": "Free household tap connections; water literacy and conservation programs", "tag": "Water", "link": "https://jaljeevanmission.gov.in"},
            {"name": "National Clean Air Programme (NCAP)", "desc": "40% reduction in PM pollution by 2026 in 132 non-attainment cities.", "benefit": "City-level action plans; funding for monitoring and clean energy transition", "tag": "Air Quality", "link": "https://cpcb.nic.in"},
        ]
        for s in schemes_central:
            render_scheme_card(s["name"], s["desc"], s["benefit"], s["tag"], s["link"])
    with tab2:
        st.markdown("Select your state to see relevant incentives:")
        state = st.selectbox("State", ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat", "Telangana", "Rajasthan", "Kerala", "West Bengal"])
        state_schemes = {
            "Maharashtra": [("EV Subsidy", "Rs 25,000 for 2-wheelers, Rs 1.5 lakh for 4-wheelers", "EV"), ("MREDC Solar Subsidy", "Rs 5,000/kWh for residential solar", "Solar"), ("Single-Use Plastic Ban", "Ban on plastics < 50 microns since 2018", "Waste")],
            "Delhi": [("EV Subsidy", "Up to Rs 30,000 for 2-wheelers, Rs 1.5 lakh for cars", "EV"), ("100% Road Tax Waiver", "Zero road tax for all EVs", "EV"), ("Switch Delhi Campaign", "Free EV insurance for 1st year + charging incentives", "Green")],
            "Karnataka": [("KREDL Solar", "Net metering and group net metering programs", "Solar"), ("Solar Water Heater", "Rs 7,500 subsidy for EWS/LIG households", "Solar")],
            "Tamil Nadu": [("Rooftop Solar", "Net metering mandatory + group net metering", "Solar"), ("Mandatory RWH", "Rainwater harvesting mandatory for all new buildings", "Water")],
            "Gujarat": [("Solar Rooftop Yojana", "Rs 10,000/kW subsidy up to 3kW", "Solar"), ("EV Policy", "25% subsidy capped at Rs 1.75 lakh for 4-wheelers", "EV")],
        }
        for s_name, s_benefit, s_tag in state_schemes.get(state, [("Coming Soon", "More schemes being added", "Update")]):
            render_scheme_card(s_name, "", s_benefit, s_tag)

def page_recycling() -> None:
    section_header("Recycling & Waste Segregation Guide", ICONS["leaf"])
    st.caption("Know your bins — proper waste segregation at source makes recycling possible")
    waste_types = [
        {"waste_type": "Wet / Organic Waste", "color": "#16a34a", "bin_label": "GREEN BIN - Wet Waste", "examples": "Fruit & vegetable peels, cooked food leftovers, tea leaves, coffee grounds, garden trimmings", "instructions": "Dispose daily. Can be composted at home or sent to municipal biogas plants."},
        {"waste_type": "Dry / Recyclable Waste", "color": "#2563eb", "bin_label": "BLUE BIN - Dry Waste", "examples": "Paper, cardboard, plastic bottles/containers, glass bottles, metal cans, tetra packs, newspapers", "instructions": "Rinse and dry before discarding. Remove food residue. Sort by material when possible."},
        {"waste_type": "Hazardous Waste", "color": "#dc2626", "bin_label": "RED BIN - Hazardous Waste", "examples": "Batteries, chemicals, paints, pesticides, medicines, fluorescent bulbs, motor oil", "instructions": "NEVER mix with regular waste. Take to designated hazardous waste collection points."},
        {"waste_type": "E-Waste", "color": "#9333ea", "bin_label": "E-WASTE - Electronics", "examples": "Old phones, laptops, chargers, cables, TVs, refrigerators, washing machines", "instructions": "Return to manufacturer take-back programs. Use certified e-waste recyclers."},
        {"waste_type": "Sanitary Waste", "color": "#d97706", "bin_label": "YELLOW - Sanitary Waste", "examples": "Diapers, sanitary pads, bandages, medical gloves", "instructions": "Wrap tightly in newspaper or a separate bag. Mark clearly. Do not put in green or blue bins."},
    ]
    for wt in waste_types:
        render_recycling_card(wt["waste_type"], wt["color"], wt["bin_label"], wt["examples"], wt["instructions"])
    st.markdown("---")
    st.subheader("Composting at Home")
    col_a, col_b, col_c = st.columns(3)
    methods = [
        ("Aerobic Bin", "6-8 weeks", "Kitchen scraps + dry leaves. Perfect for gardens. Keep 3:1 brown:green ratio."),
        ("Vermicomposting", "2-4 weeks", "Red earthworms process waste 3x faster. Produces rich worm castings."),
        ("Bokashi", "2 weeks", "Anaerobic fermentation. Accepts meat & dairy. Uses EM bran. Ideal for apartments."),
    ]
    for col, (method, time_val, desc) in zip([col_a, col_b, col_c], methods):
        with col:
            st.markdown(f'''
            <div class="eco-card">
                <div class="eco-card-title">{method}</div>
                <div style="color:var(--accent); font-size:0.82rem; margin-bottom:0.4rem;">{time_val}</div>
                <div style="font-size:0.85rem;">{desc}</div>
            </div>
            ''', unsafe_allow_html=True)

def page_products() -> None:
    section_header("Sustainable Product Recommendations", ICONS["leaf"])
    st.caption("Eco-friendly alternatives that save money and reduce your footprint")
    categories = st.tabs(["Kitchen", "Bathroom", "Household", "Clothing", "Energy"])
    kitchen_products = [
        ("Beeswax Wraps", "Replace plastic cling film", "Rs 400-800", "1 year reusable", "#16a34a"),
        ("Stainless Steel Bottles", "Replace single-use plastic bottles", "Rs 300-1200", "10+ years", "#16a34a"),
        ("Bamboo Straws (set of 8)", "Replace plastic straws", "Rs 100-200", "Reusable, washable", "#16a34a"),
        ("Natural Dish Soap Bar", "Replace liquid soap in plastic bottle", "Rs 80-150", "Compostable packaging", "#16a34a"),
        ("Silicone Food Bags", "Replace ziplock plastic bags", "Rs 200-500", "Dishwasher safe, reusable", "#4ade80"),
        ("Coconut Fibre Scrubber", "Replace synthetic sponge", "Rs 30-80", "Fully compostable", "#86efac"),
        ("Cloth Produce Bags", "Replace plastic produce bags", "Rs 150-300/set", "Washable, organic cotton", "#4ade80"),
        ("Compost Bin (5L)", "Separate wet waste at source", "Rs 300-800", "Enables home composting", "#16a34a"),
    ]
    bathroom_products = [
        ("Bamboo Toothbrush", "Replace plastic toothbrush", "Rs 80-150", "Compostable bamboo handle", "#16a34a"),
        ("Shampoo Bar", "Replace plastic shampoo bottle", "Rs 200-400", "Last 80-90 washes", "#16a34a"),
        ("Safety Razor", "Replace disposable plastic razors", "Rs 500-2000", "Replace only blade", "#16a34a"),
        ("Menstrual Cup", "Replace disposable pads/tampons", "Rs 500-1500", "Lasts 10 years", "#16a34a"),
        ("Reusable Cotton Rounds", "Replace cotton pads", "Rs 250-400/16pc", "Machine washable", "#4ade80"),
        ("Natural Soap Bars", "Replace liquid body wash", "Rs 80-200", "Natural ingredients", "#4ade80"),
    ]
    household_products = [
        ("Bio-enzyme Cleaners", "Replace chemical surface cleaners", "Rs 150-300", "Non-toxic, safe for pets", "#16a34a"),
        ("Reusable 'Paper' Towels", "Replace disposable paper towels", "Rs 200-500", "Washable cotton/bamboo", "#4ade80"),
        ("Eco Laundry Detergent Sheets", "Replace liquid detergent in plastic", "Rs 300-600", "Zero plastic, plant-based", "#16a34a"),
        ("Jute/Canvas Grocery Bags", "Replace plastic shopping bags", "Rs 100-250", "Heavy duty, lasts for years", "#16a34a"),
        ("Coir Doormats", "Replace synthetic rubber mats", "Rs 300-700", "100% biodegradable", "#86efac"),
        ("Essential Oil Room Freshener", "Replace aerosol air fresheners", "Rs 200-400", "No harmful VOCs", "#4ade80"),
    ]

    clothing_products = [
        ("Organic Cotton Basics", "Replace fast fashion synthetics", "Rs 500-1500", "Breathable, pesticide-free", "#16a34a"),
        ("Bamboo Fiber Socks", "Replace Nylon/Polyester socks", "Rs 150-300", "Odor-resistant, sustainable", "#4ade80"),
        ("Upcycled Tote Bags", "Replace new synthetic bags", "Rs 300-800", "Diverts waste from landfill", "#16a34a"),
        ("Guppyfriend Washing Bag", "Replace standard wash bags", "Rs 1500-2000", "Catches microplastics in wash", "#86efac"),
    ]

    energy_products = [
        ("LED Bulbs (9W)", "Replace Incandescent/CFL bulbs", "Rs 100-300", "Uses 80% less energy", "#16a34a"),
        ("Solar Power Bank", "Replace grid-only power banks", "Rs 800-2000", "Charges devices via sunlight", "#16a34a"),
        ("Smart Power Strip", "Replace standard extension cords", "Rs 1000-2500", "Prevents phantom power drain", "#4ade80"),
        ("Rechargeable NiMH Batteries", "Replace single-use AA/AAA batteries", "Rs 400-1000", "Can be recharged 1000x", "#16a34a"),
        ("Water-saving Aerator", "Standard high-flow taps", "Rs 150-300", "Saves up to 60% water", "#16a34a"),
        ("Solar String Lights", "Plug-in decorative lights", "Rs 500-1200", "Zero electricity cost", "#86efac"),
    ]
    with categories[0]:
        cols = st.columns(2)
        for i, (name, replace, price, benefit, color) in enumerate(kitchen_products):
            with cols[i % 2]:
                st.markdown(f'''
                <div class="eco-card" style="border-left:4px solid {color};">
                    <div class="eco-card-title">{name}</div>
                    <div style="font-size:0.83rem; color:var(--text-muted);">Replaces: {replace}</div>
                    <div style="font-size:0.88rem; margin:0.3rem 0;">Price: {price}</div>
                    <div style="font-size:0.83rem; color:var(--accent);">Benefit: {benefit}</div>
                </div>
                ''', unsafe_allow_html=True)
    with categories[1]:
        cols = st.columns(2)
        for i, (name, replace, price, benefit, color) in enumerate(bathroom_products):
            with cols[i % 2]:
                st.markdown(f'''
                <div class="eco-card" style="border-left:4px solid {color};">
                    <div class="eco-card-title">{name}</div>
                    <div style="font-size:0.83rem; color:var(--text-muted);">Replaces: {replace}</div>
                    <div style="font-size:0.88rem; margin:0.3rem 0;">Price: {price}</div>
                    <div style="font-size:0.83rem; color:var(--accent);">Benefit: {benefit}</div>
                </div>
                ''', unsafe_allow_html=True)
    with categories[2]:
        cols = st.columns(2)
        for i, (name, replace, price, benefit, color) in enumerate(household_products):
            with cols[i % 2]:
                st.markdown(f'''
                <div class="eco-card" style="border-left:4px solid {color};">
                    <div class="eco-card-title">{name}</div>
                    <div style="font-size:0.83rem; color:var(--text-muted);">Replaces: {replace}</div>
                    <div style="font-size:0.88rem; margin:0.3rem 0;">Price: {price}</div>
                    <div style="font-size:0.83rem; color:var(--accent);">Benefit: {benefit}</div>
                </div>
                ''', unsafe_allow_html=True)
    with categories[3]:
        cols = st.columns(2)
        for i, (name, replace, price, benefit, color) in enumerate(clothing_products):
            with cols[i % 2]:
                st.markdown(f'''
                <div class="eco-card" style="border-left:4px solid {color};">
                    <div class="eco-card-title">{name}</div>
                    <div style="font-size:0.83rem; color:var(--text-muted);">Replaces: {replace}</div>
                    <div style="font-size:0.88rem; margin:0.3rem 0;">Price: {price}</div>
                    <div style="font-size:0.83rem; color:var(--accent);">Benefit: {benefit}</div>
                </div>
                ''', unsafe_allow_html=True)
    with categories[4]:
        cols = st.columns(2)
        for i, (name, replace, price, benefit, color) in enumerate(energy_products):
            with cols[i % 2]:
                st.markdown(f'''
                <div class="eco-card" style="border-left:4px solid {color};">
                    <div class="eco-card-title">{name}</div>
                    <div style="font-size:0.83rem; color:var(--text-muted);">Replaces: {replace}</div>
                    <div style="font-size:0.88rem; margin:0.3rem 0;">Price: {price}</div>
                    <div style="font-size:0.83rem; color:var(--accent);">Benefit: {benefit}</div>
                </div>
                ''', unsafe_allow_html=True)

def page_upload() -> None:
    section_header("Upload Document for Analysis", ICONS["leaf"])
    st.caption("Upload PDFs or Text files to augment the AI's knowledge")
    st.info("Feature in development. For now, use the scripts/ingest_documents.py tool.")

def main() -> None:
    init_session_state()
    st.markdown(inject_css(st.session_state.theme), unsafe_allow_html=True)
    sidebar_col, content_col = st.columns([0.28, 0.72], gap="large")
    with sidebar_col:
        render_sidebar()
    with content_col:
        page = st.session_state.page
        if page == "chat":
            page_chat()
        elif page == "dashboard":
            page_dashboard()
        elif page == "carbon":
            page_carbon_calculator()
        elif page == "score":
            page_eco_score()
        elif page == "schemes":
            page_schemes()
        elif page == "recycling":
            page_recycling()
        elif page == "products":
            page_products()
        elif page == "upload":
            page_upload()

if __name__ == "__main__":
    main()
    
# Force reload for ultimate CSS override
