import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="UNCW Generator Safety Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CONSTANTS & CONFIG ====================

SYSTEM_PROMPT = """You are the UNCW Generator Safety Assistant, an official resource for students.
Provide accurate, life-saving information about generator safety, CO poisoning prevention, and emergency procedures.
Always prioritize safety and direct users to call 911 in emergencies.
Base answers on official guidelines from Red Cross, CDC, NFPA, and NOAA.
Be concise but thorough. Use clear, professional language suitable for college students."""

# Professional color palette
COLORS = {
    "primary": "#0066B3",      # UNCW Teal
    "secondary": "#F2C75F",     # UNCW Gold
    "dark": "#0B1F2E",          # Dark navy
    "surface": "#1E3A5F",       # Medium blue
    "light": "#F5F9FF",         # Light background
    "text": "#1A2B3C",          # Dark text
    "text_light": "#5F6B7A",    # Muted text
    "success": "#2E7D32",       # Green
    "warning": "#C62828",       # Red
    "border": "#D1D9E6",        # Light gray
    "card_bg": "#FFFFFF",       # White
}

# Safety rules data for easy updates
SAFETY_RULES = [
    {"icon": "📍", "rule": "OUTDOORS ONLY", "detail": "Never in garages, basements, porches, or indoors"},
    {"icon": "📏", "rule": "20 FEET", "detail": "From doors, windows, and vents"},
    {"icon": "🔋", "rule": "CO DETECTORS", "detail": "Required on every level, test monthly"},
    {"icon": "⛽", "rule": "REFUELING", "detail": "Turn off and let cool 30min before adding gas"},
    {"icon": "🔌", "rule": "NO BACKFEEDING", "detail": "Never plug into wall outlets"},
    {"icon": "☔", "rule": "KEEP DRY", "detail": "Never operate in rain or wet conditions"},
    {"icon": "🛑", "rule": "OVERLOAD", "detail": "Check wattage, don't daisy chain cords"},
    {"icon": "⚠️", "rule": "CO SYMPTOMS", "detail": "Headache, dizziness, nausea = get to fresh air NOW"},
]

QUICK_REFERENCE = [
    {"icon": "🏠", "topic": "GARAGE", "detail": "Never run in garage - CO kills"},
    {"icon": "🏢", "topic": "BALCONY", "detail": "Too close to building, 20ft minimum"},
    {"icon": "🏫", "topic": "DORM", "detail": "Generators prohibited in dorms"},
    {"icon": "🏡", "topic": "OFF-CAMPUS", "detail": "Place 20ft from house, never indoors"},
    {"icon": "🔋", "topic": "CO DETECTOR", "detail": "Test monthly, replace batteries"},
    {"icon": "⛽", "topic": "FUEL", "detail": "Store outside in approved containers"},
    {"icon": "🌊", "topic": "HURRICANE", "detail": "Check NOAA for updates"},
    {"icon": "📞", "topic": "EMERGENCY", "detail": "911 for immediate danger"},
    {"icon": "☎️", "topic": "POISON CONTROL", "detail": "1-800-222-1222"},
]

# ==================== CUSTOM CSS ====================

