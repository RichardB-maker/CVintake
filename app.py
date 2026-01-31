import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
API_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"
# Gebruik transport='rest' om v1beta/gRPC problemen te voorkomen
genai.configure(api_key=API_KEY, transport='rest')

SYSTEM_PROMPT = """
Jij bent een empathische CV-coach voor laaggeletterden. 
Gebruik korte zinnen. Stel één vraag tegelijk.
Zodra je alle info hebt, maak je een overzicht met de titel: 'JOUW NIEUWE CV'.
"""

st.set_page_config(page_title="AI CV Coach", page_icon="🎤")
st.title("🎤 Jouw AI CV Coach")

# Functie om het juiste model te vinden
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # We zoeken eerst naar flash, dan naar pro
        for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in available_models:
                return target
        return available_models[0] if available_models else 'gemini-1.5-flash'
    except:
        return 'gemini-1.5-flash'

WORKING_MODEL = get_working_model()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je hulpje voor je CV. Hoe heet je?"}]

# --- 2. VOORLEES-FUNCTIE ---
def speak_text(text):
    clean_text = text.replace('"', "'").replace("\n", " ")
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{clean_text}");
    msg.lang = 'nl-NL';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

# Toon chat
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if i == len(st.session_state.messages) - 1 and message["role"] == "assistant":
            speak_text(message["content"])

# --- 3. INPUT ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎤 Praat tegen mij", stop_prompt="🛑 Stop", key='recorder')
prompt = st.chat_input("Of typ hier...")

user_input = None
if audio_input:
    with st.spinner("Ik luister..."):
        try:
            model = genai.GenerativeModel(WORKING_MODEL)
            response = model.generate_content([
                SYSTEM_PROMPT,
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_input = response.text
        except Exception as e:
            st.error(f"Microfoon werkte niet: {e}. Typ a.u.b. je antwoord.")

if prompt:
    user_input = prompt

# --- 4. VERWERKING ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Nadenken..."):
        try:
            model = genai.GenerativeModel(WORKING_MODEL)
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nCoach:"
            
            response = model.generate_content(full_query)
            ai_text = response.text
            
            with st.chat_message("assistant"):
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
                st.rerun()
        except Exception as e:
            st.error(f"Fout bij verbinden met AI: {e}")

# --- 5. DOWNLOAD ---
if "JOUW NIEUWE CV" in st.session_state.messages[-1]["content"].upper():
    st.download_button("📄 Download mijn CV", st.session_state.messages[-1]["content"], file_name="cv.txt")
