import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time

# --- 1. CONFIGURATIE ---
# Haal de sleutel veilig op uit Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"]
else:
    # Voor lokaal testen als je nog geen Secrets hebt ingesteld
    API_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"

genai.configure(api_key=API_KEY)
MODEL_NAME = 'gemini-1.5-flash'

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Praat simpel. Stel één vraag tegelijk.
Vraag eerst naar de naam, dan naar werkervaring, dan naar sterke punten.
Eindig altijd met de tekst 'JOUW NIEUWE CV' gevolgd door een overzicht.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje voor je CV. Hoe heet je?"}]

# Chat tonen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. INPUT ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎤 Klik en praat", stop_prompt="🛑 Klaar", key='recorder')
prompt = st.chat_input("Of typ hier...")

user_input = None

if audio_input:
    with st.spinner("Ik luister..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content([
                SYSTEM_PROMPT + "\nBeantwoord dit audiobericht kort.",
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except Exception as e:
            if "429" in str(e):
                st.warning("De AI moet even 30 seconden rusten. Probeer het zo nog eens!")
            else:
                st.error("Er ging iets mis. Probeer het te typen.")

if prompt:
    user_input = prompt

# --- 3. VERWERKING ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            # Stuur alleen de laatste 4 berichten mee om quota te besparen
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nCoach:"
            
            response = model.generate_content(full_query)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Ik ben even overbelast. Wacht 60 seconden en typ dan weer iets.")

# --- 4. DOWNLOAD ---
last_msg = st.session_state.messages[-1]["content"]
if "JOUW NIEUWE CV" in last_msg.upper():
    st.success("Gefeliciteerd! Je CV staat hieronder klaar.")
    st.download_button("📄 Download mijn CV", last_msg, file_name="mijn_cv.txt")
