import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE (DE VEILIGE METHODE) ---
# Stap A: Probeer de sleutel uit de 'Secrets' van Streamlit te halen (voor online gebruik)
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"]
else:
    # Stap B: Als de secret niet bestaat (lokaal testen), gebruik dan deze variabele
    # LET OP: Plak hier je NIEUWE sleutel als je lokaal test, 
    # maar gebruik liever de Secrets in de Streamlit Cloud console.
    API_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"

# Configureer de AI met de sleutel
genai.configure(api_key=API_KEY)

# Gebruik Gemini 1.5 Flash (deze is het meest stabiel voor de gratis versie)
MODEL_NAME = 'gemini-1.5-flash'

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Korte zinnen, één vraag tegelijk. 
Doel: verzamel Naam, Werkervaring en Vaardigheden.
"""

st.set_page_config(page_title="CV Coach", page_icon="🎤")
st.title("🎤 Jouw CV Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje. Hoe heet je?"}]

# Chat tonen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. INPUT ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎤 Praat", stop_prompt="🛑 Stop", key='recorder')
prompt = st.chat_input("Of typ hier...")

user_input = None

if audio_input:
    with st.spinner("Ik luister..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content([
                SYSTEM_PROMPT,
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except Exception as e:
            if "429" in str(e):
                st.error("Rustig aan! Wacht even 30 seconden en probeer het dan opnieuw.")
            else:
                st.error("Er ging iets mis. Probeer het te typen.")

if prompt:
    user_input = prompt

# --- 3. VERWERKING ---
if user_input:
    # Voeg gebruiker toe
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            # Alleen de laatste 5 berichten meesturen om data (en quota) te besparen
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nCoach:"
            
            response = model.generate_content(full_query)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("De AI is even moe (Quota bereikt). Wacht een minuutje.")

# --- 4. EXPORT ---
last_msg = st.session_state.messages[-1]["content"].upper()
if "JOUW NIEUWE CV" in last_msg or "CV:" in last_msg:
    st.download_button("📄 Download CV", st.session_state.messages[-1]["content"], file_name="cv.txt")
