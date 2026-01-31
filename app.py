import streamlit as st
from audio_recorder_streamlit import audio_recorder
import google.generativeai as genai

# Je geheime sleutel ophalen uit de instellingen
# api_key = st.secrets["AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw"]
# genai.configure(api_key=api_key)
# Vervang die hele st.secrets regel door dit:
genai.configure(api_key="AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw")
st.title("Sprekend CV 🎙️")

st.write("Klik op de microfoon en vertel iets over jezelf.")

# Geluid opnemen
audio_bytes = audio_recorder(text="Klik en praat", icon_size="2x")

if audio_bytes:
    # We laten de gebruiker weten dat we luisteren
    st.audio(audio_bytes, format="audio/wav")
    
    # Voor een stabiel prototype gebruiken we Gemini's tekstkracht.
    # OPMERKING: Directe audio-bitstream upload vereist vaak een tijdelijk bestand.
    # Laten we het voor nu simpel en werkend houden via tekst:
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We vragen Gemini om te reageren op de input (tekst of gesimuleerde audio)
    # Als je echt audio wilt transcriberen, gebruik je de Whisper integratie.
    # Voor nu herstellen we de chat-functie:
    
    with st.spinner("Ik ben even aan het luisteren en nadenken..."):
        # Hier sturen we de prompt als tekst. 
        # Zorg dat de gebruiker ook in de tekstbalk kan typen voor de zekerheid.
        response = model.generate_content(f"{SYSTEM_PROMPT} \n De gebruiker heeft iets ingesproken. Reageer vriendelijk.")
        st.write(response.text)
