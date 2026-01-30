import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
import io

# 1. Instellingen - Plak hier je API key uit Google AI Studio
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")

# 2. De System Prompt (De 'hersenen' van je coach)
SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Regels:
- Gebruik korte zinnen en simpele woorden (geen vaktaal).
- Stel maximaal één vraag tegelijk.
- Vraag naar: Naam, wat voor werk iemand zoekt, wat iemand nu al kan (ervaring) en sterke punten.
- Als iemand iets inspreekt, reageer dan bemoedigend.
- Zodra je alle info hebt, maak je een overzichtelijk CV.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hoi! Ik ben je hulpje voor je CV. Wat is je naam?"}
    ]

st.title("🎤 Jouw AI CV Coach")
st.write("Druk op de knop hieronder en vertel je verhaal. Ik help je een mooi CV te maken!")

# 3. Chat geschiedenis weergeven
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Audio opname functie
audio_bytes = audio_recorder(text="Klik om te praten", icon_size="2x")

if audio_bytes:
    # Hier zou normaal gesproken Whisper API komen om audio naar tekst te zetten.
    # Voor dit prototype simuleren we even dat de tekst binnenkomt via de chatbalk,
    # omdat volledige audio-integratie in een browser vaak extra libraries nodig heeft.
    st.info("Audio ontvangen! (In de volledige versie wordt dit nu direct naar tekst omgezet)")

# 5. Tekst invoer (als backup en voor de test)
if prompt := st.chat_input("Typ hier je antwoord (of gebruik de microfoon)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini aanroepen
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
    
    # We sturen de hele context mee inclusief de system prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nGebruiker zegt: {prompt}"
    response = chat.send_message(full_prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
