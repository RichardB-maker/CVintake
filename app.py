
# --- 1. CONFIGURATIE & SETUP ---
# Haal de sleutels op uit Streamlit Secrets
import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import requests
import base64

# --- 1. CONFIGURATIE ---
GEMINI_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"
ELEVEN_KEY = "sk_722508e8af2591b1e34e0b36ca75b0518e8266c20964b162"
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

if not GEMINI_KEY or not ELEVEN_KEY:
    st.error("⚠️ API-sleutels ontbreken in de Secrets!")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

def get_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = "Jij bent een HR-interviewer. Stel 1 vraag tegelijk. Eindig met een CV."

st.set_page_config(page_title="AI HR Coach", page_icon="🎙️")
st.title("🎙️ Live HR Interview")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je HR-coach. Wat voor werk zoek je?"}]

# --- 2. HULPFUNCTIES ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.content if response.status_code == 200 else None
    except: return None

def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- 3. DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. INTERVIEW LOGICA ---
st.write("---")

# CRUCIALE FIX: Gebruik een container die we leeg kunnen maken
ui_container = st.empty()

with ui_container.container():
    # De key verandert nu ELKE keer dat de chat-historie verandert
    m_key = f"mic_{len(st.session_state.messages)}"
    audio_input = mic_recorder(start_prompt="🎤 Praat", stop_prompt="🛑 Stop", key=m_key)
    text_input = st.chat_input("Of typ hier...")

user_reply = None

if audio_input:
    model = get_model()
    try:
        response = model.generate_content(["Schrijf op:", {"mime_type": "audio/wav", "data": audio_input['bytes']}])
        user_reply = response.text
    except: st.error("Spraakherkenning mislukt.")

if text_input:
    user_reply = text_input

if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    
    with st.spinner("Coach denkt na..."):
        model = get_model()
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
        ai_message = model.generate_content(f"{SYSTEM_PROMPT}\n\n{history}").text
        
        st.session_state.messages.append({"role": "assistant", "content": ai_message})
        
        audio_content = text_to_speech(ai_message)
        if audio_content:
            autoplay_audio(audio_content)
        
        # FIX: Maak de container leeg voordat we de rerun doen
        ui_container.empty()
        st.rerun()
