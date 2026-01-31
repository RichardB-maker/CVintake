import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw" 
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Gebruik korte zinnen. Stel één vraag tegelijk.
Zodra je alle info hebt, maak je een duidelijk overzicht met de titel: 'JOUW NIEUWE CV'.
Zorg dat dit overzicht heel overzichtelijk is met dikgedrukte koppen.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje. Hoe heet je?"}]

# Toon chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. INPUT ---
audio_input = mic_recorder(start_prompt="👉 Praat tegen mij", stop_prompt="🛑 Stop", key='recorder')
prompt = st.chat_input("Of typ hier...")

user_input = None
if audio_input:
    with st.spinner("Ik luister..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        try:
            response = model.generate_content([
                SYSTEM_PROMPT + "\nDe gebruiker spreekt. Beantwoord de vraag of vraag door.",
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except:
            st.error("Ik kon je niet goed horen. Probeer het nog eens of typ je antwoord.")

if prompt:
    user_input = prompt

# --- 3. VERWERKING ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{context}\n\nCoach:"
        
        response = model.generate_content(full_query)
        ai_text = response.text
        
        with st.chat_message("assistant"):
            st.markdown(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

# --- 4. EXPORT (De Download Knop) ---
# We checken of het laatste bericht een CV bevat
last_message = st.session_state.messages[-1]["content"]
if "JOUW NIEUWE CV" in last_message.upper():
    st.success("Je CV is klaar! Je kunt het hieronder opslaan.")
    st.download_button(
        label="📄 Download mijn CV als tekstbestand",
        data=last_message,
        file_name="mijn_nieuw_cv.txt",
        mime="text/plain"
    )
