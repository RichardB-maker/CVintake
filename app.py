import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.title("De Sprekende CV-Helper 🎙️")
st.write("Klik op de microfoon en vertel me wie je bent en wat je kunt!")

# 1. Naam opnemen
st.subheader("1. Hoe heet je?")
audio_naam = audio_recorder(text="Klik om je naam in te spreken")

# 2. Werkervaring opnemen
st.subheader("2. Wat voor werk heb je gedaan?")
audio_werk = audio_recorder(text="Vertel hier over je vorige baan")

# Een knop om alles te verwerken
if st.button("Maak mijn CV"):
    st.success("Wat goed! Ik ga nu je spraak omzetten naar tekst.")
    # Hier komt de AI die van geluid tekst maakt
    st.write("Je CV wordt nu gemaakt...")
