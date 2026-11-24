from html import escape
import streamlit as st
import requests
from gtts import gTTS
import base64
from streamlit_mic_recorder import speech_to_text

def speak_text(text):
    if text:
  
        tts = gTTS(text=text, lang='en', tld='co.in') 
        
       
        tts.save("speech.mp3")
        
        
        with open("speech.mp3", "rb") as f:
            audio_bytes = f.read()
        
       
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="true" style="display:none;"></audio>'
        
        # Streamlit par html execute kar diya (bina kisi player ko screen par dikhaye)
        st.markdown(audio_html, unsafe_allow_html=True)

# Backend FastAPI URL
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="HireMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: radial-gradient(
        ellipse at top right,
        #241340 0%,
        #0B1020 45%,
        #080B16 100%
    );
    color: #F1F5F9;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1150px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* Main heading */
.main-header {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(
        90deg, #C4B5FD, #8B5CF6, #22D3EE
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-header {
    font-size: 16px;
    color: #94A3B8;
    margin-bottom: 30px;
}

/* Glassmorphism cards */
.card {
    background: rgba(21, 25, 44, 0.85);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(139, 92, 246, 0.25);
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    margin-bottom: 20px;
    color: #E2E8F0;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(
        135deg, #7C3AED, #4F46E5
    );
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px 24px;
    width: 100%;
    font-weight: 600;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(139,92,246,0.5);
    color: white;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    background: #15192C;
    color: #F1F5F9;
    border: 1px solid #34304C;
    border-radius: 10px;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(139,92,246,0.07);
    border: 2px dashed #6650A4;
    border-radius: 16px;
    padding: 25px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0D1120;
    border-right: 1px solid #29243E;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #15192C;
    border: 1px solid #302747;
    border-radius: 15px;
    padding: 20px;
}

/* Expander */
[data-testid="stExpander"] {
    background: #15192C;
    border-radius: 12px;
    border: 1px solid #302747;
}

h1, h2, h3, h4, h5 {
    color: #F1F5F9;
}

[data-testid="stHeader"] {
    background: transparent;
}
/* Hero Section */
.hero-section {
    background: linear-gradient(
        135deg, #20143D, #10182F, #142A3D
    );
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 24px;
    padding: 55px 25px;
    text-align: center;
    margin-bottom: 30px;
    animation: fadeIn 0.8s ease-in-out;
}

.hero-badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid #7254B5;
    color: #C4B5FD;
    padding: 8px 18px;
    border-radius: 30px;
    font-size: 12px;
    letter-spacing: 2px;
}

.hero-title {
    font-size: clamp(32px, 5vw, 55px);
    font-weight: 800;
    line-height: 1.2;
    margin: 22px 0;
    color: #FFFFFF;
}

.gradient-text {
    background: linear-gradient(
        90deg, #A78BFA, #818CF8, #22D3EE
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    font-size: 17px;
    color: #A8B1C5;
    max-width: 650px;
    margin: auto;
    line-height: 1.7;
}

/* Feature Cards */
.feature-card {
    background: rgba(21,25,44,0.85);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 18px;
    padding: 28px 15px;
    text-align: center;
    height: 230px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-7px);
    border-color: #8B5CF6;
    box-shadow: 0 10px 30px rgba(139,92,246,0.2);
}

.feature-icon {
    font-size: 38px;
    margin-bottom: 12px;
}

.feature-title {
    font-size: 19px;
    font-weight: 700;
    color: #E2E8F0;
}

.feature-description {
    font-size: 14px;
    color: #94A3B8;
    margin-top: 8px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(21, 25, 44, 0.65);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 20px;
    padding: 15px;
}
.sidebar-brand {
    font-size: 28px;
    font-weight: 800;
    color: #C4B5FD;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #94A3B8;
    letter-spacing: 1px;
}

.sidebar-label {
    font-size: 11px;
    color: #94A3B8;
    letter-spacing: 2px;
    margin-top: 20px;
    margin-bottom: 12px;
}

.sidebar-item {
    padding: 12px;
    border-radius: 10px;
    color: #CBD5E1;
    font-size: 14px;
    margin-bottom: 5px;
    transition: 0.3s;
}

.sidebar-item:hover {
    background: rgba(139,92,246,0.15);
    color: #C4B5FD;
}

.sidebar-active {
    background: rgba(139,92,246,0.20);
    border-left: 3px solid #8B5CF6;
    color: #C4B5FD;
}

