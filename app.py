# --- 1. CONFIGURATIE ---
# Vul deze in bij Streamlit 'Secrets' of vervang ze hier tijdelijk voor een lokale test
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A")
ELEVEN_KEY = st.secrets.get("ELEVEN_API_KEY", "sk_722508e8af2591b1e34e0b36ca75b0518e8266c20964b162")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Een warme, Nederlandse stem (bijv. 'Adam' of 'Marcus')

genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """
Jij bent een warme HR-interviewer. Voer een natuurlijk gesprek. 
Stel zelfstandig vragen om een beeld te krijgen van iemands:
1. Naam en droombaan.
2. Werkervaring en sterke punten.
3. Persoonlijke passies en hobby's.
Stel slechts ÉÉN vraag tegelijk. Reageer op wat de gebruiker zegt.
Als je alles weet, zeg je: 'Bedankt! Hier is je CV:' en maak je een overzicht.
"""

st.set_page_config(page_title="AI HR Coach", page_icon="🎙️")
st.title("🎙️ Live HR Interview")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je HR-coach. Ik help je om een mooi CV te maken. Vertel eens, wie ben je en wat voor werk zou je het liefste doen?"}]

# --- 2. ELEVENLABS FUNCTIE (Voice Output) ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    return None

def autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- 3. CHAT DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. INTERVIEW LOGICA ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎤 Geef antwoord (Spraak)", stop_prompt="🛑 Stop", key='recorder')
text_input = st.chat_input("Of typ hier...")

user_reply = None

if audio_input:
    with st.spinner("Ik luister..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(["Schrijf exact op wat hier gezegd wordt:", {"mime_type": "audio/wav", "data": audio_input['bytes']}])
        user_reply = response.text

if text_input:
    user_reply = text_input

if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    with st.chat_message("user"):
        st.markdown(user_reply)

    with st.spinner("De coach denkt na..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
        full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nInterviewer:"
        
        ai_response = model.generate_content(full_query).text
        
        with st.chat_message("assistant"):
            st.markdown(ai_message := ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_message})
            
            # Directe Voice Output
            audio_content = text_to_speech(ai_message)
            if audio_content:
                autoplay_audio(audio_content)
