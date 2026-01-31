import streamlit as st
import google.generativeai as genai

# 1. Instellingen & API Key
# Gebruik st.secrets op Streamlit Cloud of plak je key hier direct voor een lokale test
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw" 
genai.configure(api_key=API_KEY)

# 2. De Instructies voor de AI (System Prompt)
SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Jouw doel is om via een gesprek alle info voor een CV te verzamelen.
Regels:
- Gebruik korte zinnen en simpele woorden (geen moeilijke woorden).
- Stel altijd maar één vraag tegelijk.
- Wees heel positief en bemoedigend.
- Vraag naar: Naam, wat voor werk iemand zoekt, werkervaring en sterke punten.
- Zodra je alles weet, zeg je: 'Bedankt! Ik ga nu je CV maken.' en toon je een simpel overzicht.
"""

st.set_page_config(page_title="AI CV Hulp", page_icon="🎤")
st.title("🎤 Jouw CV Coach")
st.write("Hoi! Ik help je om een mooi CV te maken door gewoon even te kletsen.")

# 3. Chat geschiedenis initialiseren
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Startbericht van de AI
    initial_text = "Hoi! Ik ben je hulpje voor je CV. Om te beginnen: wat is je naam?"
    st.session_state.messages.append({"role": "assistant", "content": initial_text})

# Chat geschiedenis tonen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Input van de gebruiker
if prompt := st.chat_input("Typ hier je antwoord..."):
    # Voeg gebruikersbericht toe aan geschiedenis
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Gemini aanroepen met de hele context
    with st.spinner("Nadenken..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # We bouwen de context op voor Gemini
        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        full_query = f"{SYSTEM_PROMPT}\n\nGeschiedenis van het gesprek:\n{history_context}\n\nCoach:"
        
        response = model.generate_content(full_query)
        
        # Antwoord tonen en opslaan
        with st.chat_message("assistant"):
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
