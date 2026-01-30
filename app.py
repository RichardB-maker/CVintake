import streamlit as st
from audio_recorder_streamlit import audio_recorder
import google.generativeai as genai

# Je geheime sleutel ophalen uit de instellingen
api_key = st.secrets["AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw"]
genai.configure(api_key=api_key)

st.title("Sprekend CV 🎙️")

st.write("Klik op de microfoon en vertel iets over jezelf.")

# Geluid opnemen
audio_bytes = audio_recorder(text="Klik en praat", icon_size="2x")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    if st.button("Maak tekst van mijn spraak"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # De AI vragen om het geluid om te zetten naar tekst
        # Let op: dit is een simpel voorbeeld, Gemini kan bestanden lezen!
        response = model.generate_content([
            "Wat wordt er gezegd in dit fragment? Schrijf het kort op voor een CV.",
            {"mime_type": "audio/wav", "data": audio_bytes}
        ])
        
        st.subheader("Dit heb ik gehoord:")
        st.write(response.text)
