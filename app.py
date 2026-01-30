import streamlit as st

st.title("De CV-Helper")
st.write("Beantwoord de vragen en maak je eigen CV!")

# Vragen stellen
naam = st.text_input("Wat is je naam?")
telefoon = st.text_input("Wat is je telefoonnummer?")
email = st.text_input("Wat is je e-mailadres?")
werk_keuze = st.text_input("Wat voor werk zoek je?")
ervaring = st.text_area("Wat heb je voor werk gedaan? (bijvoorbeeld: grasmaaien)")
eigenschappen = st.text_input("Waar ben je goed in? (bijvoorbeeld: hard werken)")

# Knop om CV te maken
if st.button("Maak mijn CV"):
    st.divider()
    st.header(f"CV van {naam}")
    st.subheader("Contact")
    st.write(f"📞 {telefoon}")
    st.write(f"📧 {email}")
    
    st.subheader("Over mij")
    st.write(werk_keuze)
    
    st.subheader("Werkervaring")
    st.write(ervaring)
    
    st.subheader("Eigenschappen")
    st.write(f"Ik ben goed in: {eigenschappen}")
    
    st.success("Je CV is klaar! Je kunt deze tekst nu kopiëren.")
