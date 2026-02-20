import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="UNCW Generator Safety Guide",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Dark Mode ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #1A1A1A !important;
        color: #E0E0E0 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #202020 !important;
        border-right: 1px solid #333333;
        padding: 2rem 1rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #252525 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* User messages */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"]):nth-child(odd) {
        background-color: #282828 !important;
        border-left: 4px solid #4A90E2;
    }
    
    /* Assistant messages */
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"]):nth-child(even) {
        background-color: #232323 !important;
        border-left: 4px solid #50C878;
    }
    
    /* Chat input */
    .stChatInputContainer {
        padding: 1rem 0;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .stChatInputContainer input {
        background-color: #252525 !important;
        color: #E0E0E0 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
        padding: 12px;
    }
    
    /* Sidebar links */
    .sidebar-links a {
        color: #4A90E2 !important;
        text-decoration: none;
        display: block;
        padding: 10px 0;
        border-bottom: 1px solid #333333;
    }
    
    .sidebar-links a:hover {
        color: #7FB3D5 !important;
        padding-left: 5px;
        transition: 0.2s;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FFFFFF !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: #A0A0A0;
        border-top: 1px solid #333333;
        margin-top: 40px;
    }
    
    .footer a {
        color: #4A90E2 !important;
        text-decoration: none;
        margin: 0 10px;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Emergency banner */
    .emergency-banner {
        background-color: #C0392B;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #252525 !important;
        color: #E0E0E0 !important;
        border: 1px solid #333333 !important;
        border-radius: 6px;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #333333 !important;
        border-color: #4A90E2 !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #282828 !important;
        border: 1px solid #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I'm your UNCW Generator Safety Guide. How can I help with generator safety today?"}
    ]

# --- GROQ API ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- SYSTEM PROMPT (No <think> tags, direct responses) ---
SYSTEM_PROMPT = """You are an AI assistant for UNCW students on generator safety during hurricanes. Respond directly to any message. Focus on safety advice. Never use <think> tags or show reasoning. Provide clear, practical guidance.

[ROLE]
Provide guidance on safe generator use, setup, operation, maintenance, and fuel handling.

[GOAL]
Identify two immediate safety actions. Prioritize urgent risks.

[DEFINITIONS]
Carbon monoxide (CO) — Colorless, odorless gas; causes headaches, dizziness, death.
Portable generator — Use outdoors only, 20+ feet from home.
CO detector — Install on every level.
Backfeed — Never plug into wall outlet.
Refueling — Cool 15+ minutes first.
Wet conditions — Keep dry.

[CONSTRAINTS]
No indoor use. No medical advice; call 911. No forecasts; refer to NOAA. No brands.

[TASK]
Answer on generator safety. Give urgent warnings for dangers.

[PROCESS]
1. Assess situation.
2. Detect dangers.
3. Warn if needed.
4. Provide two actions.
5. End with reminder."""

# --- SIDEBAR (Resources and Safety Stuff) ---
with st.sidebar:
    st.markdown("## ⚡ Generator Safety Resources")
    st.markdown("---")
    
    st.markdown("### 🛡️ Health & Safety Tips")
    st.info(
        "• Always outdoors, 20+ ft from home\n"
        "• CO detectors on every level\n"
        "• Cool before refueling\n"
        "• No backfeeding\n"
        "• Dry conditions only"
    )
    
    st.markdown("### 🔗 Official Links")
    st.markdown("""
    <div class="sidebar-links">
        <a href="https://uncw.edu/emergency-safety" target="_blank">UNCW Emergency</a>
        <a href="https://www.nhc.noaa.gov" target="_blank">National Hurricane Center</a>
        <a href="https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage/safe-generator-use.html" target="_blank">Red Cross Guide</a>
        <a href="https://uncw.edu/about/university-administration/business-affairs/environmental-health-safety/ems/severe-weather/hurricane" target="_blank">UNCW Hurricane Prep</a>
        <a href="https://www.cdc.gov/co/generatorsafetyfactsheet.html" target="_blank">CDC CO Safety</a>
        <a href="https://www.fema.gov/fact-sheet/generator-safety" target="_blank">FEMA Generator Tips</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚨 Emergency Contacts")
    st.markdown("**911** for emergencies")
    st.markdown("**Poison Control:** 1-800-222-1222")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello, I'm your UNCW Generator Safety Guide. How can I help with generator safety today?"}
        ]
        st.rerun()

# --- MAIN CHAT AREA ---
st.title("⚡ UNCW Generator Safety Guide")
st.caption("Professional guidance on safe generator use during emergencies")

# Emergency banner
st.markdown("""
<div class="emergency-banner">
    ⚠️ If dizzy, headache, or nauseous - GET FRESH AIR & CALL 911 IMMEDIATELY ⚠️
</div>
""", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about generator safety..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Handle emergencies directly
    lower_prompt = prompt.lower()
    if any(word in lower_prompt for word in ["headache", "dizzy", "nausea", "sick"]):
        response = "🚨 POTENTIAL CO POISONING: Get fresh air now. Call 911. Do not re-enter until cleared."
    elif any(word in lower_prompt for word in ["inside", "garage", "basement", "indoors"]):
        response = "⚠️ DANGER: Turn off generator. Move outdoors 20+ ft from home. Indoor use kills."
    else:
        # Call Groq API for fast response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages[-5:]:
                    messages_for_api.append({"role": msg["role"], "content": msg["content"]})
                
                payload = {
                    "model": "mixtral-8x7b-32768",  # Fast Groq model
                    "messages": messages_for_api,
                    "temperature": 0.3,
                    "max_tokens": 1024,
                    "stream": True
                }
                
                response = requests.post(GROQ_API_URL, headers=headers, json=payload, stream=True, timeout=30)
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith("data: "):
                                line = line[6:]
                            if line == "[DONE]":
                                break
                            json_response = json.loads(line)
                            if "choices" in json_response:
                                chunk = json_response["choices"][0]["delta"].get("content", "")
                                full_response += chunk
                                message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                else:
                    full_response = "Error: Could not generate response. Follow basic safety: Outdoors only, CO detectors installed."
                    message_placeholder.markdown(full_response)
            except:
                full_response = "Connection issue. Key safety: Generator outdoors 20+ ft, cool before refuel."
                message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response or response})

# --- FOOTER ---
st.markdown("""
<div class="footer">
    <strong>Resources:</strong>
    <a href="https://uncw.edu/emergency-safety" target="_blank">UNCW Emergency</a> |
    <a href="https://www.nhc.noaa.gov" target="_blank">NHC</a> |
    <a href="https://www.redcross.org" target="_blank">Red Cross</a> |
    <a href="https://uncw.edu" target="_blank">UNCW Guide</a>
    <br>
    Emergency: 911 | Poison: 1-800-222-1222 | Updated: Feb 2026
</div>
""", unsafe_allow_html=True)
