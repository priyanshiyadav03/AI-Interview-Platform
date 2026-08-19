import streamlit as st
import requests
from gtts import gTTS
import base64
from streamlit_mic_recorder import speech_to_text

def speak_text(text):
    if text:
        # 1. Text ko Audio (gTTS) mein convert kiya (English with professional accent)
        tts = gTTS(text=text, lang='en', tld='co.in') 
        
        # 2. Memory mein save karne ke liye temporary file banayi
        tts.save("speech.mp3")
        
        # 3. Streamlit mein audio ko background mein AUTO-PLAY karne ka jugad
        with open("speech.mp3", "rb") as f:
            audio_bytes = f.read()
        
        # HTML audio tag banaya autoplay feature ke sath
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="true" style="display:none;"></audio>'
        
        # Streamlit par html execute kar diya (bina kisi player ko screen par dikhaye)
        st.markdown(audio_html, unsafe_allow_html=True)

# Backend FastAPI URL
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Recruitment & Interview Portal", layout="centered")

# --- Custom UI Styling (Injecting CSS for Corporate Look) ---
st.markdown("""
    <style>
        .main-header { font-size: 36px; font-weight: 800; color: #4F46E5; margin-bottom: 5px; }
        .sub-header { font-size: 16px; color: #64748B; margin-bottom: 25px; }
        .card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; }
        div.stButton > button:first-child { background-color: #4F46E5; color: white; border-radius: 6px; width: 100%; padding: 10px; font-weight: bold; }
        div.stButton > button:first-child:hover { background-color: #4338CA; }
    </style>
""", unsafe_allow_html=True)

# --- 1. Catching session_id from URL Query Parameters ---
query_params = st.query_params
session_id_from_url = query_params.get("session_id", None)

if session_id_from_url:
  
    # ==========================================
    # SCREEN 2: LIVE INTERVIEW ROOM (From Email)
    # ==========================================
    st.markdown('<p class="main-header">🎙️ AI Live Interview Room</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Active Session Token: <code>{session_id_from_url}</code></p>', unsafe_allow_html=True)
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    # 🧠 FIX 1: Agar session_state me question nahi hai, toh backend se fetch karo (Ya fir default set karo)
    if "current_question" not in st.session_state:
        with st.spinner("Initializing interview room..."):
            try:
                # Backend ke /start endpoint ko hit karke initial question la rahe hain
                start_response = requests.post(f"{BACKEND_URL}/api/start", json={"session_id": session_id_from_url})
                if start_response.status_code == 200:
                    st.session_state.current_question = start_response.json().get("question")
                else:
                    # Fallback agar /start configured na ho properly
                    st.session_state.current_question = "Can you take a few minutes to introduce yourself, share your background in software engineering, and highlight any key projects that you've worked on recently?"
            except Exception:
                st.session_state.current_question = "Can you take a few minutes to introduce yourself, share your background in software engineering, and highlight any key projects that you've worked on recently?"
    if st.session_state.get('last_spoken_question') != st.session_state.current_question:
        speak_text(st.session_state.current_question)
        st.session_state.last_spoken_question = st.session_state.current_question # Lock laga diya taaki repeat na ho
    # 🔥 FIX 2: Ab question hardcoded nahi hai, variable se dynamic show hoga!
    st.markdown(f'<div class="card"><strong>Current Question:</strong><br>{st.session_state.current_question}</div>', unsafe_allow_html=True)
    st.markdown("##### 🎤 Answer via Voice:")
    
    # 🎙️ Streamlit native mic recorder speech-to-text component
    text_from_speech = speech_to_text(
        language='en',
        start_prompt="🎙️ Start Speaking",
        stop_prompt="🛑 Stop",
        just_once=False,
        use_container_width=False,
        key=f"speech_rec_{st.session_state.question_index}"
    )

    if text_from_speech:
        st.session_state[f"ans_text_{st.session_state.question_index}"] = text_from_speech
        st.session_state[f"ans_widget_{st.session_state.question_index}"] = text_from_speech

    default_text = st.session_state.get(f"ans_text_{st.session_state.question_index}", "")

    # 📝 Text Area Box
    user_answer = st.text_area(
        "Type or edit your professional answer here:", 
        value=default_text,
        height=150, 
        placeholder="Click 'Start Speaking' above to dictate or start typing manually...", 
        key=f"ans_widget_{st.session_state.question_index}"
    )

   
    
    



 

    if st.button("Submit Interview Answer"):
        if not user_answer.strip():
            st.warning("⚠️ Answer field cannot be left blank.")
        else:
            with st.spinner("Submitting and evaluating answer..."):
                try:
                    payload = {
                        "session_id": session_id_from_url,
                        "answer": user_answer
                    }
                    response = requests.post(f"{BACKEND_URL}/api/submit-answer", json=payload)

                    if response.status_code == 200:
                        data = response.json()
                        st.balloons()

                        if data.get("end_of_interview") == True:
                            st.success(f"🎉 Interview Completed! Verdict: {data.get('verdict')}")
                            st.metric(label="Final Score", value=data.get("final_percentage_score"))
                            with st.expander("📊 View Detailed Scorecard"):
                                st.json(data.get("final_evaluation"))
                        else:
                            st.session_state.current_question = data.get("question", "No question received.")
                            st.session_state.voice_text = ""
                            st.session_state.question_index += 1   # ← forces widget key change
                            st.success("✅ Answer recorded! Fetching next question...")
                            st.rerun()
                    else:
                        st.error(f"❌ Backend error: {response.text}")
                except Exception as e:
                    st.error(f"🔌 Connection failed: {e}")

