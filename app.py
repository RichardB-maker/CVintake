

import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURATIE ---
# Zorg dat de GEMINI_API_KEY in je Streamlit Secrets staat
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"])
else:
    # Voor lokaal testen als je nog geen Secrets hebt ingesteld
    API_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"

SYSTEM_PROMPT = """
Jij bent een vriendelijke HR-interviewer. Jouw doel is om een warm en natuurlijk gesprek te voeren 
om iemand te helpen een compleet CV te maken. 
- Stel korte, open vragen.
- Vraag naar: Naam, droombaan, eerdere ervaringen, maar ook hobby's en wat iemand uniek maakt.
- Reageer empathisch op persoonlijke verhalen.
- Stel slechts ÉÉN vraag tegelijk.
- Zodra je genoeg weet, zeg je: 'Bedankt! Ik heb genoeg info. Hier is je CV:' en maak je een prachtig overzicht.
"""

st.set_page_config(page_title="AI HR Interviewer", page_icon="🎤")
st.title("🤝 Je Persoonlijke HR Coach")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je coach. Vertel eens, wie ben je en waar word jij echt blij van in je werk of vrije tijd?"}]

# --- 2. VOICE OUTPUT (De AI praat terug) ---
def speak(text):
    # Verwijdert sterretjes en vreemde tekens voor een schone uitspraak
    clean_text = text.replace('*', '').replace('"', "'").replace("\n", " ")
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{clean_text}");
    msg.lang = 'nl-NL';
    msg.rate = 0.9; 
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. DISPLAY CHAT ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Laat de AI het laatste bericht voorlezen
        if i == len(st.session_state.messages) - 1 and message["role"] == "assistant":
            speak(message["content"])

# --- 4. INPUT (Voice & Text) ---
st.write("---")
audio_data = mic_recorder(start_prompt="🎤 Klik om te praten", stop_prompt="🛑 Stop met praten", key='recorder')
text_input = st.chat_input("Of typ je antwoord hier...")

user_reply = None

if audio_data:
    with st.spinner("Ik luister..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Gemini kan de audio direct analyseren
            response = model.generate_content([
                "Wat zegt de gebruiker hier? Vat het niet samen, schrijf het letterlijk op.",
                {"mime_type": "audio/wav", "data": audio_data['bytes']}
            ])
            user_reply = response.text
        except:
            st.error("Kon de audio niet verwerken. Probeer het te typen.")

if text_input:
    user_reply = text_input

# --- 5. LOGICA & AI REACTIE ---
if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    with st.chat_message("user"):
        st.markdown(user_reply)

    with st.spinner("Aan het nadenken..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        # We sturen de laatste 6 berichten mee voor de context
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
        full_prompt = f"{SYSTEM_PROMPT}\n\nGespreksverloop:\n{history}\n\nInterviewer:"
        
        response = model.generate_content(full_query if 'full_query' in locals() else full_prompt)
        ai_message = response.text
        
        with st.chat_message("assistant"):
            st.markdown(ai_message)
            st.session_state.messages.append({"role": "assistant", "content": ai_message})
            st.rerun() # Rerun om de spraak-functie te activeren

# --- 6. HET RESULTAAT (DOWNLOAD) ---
last_content = st.session_state.messages[-1]["content"]
if "HIER IS JE CV" in last_content.upper():
    st.balloons()
    st.download_button("📄 Download mijn mooie CV", last_content, file_name="Mijn_Nieuwe_CV.txt")