.engine-card {
    background: linear-gradient(135deg, #211638, #15192C);
    border: 1px solid #40305D;
    border-radius: 14px;
    padding: 18px;
    margin-top: 20px;
}
.score-panel {
    background: #15192C;
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    min-height: 350px;
}

.score-circle {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    margin: 25px auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.score-inner {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: #15192C;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.score-number {
    font-size: 42px;
    font-weight: 800;
    color: #FFFFFF;
}

.score-label {
    font-size: 12px;
    color: #94A3B8;
    letter-spacing: 2px;
}

.skill-row {
    margin-bottom: 20px;
}

.skill-heading {
    display: flex;
    justify-content: space-between;
    color: #E2E8F0;
    font-size: 15px;
    margin-bottom: 8px;
}

.skill-track {
    height: 10px;
    background: #2A3046;
    border-radius: 20px;
    overflow: hidden;
}

.skill-fill {
    height: 100%;
    border-radius: 20px;
    animation: growBar 1.2s ease-out;
}

.skill-weight {
    color: #94A3B8;
    font-size: 11px;
    margin-top: 5px;
}

@keyframes growBar {
    from { width: 0; }
}

@media (prefers-reduced-motion: reduce) {
    .skill-fill {
        animation: none;
    }
}
.interview-header {
    background: linear-gradient(
        135deg, #211638, #10182F
    );
    border: 1px solid #40305D;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
}

.ai-orb-container {
    text-align: center;
    padding: 35px 20px;
}

.ai-orb {
    width: 140px;
    height: 140px;
    margin: 20px auto;
    border-radius: 50%;
    background: radial-gradient(
        circle at 30% 30%,
        #C4B5FD,
        #8B5CF6,
        #4338CA,
        #15192C
    );
    box-shadow: 0 0 50px rgba(139,92,246,0.6);
    animation: pulseOrb 3s infinite ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 45px;
}

@keyframes pulseOrb {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 30px rgba(139,92,246,0.4);
    }

    50% {
        transform: scale(1.08);
        box-shadow: 0 0 65px rgba(139,92,246,0.8);
    }
}

.ai-name {
    color: #C4B5FD;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 3px;
}

.question-card {
    background: #15192C;
    border: 1px solid #40305D;
    border-left: 5px solid #8B5CF6;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 25px;
}

.question-label {
    color: #A78BFA;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 15px;
}

.question-text {
    color: #F1F5F9;
    font-size: 22px;
    font-weight: 600;
    line-height: 1.6;
}

@media (prefers-reduced-motion: reduce) {
    .ai-orb {
        animation: none;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 1. Catching session_id from URL Query Parameters ---
def show_ats_dashboard(final_score, skill_score,
                       tech_score, exp_score, soft_score):

    shortlisted = final_score >= 70

    status_color = "#10B981" if shortlisted else "#EF4444"

    status = (
        "✓ SHORTLISTED FOR INTERVIEW"
        if shortlisted
        else "APPLICATION REJECTED"
    )

    visual_score = max(0, min(100, final_score))

    st.markdown("## 📊 AI Resume Analysis")
    st.caption("Intelligent candidate evaluation results")

    left, right = st.columns(2)

    with left:
        st.markdown(
            f'<div class="score-panel">'
            f'<div class="score-label">OVERALL ATS SCORE</div>'
            f'<div class="score-circle" style="background:'
            f'conic-gradient(#8B5CF6 0%, #22D3EE {visual_score}%,'
            f'#2A3046 {visual_score}% 100%);">'
            f'<div class="score-inner">'
            f'<div class="score-number">{final_score}%</div>'
            f'<div class="score-label">MATCH SCORE</div>'
            f'</div></div>'
            f'<div style="color:{status_color};font-weight:700;">'
            f'{status}</div>'
            f'<p style="color:#94A3B8;font-size:13px;">'
            f'Minimum required score: 70%</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    with right:

        scores = [
            ("Core Skills", skill_score, "#8B5CF6", 40),
            ("Technology & Tools", tech_score, "#22D3EE", 30),
            ("Experience", exp_score, "#60A5FA", 15),
            ("Soft Skills", soft_score, "#34D399", 15)
        ]

        html = (
            '<div class="score-panel" style="text-align:left;">'
            '<h4>Detailed Score Breakdown</h4>'
        )

        for name, score, color, weight in scores:

            bar_width = max(0, min(100, score))

            html += (
                f'<div class="skill-row">'
                f'<div class="skill-heading">'
                f'<span>{name}</span>'
                f'<span style="color:{color};">{score}%</span>'
                f'</div>'
                f'<div class="skill-track">'
                f'<div class="skill-fill" style="width:{bar_width}%;'
                f'background:{color};"></div>'
                f'</div>'
                f'<div class="skill-weight">{weight}% weight</div>'
                f'</div>'
            )

        html += '</div>'

        st.markdown(html, unsafe_allow_html=True)
query_params = st.query_params
session_id_from_url = query_params.get("session_id", None)
with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">🧠 HireMind AI</div>'
        '<div class="sidebar-subtitle">INTELLIGENT RECRUITMENT</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    active_page = (
        "🎙️ Live Interview Room"
        if session_id_from_url
        else "🏠 Recruitment Portal"
    )

    st.markdown(
        f'<div class="sidebar-item sidebar-active">{active_page}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-label">PLATFORM FEATURES</div>',
        unsafe_allow_html=True
    )

    features = [
        "📄 Resume Screening",
        "🎯 ATS Analysis",
        "🧠 Adaptive AI",
        "🎙️ Voice Interview",
        "📊 Smart Evaluation"
    ]

    for feature in features:
        st.markdown(
            f'<div class="sidebar-item">{feature}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown(
        '<div class="engine-card">'
        '<div style="color:#A78BFA;font-size:12px;">✦ AI ENGINE</div>'
        '<div style="font-size:20px;font-weight:700;">LangGraph</div>'
        '<div style="color:#94A3B8;font-size:12px;">Intelligent interview workflow</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.caption("HireMind AI • Version 1.0")
    st.caption("Powered by Artificial Intelligence")

if session_id_from_url:
  
    # ==========================================
    # SCREEN 2: LIVE INTERVIEW ROOM (From Email)
    # ==========================================
    st.markdown(
        '<div class="interview-header">'
        '<div style="color:#34D399;font-size:13px;">'
        '● SESSION ACTIVE</div>'
        '<div class="main-header">AI Interview Room</div>'
        '<div class="sub-header">'
        'Your intelligent AI-powered interview experience'
        '</div></div>',
        unsafe_allow_html=True
    )
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
    st.markdown("""
        <div class="hero-section">

        <div class="hero-badge">
            ✦ NEXT-GENERATION RECRUITMENT
        </div>

        <div class="hero-title">
            Hire Smarter.<br>
            <span class="gradient-text">
                Interview Better.
            </span>
        </div>

        <div class="hero-description">
            HireMind AI combines intelligent resume
            screening, adaptive interviews and
            AI-powered candidate evaluation into
            one seamless recruitment experience.
        </div>

        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart ATS</div>
            <div class="feature-description">
                Intelligent resume screening
                and skill matching.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Adaptive AI</div>
            <div class="feature-description">
                Personalized questions and
                intelligent follow-ups.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <div class="feature-title">Voice Interview</div>
            <div class="feature-description">
                Interactive AI-powered
                interview experience.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("## Candidate Registration")
    st.caption(
        "Start your AI-powered recruitment journey."
    )
    
    #with st.container():
     #   st.markdown('<div class="card">', unsafe_allow_html=True)
      #  st.subheader("📝 Candidate Profiles")
       # c_name = st.text_input("Candidate Name", placeholder="e.g., Jane Doe")
        #c_email = st.text_input("Candidate Email", placeholder="e.g., jane@example.com")
        
        #st.write("---")
        #st.subheader("📁 Documents")
        #uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
        #st.markdown('</div>', unsafe_allow_html=True)
    with st.container(border=True):

        st.markdown("### 👤 Candidate Information")
        st.caption("Enter your details to begin the screening process.")

        name_col, email_col = st.columns(2)

        with name_col:
            c_name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

        with email_col:
            c_email = st.text_input(
                "Email Address",
                placeholder="Enter your email address"
            )

        st.divider()

        st.markdown("### 📄 Upload Resume")
        st.caption("Upload your latest resume for AI-powered analysis.")

        uploaded_file = st.file_uploader(
            "Resume (PDF only)",
            type=["pdf"],
            label_visibility="collapsed"
        )
        
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

                        show_ats_dashboard(
                            final_score,
                            skill_score,
                            tech_score,
                            exp_score,
                            soft_score
                        )
                        
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