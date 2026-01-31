import streamlit as st
import google.generativeai as genai  # <--- DIT IS DE BELANGRIJKSTE REGEL
from streamlit_mic_recorder import mic_recorder
import requests
import base64

# --- 1. VEILIGE CONFIGURATIE ---
# We checken eerst of de secrets bestaan, anders gebruiken we een lege tekst
GEMINI_KEY = "AIzaSyBj_7CBm7wm_fPFeUXEm6u5x9YRARv9t0A"
ELEVEN_KEY ="sk_722508e8af2591b1e34e0b36ca75b0518e8266c20964b162"

VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Een warme Nederlandse stem (Marcus)

if not GEMINI_KEY or not ELEVEN_KEY:
    st.error("⚠️ API-sleutels ontbreken in de Secrets!")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """
Jij bent een warme HR-interviewer. Jouw doel is om een natuurlijk gesprek te voeren.
Stel zelfstandig vragen om een beeld te krijgen van iemands:
1. Naam en passie.
2. Werkervaring en kwaliteiten.
3. Hobby's en wat die zeggen over de persoon.
Stel slechts ÉÉN vraag tegelijk. Wees empathisch.
Als je alles weet, zeg je: 'Bedankt! Hier is je CV:' en maak je een prachtig overzicht.
"""

st.set_page_config(page_title="Live AI HR Interview", page_icon="🎙️")
st.title("🎙️ Live HR Interview")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hoi! Ik ben je HR-coach. Wat leuk dat je er bent. Vertel eens, wie ben je en waar word jij echt blij van in je werk?"}]

# --- 2. HULPFUNCTIES (Voice & Audio) ---
def text_to_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.error(f"ElevenLabs fout: {e}")
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
# Microfoon input
audio_input = mic_recorder(start_prompt="🎤 Klik en praat", stop_prompt="🛑 Stop", key='recorder')
# Tekst input als backup
text_input = st.chat_input("Of typ hier je antwoord...")

user_reply = None

# Stap A: Verwerk Spraak naar Tekst via Gemini
if audio_input:
    with st.spinner("Ik luister..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([
                "Schrijf exact op wat de gebruiker zegt in deze audio. Geef alleen de tekst terug.", 
                {"mime_type": "audio/wav", "data": audio_input['bytes']}
            ])
            user_reply = response.text
        except Exception as e:
            st.error("Kon de spraak niet verwerken. Probeer het opnieuw of typ je antwoord.")

if text_input:
    user_reply = text_input

# Stap B: Genereer AI Antwoord en Stem
if user_reply:
    st.session_state.messages.append({"role": "user", "content": user_reply})
    with st.chat_message("user"):
        st.markdown(user_reply)

    with st.spinner("Coach denkt na..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Context opbouwen
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]])
            full_query = f"{SYSTEM_PROMPT}\n\nGesprek:\n{history}\n\nInterviewer:"
            
            ai_message = model.generate_content(full_query).text
            
            with st.chat_message("assistant"):
                st.markdown(ai_message)
                st.session_state.messages.append({"role": "assistant", "content": ai_message})
                
                # Direct voorlezen via ElevenLabs
                audio_content = text_to_speech(ai_message)
                if audio_content:
                    autoplay_audio(audio_content)
                
                # Pagina verversen om audio direct af te spelen (optioneel)
                st.rerun()
        except Exception as e:
            st.error(f"Fout bij genereren antwoord: {e}")

if not GEMINI_KEY or not ELEVEN_KEY:
    st.error("⚠️ API-sleutels ontbreken! Ga naar 'Settings' > 'Secrets' in Streamlit Cloud en voeg ze toe.")
    st.stop()

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
