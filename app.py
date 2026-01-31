
import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import requests
import base64

# --- 1. CONFIGURATIE ---
GEMINI_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"
ELEVEN_KEY ="sk_722508e8af2591b1e34e0b36ca75b0518e8266c20964b162"
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Marcus (NL stem)

if not GEMINI_KEY or not ELEVEN_KEY:
    st.error("⚠️ API-sleutels ontbreken in de Secrets!")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

# Hulpfunctie om het juiste model te vinden (voorkomt 404)
def get_model():
    try:
        # De meest stabiele naam voor het gratis 1.5 model
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        # Backup voor het geval dat 1.5-flash niet beschikbaar is in jouw regio
        return genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = """
Jij bent een empathische HR-interviewer. Voer een kort en krachtig gesprek.
Stel één vraag tegelijk over: naam, ervaring en passies.
Eindig na 5-6 vragen met een overzichtelijk CV in Markdown.
"""

st.set_page_config(page_title="AI HR Interview", page_icon="🎙️")
st.title("🎙️ Live HR Interview")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je HR-coach. Wat leuk dat je er bent. Vertel eens, wat voor werk zoek je?"}]

# --- 2. AUDIO FUNCTIES ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- 3. CHAT DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. INTERVIEW LOGICA ---
st.write("---")
recorder_key = f"mic_{len(st.session_state.messages)}"
audio_input = mic_recorder(start_prompt="🎤 Praat", stop_prompt="🛑 Stop", key=recorder_key)
text_input = st.chat_input("Of typ hier...")

user_reply = None

if audio_input:
    with st.spinner("Ik luister..."):
        model = get_model()
        try:
            response = model.generate_content([
                "Schrijf exact op wat de gebruiker zegt. Geef alleen de tekst.", 
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_reply = response.text
        except:
            st.error("Audio niet verstaan. Typ a.u.b. je antwoord.")

if text_input:
    user_reply = text_input

if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    with st.chat_message("user"):
        st.markdown(user_reply)

    with st.spinner("De coach denkt na..."):
        try:
            model = get_model()
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-8:]])
            full_query = f"{SYSTEM_PROMPT}\n\nHistorie:\n{history}\n\nInterviewer:"
            
            ai_message = model.generate_content(full_query).text
            
            with st.chat_message("assistant"):
                st.markdown(ai_message)
                st.session_state.messages.append({"role": "assistant", "content": ai_message})
                
                audio_content = text_to_speech(ai_message)
                if audio_content:
                    autoplay_audio(audio_content)
                
                st.rerun()
        except Exception as e:
            st.error(f"Fout: {e}")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Marcus (warme NL stem)

if not GEMINI_KEY or not ELEVEN_KEY:
    st.error("⚠️ API-sleutels ontbreken in de Secrets! Controleer GEMINI_API_KEY en ELEVEN_API_KEY.")
    st.stop()

# Initialiseer Google AI
genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """
Jij bent een empathische HR-interviewer. Jouw doel is een natuurlijk gesprek.
Verzin zelfstandig vragen om een beeld te krijgen van iemands:
1. Achtergrond en dromen.
2. Werkervaring en talenten.
3. Hobby's (vertaal deze naar werk-competenties).
Stel slechts ÉÉN vraag tegelijk. Reageer op de input van de gebruiker.
Houd je vragen kort en krachtig.
Eindig pas na ongeveer 6 vragen met een professioneel CV in Markdown-format.
"""

st.set_page_config(page_title="AI HR Coach", page_icon="🎙️")
st.title("🎙️ Live HR Interview")

# Chat geschiedenis initialiseren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je HR-coach. Wat leuk dat je er bent. Vertel eens, wie ben je en wat voor werk zou je het liefste doen?"}]

# --- 2. AUDIO FUNCTIES ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
    except Exception:
        return None
    return None

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

# Unieke key voor de recorder om DuplicateKeyError te voorkomen
recorder_key = f"mic_{len(st.session_state.messages)}"
audio_input = mic_recorder(start_prompt="🎤 Praat", stop_prompt="🛑 Stop", key=recorder_key)
text_input = st.chat_input("Of typ je antwoord...")

user_reply = None

# A. Spraak naar Tekst (via Gemini)
if audio_input:
    with st.spinner("Ik luister..."):
        # Gebruik de volledige padnaam voor het model
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        try:
            response = model.generate_content([
                "Schrijf exact op wat de gebruiker zegt. Geef alleen de tekst terug.", 
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_reply = response.text
        except Exception as e:
            st.error(f"Spraakherkenning mislukt. Typ a.u.b. je antwoord.")

# B. Tekst input
if text_input:
    user_reply = text_input

# C. AI Antwoord genereren
if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    with st.chat_message("user"):
        st.markdown(user_reply)

    with st.spinner("De coach denkt na..."):
        try:
            # Gebruik ook hier het volledige pad voor het model
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprekshistorie:\n{history}\n\nInterviewer:"
            
            ai_message = model.generate_content(full_query).text
            
            with st.chat_message("assistant"):
                st.markdown(ai_message)
                st.session_state.messages.append({"role": "assistant", "content": ai_message})
                
                # Stem genereren en afspelen
                audio_content = text_to_speech(ai_message)
                if audio_content:
                    autoplay_audio(audio_content)
                
                # Scherm herladen om de audio te triggeren en de mic te resetten
                st.rerun()
        except Exception as e:
            st.error(f"Fout bij praten met de AI: {e}")
