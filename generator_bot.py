import streamlit as st
import requests
import json
from datetime import datetime
import time

# --- Page Configuration (Professional Dark Mode) ---
st.set_page_config(
    page_title="UNCW Generator Safety Guide",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for DeepSeek-style Dark Mode ---
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #252525 !important;
        border-right: 1px solid #3A3A3A;
    }
    .stChatMessage {
        background-color: #2D2D2D !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    div[data-testid="stChatMessage"] {
        background-color: #2A2A2A !important;
    }
    .stChatMessage:has(div[data-testid="stChatMessageContent"]):nth-child(even) {
        background-color: #252525 !important;
        border-left: 4px solid #00A36C;
    }
    .stTextInput > div > div > input {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 8px;
        padding: 12px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0078D7 !important;
        box-shadow: 0 0 0 2px rgba(0,120,215,0.3);
    }
    .stButton > button {
        background-color: #0078D7 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #005A9E !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    a {
        color: #4CAF50 !important;
        text-decoration: none;
        border-bottom: 1px dotted #4CAF50;
    }
    a:hover {
        color: #81C784 !important;
        border-bottom: 1px solid #81C784;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 400 !important;
        border-bottom: 1px solid #3A3A3A;
        padding-bottom: 10px;
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "⚡ Hello, I'm your UNCW Generator Safety Guide. I'm here to help you stay safe during hurricanes and power outages. Before we begin, please tell me: Are you dealing with a power outage right now, or are you preparing before a hurricane? Is your generator currently running?"}
    ]

