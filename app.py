import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw" 
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Jouw doel: via een gesprek alle info voor een CV verzamelen.
Regels:
- Gebruik korte zinnen en simpele woorden (geen vaktaal).
- Stel altijd maar één vraag tegelijk.
- Vraag naar: Naam, wat voor werk iemand zoekt, eerdere banen/ervaring en sterke punten.
- Als je alle info hebt, maak dan een overzichtelijk CV-schema.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")
st.write("Hoi! Klik op de microfoon om te praten of typ je antwoord onderaan.")

# --- 2. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hoi! Ik ben je hulpje voor je CV. Om te beginnen: hoe heet je?"}
    ]

# Toon alle berichten
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. INPUT: MICROFOON ---
st.write("---")
audio_input = mic_recorder(
    start_prompt="👉 Klik om te praten",
    stop_prompt="🛑 Stop met praten",
    key='recorder'
)

# --- 4. LOGICA ---
user_input = None

# A. Als er audio is opgenomen
if audio_input:
    # In een prototype sturen we de audio naar Gemini (Gemini 1.5 kan audio direct lezen!)
    with st.spinner("Ik ben aan het luisteren..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        try:
            # We sturen de audio data direct naar Gemini
            response = model.generate_content([
                SYSTEM_PROMPT + "\nDe gebruiker heeft dit ingesproken. Reageer op de inhoud.",
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except Exception as e:
            st.error(f"Oeps, ik kon de audio niet goed horen. Probeer het eens te typen?")

# B. Als er getypt wordt
if prompt := st.chat_input("Of typ hier je antwoord..."):
    user_input = prompt

# --- 5. AI ANTWOORD GENEREREN ---
if user_input:
    # Voeg gebruikersinput toe aan de chat
    if not audio_input: # Voorkom dubbele weergave bij audio
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

    # Vraag Gemini om een reactie
    with st.spinner("Nadenken..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        # We bouwen de context op
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{context}\n\nCoach:"
        
        response = model.generate_content(full_query)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
