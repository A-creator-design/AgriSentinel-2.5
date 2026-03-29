import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from PIL import Image
import requests

# --- 1. API CONFIG (Direct 2.5 Flash) ---
import os
OS_KEY = os.getenv("API_KEY")
genai.configure(api_key=OS_KEY)

# --- 2. THE DARK EMERALD THEME ---
st.set_page_config(page_title="AgriSentinel 2.5 Pro", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background-color: #0F172A; color: #F1F5F9; }
    .main .block-container { background-color: #1E293B; border-radius: 15px; padding: 2rem; }
    p, li, h1, h2, h3, span, label { color: #F1F5F9 !important; }
    
    /* Emerald Analyze Button */
    div.stButton > button:first-child {
        background-color: #22C55E !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
        border: none;
    }
    /* Red 'STOP' Button Styling */
    div.stButton > button[aria-label="🛑 STOP AUDIO"] {
        background-color: #EF4444 !important;
        color: white !important;
    }
    
    .stAlert { background-color: #0F172A !important; border: 2px solid #22C55E !important; color: #F1F5F9 !important; }
    [data-testid="stMetricValue"] { color: #22C55E !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True
)

# --- 3. DYNAMIC WEATHER ---
@st.fragment(run_every=600)
def show_live_weather():
    try:
        url = "https://wttr.in/Hyderabad?format=j1"
        data = requests.get(url).json()
        temp = data['current_condition'][0]['temp_C']
        desc = data['current_condition'][0]['weatherDesc'][0]['value']
        st.subheader("☀️ Live Weather")
        st.metric(label="Hyderabad Status", value=f"{temp}°C", delta=desc)
    except:
        st.sidebar.write("Weather: 28°C (Sunny)")

# --- 4. SIDEBAR ---
with st.sidebar:
    show_live_weather()
    st.divider()
    lang_opt = st.selectbox("🌐 Select Language:", ["English", "Telugu", "Hindi"])
    lang_codes = {"English": "en", "Telugu": "te", "Hindi": "hi"}
    st.divider()
    # CAMERA TOGGLE (OFF SWITCH)
    cam_on = st.toggle("📷 Enable Live Camera", value=True)
    if st.button("🛑 STOP AUDIO"):
        st.rerun()

# --- 5. MAIN UI ---
st.title("🌾 AgriSentinel 2.5: Vision & Voice")

img_file = None
if cam_on:
    img_file = st.camera_input("📸 Take Photo")
else:
    st.warning("Camera Hardware OFF.")

up_file = st.file_uploader("📁 Or Upload Image", type=['jpg','png','jpeg'])
if up_file:
    img_file = up_file

if img_file:
    col1, col2 = st.columns(2)
    img = Image.open(img_file)
    with col1:
        st.image(img, use_container_width=True)
    
    with col2:
        if st.button("🔍 ANALYZE & SPEAK"):
            try:
                # DIRECT 2.5 FLASH CALL
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"In {lang_opt}, identify plant/health. Give 2 bullets for treatment and 2026 Mandi price. Keep it very short."
                
                response = model.generate_content([prompt, img])
                txt = response.text
                
                st.subheader("📋 Quick Report")
                st.info(txt)
                
                # --- VOICE ENGINE (Direct Stream) ---
                sound_io = BytesIO()
                tts = gTTS(text=txt, lang=lang_codes[lang_opt])
                tts.write_to_fp(sound_io)
                sound_io.seek(0)
                st.audio(sound_io, format="audio/mp3", autoplay=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("Phase 2 ET GenAI Hackathon | Developed by Alli Rajitha")