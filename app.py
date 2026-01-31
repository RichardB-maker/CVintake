import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
# Gebruik je eigen sleutel hier
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw" 
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Gebruik korte zinnen. Stel één vraag tegelijk.
Zodra je alle info hebt, maak je een overzicht met de titel: 'JOUW NIEUWE CV'.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")

# Chat geschiedenis initialiseren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje. Hoe heet je?"}]

# Toon chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. INPUT SECTIE ---
st.write("---")
col1, col2 = st.columns([1, 4])
with col1:
    audio_input = mic_recorder(start_prompt="🎤 Praat", stop_prompt="🛑 Stop", key='recorder')

prompt = st.chat_input("Of typ hier je antwoord...")

user_input = None

# Audio verwerking
if audio_input:
    with st.spinner("Ik luister naar je..."):
        try:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            response = model.generate_content([
                SYSTEM_PROMPT,
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except Exception as e:
            st.error("Het lukte even niet met de microfoon. Kun je het typen?")

# Tekst verwerking
if prompt:
    user_input = prompt

# --- 3. AI ANTWOORD GENEREREN ---
if user_input:
    # Voeg gebruiker toe aan chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        try:
            # Belangrijk: we voegen 'models/' toe voor de zekerheid
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            # Context opbouwen
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            full_query = f"{SYSTEM_PROMPT}\n\nGeschiedenis:\n{history}\n\nCoach:"
            
            response = model.generate_content(full_query)
            ai_text = response.text
            
            with st.chat_message("assistant"):
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
        except Exception as e:
            st.error(f"Er ging iets mis bij Google: {e}")

# --- 4. EXPORT ---
if len(st.session_state.messages) > 0:
    last_msg = st.session_state.messages[-1]["content"]
    if "JOUW NIEUWE CV" in last_msg.upper():
        st.download_button("📄 Download CV", last_msg, file_name="cv.txt")