def load_css():
    """Load custom CSS for professional styling"""
    st.markdown(f"""
    <style>
        /* Main container */
        .main {{
            background-color: {COLORS["light"]};
        }}
        
        .stApp {{
            background-color: {COLORS["light"]};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Header styling */
        .header-container {{
            background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["surface"]} 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            border-radius: 0 0 30px 30px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }}
        
        .header-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
        }}
        
        .official-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-size: 0.9rem;
            margin-top: 1rem;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        /* Emergency banner */
        .emergency-banner {{
            background: #FFEBEE;
            border-left: 6px solid {COLORS["warning"]};
            color: {COLORS["warning"]};
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            font-weight: 600;
            font-size: 1.1rem;
            box-shadow: 0 2px 8px rgba(198,40,40,0.1);
        }}
        
        /* Resource bar */
        .resource-bar {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 1.5rem 0 2.5rem 0;
            padding: 0.75rem 1.5rem;
            background: white;
            border-radius: 50px;
            border: 1px solid {COLORS["border"]};
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }}
        
        .resource-link {{
            color: {COLORS["primary"]};
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}
        
        .resource-link:hover {{
            color: {COLORS["surface"]};
            text-decoration: underline;
        }}
        
        /* Cards */
        .safety-card {{
            background: {COLORS["card_bg"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 20px;
            padding: 1.5rem;
            height: 100%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .safety-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,102,179,0.1);
        }}
        
        .card-header {{
            font-size: 1.1rem;
            font-weight: 600;
            color: {COLORS["primary"]};
            margin-bottom: 1.2rem;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid {COLORS["secondary"]};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .rule-item {{
            display: flex;
            align-items: flex-start;
            padding: 0.7rem 0;
            border-bottom: 1px solid {COLORS["border"]};
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        .rule-item:last-child {{
            border-bottom: none;
        }}
        
        .rule-icon {{
            font-size: 1.2rem;
            margin-right: 0.8rem;
            min-width: 24px;
        }}
        
        .rule-content {{
            flex: 1;
        }}
        
        .rule-title {{
            font-weight: 600;
            color: {COLORS["surface"]};
        }}
        
        .rule-detail {{
            color: {COLORS["text_light"]};
            font-size: 0.85rem;
        }}
        
        /* Chat panel */
        .chat-panel {{
            background: white;
            border: 1px solid {COLORS["border"]};
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }}
        
        /* Question chips */
        .stButton button {{
            background: white;
            border: 1px solid {COLORS["border"]};
            color: {COLORS["text"]};
            padding: 0.6rem 1rem;
            border-radius: 40px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        
        .stButton button:hover {{
            border-color: {COLORS["primary"]};
            background: {COLORS["light"]};
            color: {COLORS["primary"]};
            box-shadow: 0 4px 12px rgba(0,102,179,0.15);
        }}
        
        /* Input styling */
        .stTextInput > div > div > input {{
            background: {COLORS["light"]};
            border: 2px solid {COLORS["border"]};
            border-radius: 50px;
            padding: 0.8rem 1.5rem;
            font-size: 1rem;
            transition: all 0.2s;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLORS["primary"]};
            box-shadow: 0 0 0 4px rgba(0,102,179,0.1);
        }}
        
        /* Submit button */
        .stForm button {{
            background: {COLORS["primary"]};
            color: white;
            border: none;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(0,102,179,0.3);
        }}
        
        .stForm button:hover {{
            background: {COLORS["surface"]};
            box-shadow: 0 6px 16px rgba(0,102,179,0.4);
        }}
        
        /* Response area */
        .response-box {{
            background: {COLORS["light"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 20px;
            padding: 2rem;
            margin-top: 2rem;
            border-left: 6px solid {COLORS["primary"]};
        }}
        
        .response-title {{
            color: {COLORS["primary"]};
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .response-content {{
            color: {COLORS["text"]};
            line-height: 1.7;
            font-size: 1rem;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 4rem;
            padding: 2rem;
            text-align: center;
            background: {COLORS["dark"]};
            color: white;
            border-radius: 30px 30px 0 0;
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 1rem 0;
        }}
        
        .footer-links a {{
            color: {COLORS["secondary"]};
            text-decoration: none;
            font-size: 0.9rem;
        }}
        
        .footer-links a:hover {{
            text-decoration: underline;
        }}
        
        /* Helper text */
        .helper-text {{
            color: {COLORS["text_light"]};
            font-size: 0.85rem;
            margin-top: 0.8rem;
            text-align: center;
            font-style: italic;
        }}
        
        /* Divider */
        .custom-divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent, {COLORS["secondary"]}, transparent);
            margin: 2rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== FUNCTIONS ====================

def check_ollama_status():
    """Check if Ollama is running and has qwen3"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Check if qwen3 is available (any variant)
            available_models = [m["name"] for m in models]
            return any("qwen3" in m for m in available_models)
        return False
    except:
        return False

def get_safety_response(question):
    """Get response from Ollama using qwen3:32b"""
    if check_ollama_status():
        try:
            # Use qwen3:32b as specified
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen3:32b",  # CORRECTED - using qwen3:32b
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=45
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if "404" in str(e):
                return "⚠️ **Model not found**. Run: `ollama pull qwen3:32b` in your terminal"
            return f"⚠️ **Error**: {str(e)}"
        except Exception as e:
            return get_fallback_response(question)
    else:
        return get_fallback_response(question)

def get_fallback_response(question):
    """Provide fallback responses when Ollama is offline"""
    q = question.lower()
    
    responses = {
        "garage": """❌ **NEVER run generators in garages** - even with the door open!

Carbon monoxide (CO) is odorless and can reach lethal levels in minutes. Garage spaces trap CO, which then seeps into living areas through walls, doors, and windows.

**Safe alternatives:**
• Place generator outside, at least 20 feet from home
• Use a generator tent/canopy for weather protection
• Install battery-powered CO detectors on every level""",
        
        "balcony": """⚠️ **Apartment balconies are unsafe for generators**

Most apartments prohibit generators due to:
• CO poisoning risk to neighbors
• Fire hazards
• Building code violations

**What to do instead:**
• Contact your apartment office about emergency plans
• Consider battery backup systems
• Know your building's evacuation routes""",
        
        "dorm": """🚫 **Generators are strictly prohibited in all UNCW dormitories**

UNCW Housing Policy states:
• No fuel-burning equipment allowed in dorms
• Violations result in fines and disciplinary action

**During power outages:**
• Report outages to Residence Life
• Follow RA instructions
• Use flashlights, not candles
• Charge devices in common areas""",
        
        "co2": """⚠️ **Carbon monoxide (CO) has NO smell, taste, or color**

That's what makes it so dangerous - it's called the "Silent Killer."

**Protect yourself:**
• Install CO detectors on every level
• Test alarms monthly
• Replace batteries twice a year
• Know symptoms: headache, dizziness, nausea, confusion

**If alarm sounds:**
1. Get outside immediately
2. Call 911
3. Do not go back inside""",
        
        "rain": """☔ **Never operate generators in rain or wet conditions**

Water and electricity create deadly shock hazards!

**Safe operation in wet weather:**
• Use a generator tent or canopy (ensure ventilation)
• Place generator on dry, elevated surface
• Keep connections dry and off wet ground
• Never touch generator with wet hands

**Alternative:** Wait for dry conditions if possible""",
        
        "smell": """⚠️ **Carbon monoxide (CO) has NO smell!**

If you're asking about CO2 (carbon dioxide), that's different:
• **CO (carbon monoxide)** - No smell, KILLS
• **CO2 (carbon dioxide)** - Odorless, but not typically from generators

**Generator exhaust contains:**
• Carbon monoxide (deadly, no smell)
• Various gases and particles

If you smell something: it's NOT carbon monoxide - trust your CO detector, not your nose!"""
    }
    
    for key in responses:
        if key in q:
            return responses[key]
    
    return """**Generator Safety Quick Guide:**

📍 **Placement:** ALWAYS outdoors, 20+ feet from building
🔋 **Detectors:** CO alarms on every level, test monthly
⛽ **Fuel:** Store outside in approved containers
🚨 **Emergency:** If you feel sick or alarm sounds → GET OUT, call 911

**Need specific info?** Try asking about:
• Garage use
• Apartment balconies  
• Dorm rules
• CO poisoning symptoms
• Operation in rain
• What CO smells like (spoiler: nothing!)"""

# ==================== MAIN APP ====================

def main():
    # Load custom CSS
    load_css()
    
    # Initialize session state
    if "question" not in st.session_state:
        st.session_state.question = ""
    if "response" not in st.session_state:
        st.session_state.response = ""
    if "ollama_status" not in st.session_state:
        st.session_state.ollama_status = check_ollama_status()
    
    # ==================== HEADER ====================
    status_text = ""
    if st.session_state.ollama_status:
        status_text = " • Using Qwen3 32B"
    else:
        status_text = " • Offline Mode (Qwen3 not detected)"
    
    st.markdown(f"""
    <div class="header-container">
        <div style="max-width: 1200px; margin: 0 auto;">
            <div class="header-title">⚡ UNCW Generator Safety Assistant</div>
            <div class="header-subtitle">Official guidance for students • New Hanover County, NC</div>
            <div class="official-badge">
                <span style="margin-right: 8px;">🏛️</span> 
                UNCW Environmental Health & Safety{status_text}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== EMERGENCY BANNER ====================
    st.markdown("""
    <div class="emergency-banner">
        <span style="font-size: 1.3rem; margin-right: 10px;">🚨</span>
        EMERGENCY: If you smell gas, feel dizzy, or your CO detector alarms — EVACUATE IMMEDIATELY and call 911
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== RESOURCE BAR ====================
    st.markdown("""
    <div class="resource-bar">
        <a class="resource-link" href="https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage/safe-generator-use.html" target="_blank">📘 Red Cross Generator Safety</a>
        <a class="resource-link" href="https://www.nhc.noaa.gov" target="_blank">🌀 NOAA Hurricane Center</a>
        <a class="resource-link" href="https://uncw.edu/emergency-safety" target="_blank">🏛️ UNCW Emergency</a>
        <a class="resource-link" href="https://poisoncontrol.org" target="_blank">☎️ Poison Control</a>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== THREE COLUMN LAYOUT ====================
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    # ==================== LEFT COLUMN - SAFETY RULES ====================
    with col1:
        st.markdown('<div class="safety-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⚠️ Critical Safety Rules</div>', unsafe_allow_html=True)
        
        for rule in SAFETY_RULES:
            st.markdown(f"""
            <div class="rule-item">
                <span class="rule-icon">{rule['icon']}</span>
                <div class="rule-content">
                    <span class="rule-title">{rule['rule']}</span>
                    <div class="rule-detail">{rule['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== MIDDLE COLUMN - CHAT ====================
    with col2:
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        
        # Question chips
        st.markdown("<p style='font-weight: 600; margin-bottom: 0.5rem;'>Quick questions:</p>", unsafe_allow_html=True)
        
        chip_cols = st.columns(4)
        questions = [
            ("🏠 Garage", "Can I run my generator in my garage?"),
            ("🏢 Balcony", "Is it safe to use a generator on my apartment balcony?"),
            ("🏫 Dorm", "Can I use a generator in my dorm room?"),
            ("🏡 Off-campus", "I live off-campus, where should I place my generator?")
        ]
        
        for i, (label, q) in enumerate(questions):
            with chip_cols[i]:
                if st.button(label, key=f"chip_{i}", use_container_width=True):
                    st.session_state.question = q
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Chat form
        with st.form(key="chat_form", clear_on_submit=False):
            user_question = st.text_input(
                "Ask your question",
                value=st.session_state.question,
                placeholder="Example: Can I run my generator in my garage? What does CO smell like?",
                label_visibility="collapsed"
            )
            
            submitted = st.form_submit_button("💬 Get Safety Guidance", use_container_width=True)
        
        st.markdown('<div class="helper-text">Questions about placement, fuel safety, CO detectors, emergency procedures, or dorm rules</div>', unsafe_allow_html=True)
        
        # Handle submission
        if submitted and user_question:
            with st.spinner("🔍 Checking safety guidelines with Qwen3 32B..."):
                st.session_state.response = get_safety_response(user_question)
                st.session_state.question = ""  # Clear for next question
        
        # Display response
        if st.session_state.response:
            st.markdown(f"""
            <div class="response-box">
                <div class="response-title">
                    <span>⚡ Safety Guidance</span>
                    { "<span style='font-size:0.8rem; color:#5F6B7A;'>via Qwen3 32B</span>" if st.session_state.ollama_status else "" }
                </div>
                <div class="response-content">
                    {st.session_state.response}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== RIGHT COLUMN - QUICK REFERENCE ====================
    with col3:
        st.markdown('<div class="safety-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📋 Quick Reference</div>', unsafe_allow_html=True)
        
        for ref in QUICK_REFERENCE:
            st.markdown(f"""
            <div class="rule-item">
                <span class="rule-icon">{ref['icon']}</span>
                <div class="rule-content">
                    <span class="rule-title">{ref['topic']}</span>
                    <div class="rule-detail">{ref['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add timestamp
        st.markdown(f"""
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid {COLORS['border']};">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: {COLORS['text_light']}; font-size: 0.8rem;">
                <span>🕒</span>
                <span>Updated: {datetime.now().strftime('%B %Y')}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; color: {COLORS['text_light']}; font-size: 0.8rem; margin-top: 0.3rem;">
                <span>🤖</span>
                <span>Model: Qwen3 32B</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== DIVIDER ====================
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # ==================== ADDITIONAL RESOURCES ====================
    with st.expander("📚 View Additional Safety Resources"):
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.markdown("""
            **📞 Emergency Contacts**
            - **911** - Life-threatening emergencies
            - **Poison Control:** 1-800-222-1222  
            - **UNCW PD:** 910-962-2222
            - **National CO Hotline:** 1-800-638-2772
            """)
        
        with res_col2:
            st.markdown("""
            **⚠️ CO Poisoning Symptoms**
            - Headache
            - Dizziness
            - Nausea
            - Confusion
            - Chest pain
            - Loss of consciousness
            
            *Symptoms can appear flu-like*
            """)
        
        with res_col3:
            st.markdown("""
            **📋 Generator Checklist**
            - [ ] 20+ feet from home
            - [ ] On dry, level surface
            - [ ] CO detectors working
            - [ ] Fuel stored safely
            - [ ] Weather protected
            - [ ] Carbon monoxide alarm
            """)
    
    # ==================== FOOTER ====================
    st.markdown("""
    <div class="footer">
        <div style="max-width: 1200px; margin: 0 auto;">
            <p style="font-size: 0.95rem; opacity: 0.9;">
                ⚡ Official guidance adapted from American Red Cross, CDC, NFPA, and NOAA
            </p>
            <p style="font-size: 0.85rem; opacity: 0.7; margin: 1rem 0;">
                Always follow manufacturer instructions and local building codes
            </p>
            <div class="footer-links">
                <a href="https://www.nhc.noaa.gov" target="_blank">📡 NOAA Hurricane Center</a>
                <a href="https://uncw.edu/emergency-safety" target="_blank">🏛️ UNCW Emergency</a>
                <a href="https://www.cdc.gov/co" target="_blank">🏥 CDC CO Poisoning</a>
            </div>
            <p style="margin-top: 1.5rem; font-size: 0.75rem; opacity: 0.5;">
                In case of emergency, call 911. This tool provides general safety information for educational purposes.
                Last updated: February 2026
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== RUN APP ====================
if __name__ == "__main__":
    main()