else:
    # ==========================================
    # SCREEN 1: CANDIDATE REGISTRATION & ATS RESUME UPLOAD
    # ==========================================
    st.markdown('<p class="main-header">📊 AI Recruitment & ATS Portal</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Screen resumes via LangGraph AI engine and setup instant conversational loops.</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📝 Candidate Profiles")
        c_name = st.text_input("Candidate Name", placeholder="e.g., Jane Doe")
        c_email = st.text_input("Candidate Email", placeholder="e.g., jane@example.com")
        
        st.write("---")
        st.subheader("📁 Documents")
        uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("Process & Generate Interview Link"):
        if not c_name or not c_email or not uploaded_file:
            st.error("🚨 All fields (Name, Email, Resume) are strictly mandatory!")
        else:
            with st.spinner("Parsing resume and analyzing via local LLM..."):
                try:
                    # Form data payload files mapping
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    form_data = {
                    "candidate_name": c_name,
                    "candidate_email": c_email
                }
                    
                    # Target endpoint calling
                    response = requests.post(f"{BACKEND_URL}/upload-resume", files=files, data=form_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("🎯 Evaluation Finished Successfully!")
                        with st.expander("🔍 View Full JSON Response"):
                            st.json(data)
                        
                        # Render parsed output cards
                        ats = data.get("ats_scores", {}) or data.get("ats_report") or data.get("ats_results", {})
                        skill_score = int(float(ats.get('skill_score')or 0))
                        tech_score = int(float(ats.get('technology_and_tools_score')or 0))
                        exp_score = int(float(ats.get('experience_score')or 0))
                        soft_score = int(float(ats.get('soft_skill_score')or 0))
                        final_score = (skill_score * 0.40) + (tech_score * 0.30) + (soft_score * 0.15) + (exp_score * 0.15)
                        final_score = round(final_score, 1)

                        # --- 3. SHORTLIST / REJECTION LOGIC (Cutoff: 70%) ---
                        if final_score >= 70.0:
                            status_text = "🟢 SHORTLISTED FOR INTERVIEW"
                            status_color = "#10B981" # Green
                            status_bg = "#E6F4EA"
                           
                        else:
                            status_text = "🔴 APPLICATION REJECTED"
                            status_color = "#EF4444" # Red
                            status_bg = "#FCE8E6"
                            st.error("We regret to inform you that your profile doesn't match our criteria at this moment.")
                        st.markdown(f"""
                        <div class="card" style="border-left: 8px solid {status_color}; background-color: {status_bg}; padding: 22px; margin-bottom: 15px;">
                            <h2 style="margin: 0; color: #1E293B;">Final ATS Score: <span style="color: {status_color}; font-weight: 800;">{final_score}%</span></h2>
                            <p style="margin: 8px 0 0 0; font-size: 16px; font-weight: bold; color: {status_color};">
                                Hiring Status: {status_text}
                            </p>
                        </div>            
                        <div class="card" style="border-left: 5px solid #4F46E5;">
                            <h4>📈  detailed Calculated Scores Matrix</h4>
                            <p><b>Core Skills Score:</b> {skill_score}%</p>
                            <p><b>Tech Stack & Tools Score:</b> {tech_score}%</p>
                            <p><b>Experience Score:</b> {ats.get('experience_score')}%</p>
                            <p><b>Soft Skills Compatibility:</b> {ats.get('soft_skill_score')}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Generate simulated test link
                      # --- 3. SHORTLIST / REJECTION LOGIC (Cutoff: 70%) ---
                        if final_score >= 70.0:
                            # 📢 Button hatakar candidate ko email check karne ka instruction diya
                            st.success("🎉 Congratulations! You have cleared the initial screening.")
                            st.info("📧 Ek personalized interview link aapke register kiye huye Email par bhej diya gaya hai. Kripya apna inbox (ya spam folder) check karein aur interview shuru karein!")
                        else:
                            st.warning("⚠️ Candidate did not meet the minimum ATS score threshold for interview scheduling.")
                            st.error("We regret to inform you that your profile doesn't match our criteria at this moment.")
                            
                    else:
                        # Agar backend se 200 ke alawa koi aur status code aaya
                        st.error(f"Backend Returned Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"Could not connect to FastAPI app on port 8000: {e}")