# --- GROQ API CONFIGURATION ---
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- COMPLETE SYSTEM PROMPT (from your document) ---
SYSTEM_PROMPT = """[ROLE]
You are an AI assistant for students at UNCW, providing clear, practical guidance on safe generator use during hurricanes or emergencies. You focus on safety, proper setup, operation, maintenance, and fuel handling, giving students actionable steps to prevent accidents, carbon monoxide poisoning, or fire hazards. You explain instructions clearly and concisely, prioritizing the most critical safety actions first, and reference official guidelines when possible.

[GOAL]
Identify exactly two specific safety or preparedness actions that the student can take immediately to improve their readiness for using a generator during a hurricane. Each action must be practical, actionable, and achievable today, such as repositioning the generator, checking fuel storage, or setting up safety equipment. Each action should clearly explain what to do, why it matters, and how to apply it safely, so the student can complete it without delay. Prioritize the action that addresses the most urgent safety risk first.

[DEFINITIONS]
Carbon monoxide (CO) — A colorless, odorless, poisonous gas produced by burning fuel in generators; called the "silent killer" because it can't be seen or smelled. It binds to blood 250 times more strongly than oxygen, causing headaches, dizziness, nausea, unconsciousness, or death in minutes. Primary cause of generator-related fatalities during hurricanes. 
Portable generator — A fuel-powered (usually gasoline) device that produces electricity during outages; must be used outdoors only to avoid CO buildup. Never indoors, in garages, basements, sheds, or partially enclosed spaces—even with doors/windows open. 
Carbon monoxide poisoning — Illness or death from inhaling CO fumes; symptoms mimic flu or intoxication. Prevent by placing generator ≥20 feet from doors, windows, vents; directing exhaust away; installing battery-powered CO detectors on every home level. 
Backfeed (or backfeeding) — Dangerous situation where generator power flows backward into utility lines, electrocuting repair workers or starting fires. Prevent by never plugging generator into a wall outlet; use transfer switch or plug appliances directly. 
Grounding — Connecting generator to earth/ground per manufacturer instructions to prevent electric shock. Use grounded extension cords and follow manual for setup. 
Approved fuel container — DOT- or EPA-approved gas can (typically ≤5 gallons) for safe storage; store fuel outside home in cool, ventilated, secure spot away from generator/appliances to avoid vapors igniting or spills. 
Refueling hazard — Risk of fire/explosion from adding fuel to hot engine. Always shut off generator, let cool ≥10-30 minutes (per manual), then refuel outdoors away from ignition sources. 
Wet conditions hazard — Risk of electrocution when generator/equipment is wet from rain/flooding. Operate only on dry surface, under cover (not enclosed), keep extension cords dry, never touch with wet hands. 
Hurricane Watch — NOAA announcement that hurricane conditions (winds ≥74 mph) are possible in area within 48 hours; time to finalize generator setup and safety checks. 
Hurricane Warning — NOAA announcement that hurricane conditions are expected in area within 36 hours; take immediate protective actions, including generator positioning. 
UNCW (University of North Carolina Wilmington) — Local university in Wilmington, NC; students should note coastal flood risks, frequent outages from hurricanes, and follow university emergency alerts for campus-specific guidance. 
New Hanover County — County containing Wilmington/UNCW; local emergency management issues hurricane alerts, evacuation orders, and recovery info relevant to off-campus students. 
CO detector (carbon monoxide alarm) — Battery-powered or plug-in device with battery backup that sounds alarm for dangerous CO levels; install on every level and near sleeping areas; test monthly and replace batteries as needed.

[CONSTRAINTS]
Do not provide advice on modifying, repairing, or customizing generators; direct users to licensed professionals or manufacturer support.
Do not recommend using generators indoors, in enclosed spaces, or near windows/doors under any circumstances.
Do not speculate on hurricane forecasts, evacuation orders, or power outage durations; refer users to NOAA, New Hanover County Emergency Management, or UNCW alerts.
Do not answer questions outside generator safety, setup, operation, maintenance, or fuel handling during emergencies (e.g., general electrical wiring, fuel alternatives, or non-hurricane disasters).
Do not endorse specific generator brands, models, or retailers; stick to general safety principles from official sources like FEMA, CDC, and NFPA.
Do not give medical advice for CO poisoning or injuries; instruct users to call 911 or poison control immediately.
Do not suggest bypassing safety features or using unapproved equipment/extensions.
Do not provide legal advice on liability, insurance, or regulations; refer to local authorities.

[TASK]
Answer questions about generator safety for UNCW students during hurricanes. Address proper generator placement, including the critical requirement to operate generators outdoors only, at least 20 feet from doors, windows, and vents. Explain the dangers of carbon monoxide poisoning, including symptoms, the importance of battery-powered CO detectors on every level of the home, and immediate actions to take if poisoning is suspected. Provide guidance on safe fuel handling, including approved containers, proper storage locations away from living areas, and the mandatory cooling period before refueling. Instruct on electrical safety, including proper extension cord selection, avoiding overloads, and the absolute prohibition against backfeeding (plugging into wall outlets). Explain pre-hurricane preparation steps such as test running generators, checking oil and filters, and assembling generator-specific emergency supplies. Address maintenance questions for between uses and after hurricane season. Direct students to official sources for hurricane forecasts (NOAA), local evacuation orders (New Hanover County Emergency Management), and campus closures (UNCW Alerts). When questions involve immediate danger such as indoor generator use, suspected carbon monoxide symptoms, or operating in wet conditions, provide urgent warnings with specific life-saving actions. For questions outside the bot's scope including medical advice, electrical installation, legal interpretations, or brand recommendations, refer students to appropriate professionals or authorities.

[PROCESS]
1. Initial Greeting and Situation Assessment: Begin every conversation by establishing purpose and assessing situation. Ask two critical screening questions: "Are you dealing with a power outage right now, or are you preparing before a hurricane?" and "Is your generator currently running, or are you planning to use it soon?" If the student mentions any symptoms like headache, dizziness, or nausea, immediately trigger carbon monoxide emergency protocol: direct them to leave area and call 911 before any further discussion.

2. Danger Signal Detection and Triage: After initial assessment, analyze the student's full question for specific danger signals. Scan for these red flags in order of priority: Indoor/Enclosed Space Mentions, Carbon Monoxide Indicators, Wet Conditions, Refueling Concerns, Electrical Hazards, Fuel Safety Issues. If any immediate life-threatening danger is detected, respond with an urgent warning before proceeding to any other questions.

3. Focused Information Gathering: If no immediate danger is detected, gather additional context needed to provide specific, actionable guidance. Ask targeted follow-up questions based on the topic. Limit follow-up questions to two or three. Continuously monitor for any new danger signals.

4. Actionable Instruction Delivery: Based on the assessed situation, provide two specific actions the student can take immediately. First Action (Urgent Priority): State clearly, explain step-by-step, specify where/when, connect to hazard prevented. Second Action (Reinforcing or Secondary Protection): Provide complementary action, explain how it adds safety, give timing guidance.

5. Verification and Referral: After delivering instructions, verify the student understands with one confirmation question. For questions outside scope, provide clear referral information with specific resources. End every conversation by summarizing the key safety point and encouraging safe practices: "Remember, generators belong outside only, at least 20 feet from your home, with working CO detectors inside. Stay safe during the storm." """

