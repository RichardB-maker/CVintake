import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
API_KEY = "AIzaSyAgG36HsdKnA2-loH5f7D-8L97LpCgOzLw" 
genai.configure(api_key=API_KEY)

# We gebruiken hier de meest stabiele modelnaam
MODEL_NAME = 'gemini-1.5-flash-latest'

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Gebruik korte zinnen. Stel één vraag tegelijk.
Zodra je alle info hebt, maak je een overzicht met de titel: 'JOUW NIEUWE CV'.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje voor je CV. Hoe heet je?"}]

# --- 2. VOORLEES-FUNCTIE (HTML/JS) ---
def speak_text(text):
    # Dit stukje code laat de browser de tekst hardop uitspreken
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = 'nl-NL';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

# Toon chat en lees het laatste bericht voor als het van de AI is
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Spreek alleen het allerlaatste bericht van de assistent uit
        if i == len(st.session_state.messages) - 1 and message["role"] == "assistant":
            speak_text(message["content"])

# --- 3. INPUT ---
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
            st.error(f"Audio fout: Probeer het te typen.")

if prompt:
    user_input = prompt

# --- 4. VERWERKING ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nCoach:"
            
            response = model.generate_content(full_query)
            ai_text = response.text
            
            with st.chat_message("assistant"):
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                st.rerun() # Rerun om de voorlees-functie te triggeren
        except Exception as e:
            st.error(f"Fout: {e}")

# --- 5. DOWNLOAD ---
if "JOUW NIEUWE CV" in st.session_state.messages[-1]["content"].upper():
    st.download_button("📄 Download CV", st.session_state.messages[-1]["content"], file_name="cv.txt")