# --- Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/5f/UNCW_seal.svg/1200px-UNCW_seal.svg.png", width=100)
    st.title("⚡ UNCW Generator Safety")
    st.markdown("---")
    
    st.markdown("### 📌 Quick Safety Tips")
    st.info(
        "• **NEVER** run a generator indoors\n"
        "• Keep generator **20+ feet** from home\n"
        "• Install **CO detectors** on every level\n"
        "• Let generator **cool** before refueling\n"
        "• Never plug into a wall outlet"
    )
    
    st.markdown("### 🔗 Official Resources")
    st.markdown("""
    - [🏫 UNCW Hurricane Guide](https://uncw.edu/about/university-administration/business-affairs/environmental-health-safety/ems/severe-weather/hurricane)
    - [🚨 UNCW Emergency & Safety](https://uncw.edu/emergency-safety)
    - [🌪️ National Hurricane Center](https://www.nhc.noaa.gov)
    - [🪫 Red Cross Generator Safety](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage/safe-generator-use.html)
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ Powered by")
    st.markdown("**Groq + Qwen 3 32B** ⚡")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "⚡ Hello, I'm your UNCW Generator Safety Guide. I'm here to help you stay safe during hurricanes and power outages. Before we begin, please tell me: Are you dealing with a power outage right now, or are you preparing before a hurricane? Is your generator currently running?"}
        ]
        st.rerun()

# --- Main Chat Interface ---
st.title("⚡ UNCW Generator Safety Guide")
st.caption("Powered by Groq + Qwen 3 32B • Ask me anything about generator safety!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about generator safety, placement, CO detectors, fuel storage..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check for emergencies
    if any(word in prompt.lower() for word in ["headache", "dizzy", "nausea", "sick"]):
        response = """**🚨 CARBON MONOXIDE EMERGENCY 🚨**

1. **LEAVE THE AREA NOW** - Get to fresh air immediately
2. **CALL 911** - This is a medical emergency
3. **DO NOT GO BACK INSIDE**

Carbon monoxide is odorless and colorless. These symptoms mean you need fresh air NOW."""
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif any(word in prompt.lower() for word in ["inside", "garage", "basement", "room", "indoors"]):
        response = """**⚠️ IMMEDIATE DANGER ⚠️**

**STOP USING THE GENERATOR INDOORS.**

1. **TURN IT OFF** right now
2. **MOVE IT OUTSIDE** - at least 20 feet from any doors/windows
3. **OPEN WINDOWS** to ventilate if anyone feels sick

Indoor generator use KILLS. Carbon monoxide builds up in minutes."""
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        # Call Groq API
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepare the API call
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                # FIXED: Using the correct model name from your Groq screenshot
                payload = {
                    "model": "qwen/qwen3-32b",  # CORRECTED model name!
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1024,
                    "stream": True
                }
                
                # Make the request
                response = requests.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Stream the response
                    for line in response.iter_lines():
                        if line:
                            try:
                                line = line.decode('utf-8')
                                if line.startswith("data: "):
                                    line = line[6:]
                                if line == "[DONE]":
                                    break
                                    
                                json_response = json.loads(line)
                                if "choices" in json_response:
                                    chunk = json_response["choices"][0]["delta"].get("content", "")
                                    if chunk:
                                        full_response += chunk
                                        message_placeholder.markdown(full_response + "▌")
                            except:
                                continue
                    
                    # Add resource links
                    full_response += "\n\n📌 **Resources:**\n- [UNCW Emergency](https://uncw.edu/emergency-safety)\n- [Red Cross Generator Safety](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage/safe-generator-use.html)"
                    message_placeholder.markdown(full_response)
                else:
                    # If API fails, give helpful response
                    full_response = """**⚡ Generator Safety Quick Guide:**

**For your question, here are the key safety steps:**

1. **OUTDOORS ONLY** - Never inside, garage, or basement
2. **20 FEET AWAY** from doors, windows, and vents
3. **CO DETECTORS** required inside your home
4. **COOL BEFORE REFUELING** - Wait 15+ minutes
5. **NO BACKFEEDING** - Never plug into wall outlets

**Need more specific help? Ask me about:**
- Generator placement
- Fuel storage safety
- Extension cord requirements
- CO detector installation"""
                    message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"""**⚡ Generator Safety Reminder:**

While I'm having trouble connecting, remember:
- Generators go OUTSIDE only
- Keep 20+ feet from home
- Install CO detectors inside

**Error:** {str(e)}"""
                message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; padding: 20px;'>"
    "⚡ **Remember**: Generators belong OUTSIDE only, at least 20 feet from your home. Stay safe, Seahawks! ⚡"
    "</div>",
    unsafe_allow_html=True
)
