# smart_resume_analyser_final.py
import io
import re
import streamlit as st
# Hide the "Deploy" button and other Streamlit menu items
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}   /* hides the hamburger menu */
    header {visibility: hidden;}      /* hides the Streamlit header */
    footer {visibility: hidden;}      /* hides the footer */
    [data-testid="stToolbar"] {visibility: hidden;}  /* hides the deploy button */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import PyPDF2

# ----------------------------
# Helper Functions (Backend)
# ----------------------------
# 🎨 Custom CSS for styling expander header


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        return "\n".join(pages_text).strip()
    except Exception:
        return ""

def extract_name(text: str) -> str:
    if not text:
        return "Not found"
    blacklist = {
        "RESUME", "CURRICULUM VITAE", "CV", "CONTACT", "SUMMARY", "OBJECTIVE",
        "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", "WORK", "PROFILE"
    }
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines[:8]:
        up = line.upper()
        if up in blacklist:
            continue
        if "@" in line or any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4:
            if any(w[0].isupper() for w in words if w):
                return line
    return "Not found"

def extract_email(text: str) -> str:
    if not text:
        return "Not found"
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    m = re.search(email_pattern, text, flags=re.IGNORECASE)
    return m.group(0) if m else "Not found"

def extract_phone(text: str) -> str:
    if not text:
        return "Not found"
    patterns = [
        r'(?<!\d)\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?!\d)',
        r'(?<!\d)\d{10}(?!\d)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return "Not found"

def extract_skills(text: str):
    if not text:
        return []
    skill_keywords = [
        "Python", "Java", "C++", "C", "JavaScript", "HTML", "CSS", "React",
        "Node.js", "Node", "SQL", "MongoDB", "PostgreSQL", "MySQL", "R", "Scala",
        "AI", "ML", "Machine Learning", "Artificial Intelligence", "Data Science",
        "Data Analysis", "Big Data", "Deep Learning", "Neural Networks",
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
        "Excel", "PowerBI", "Tableau", "Git", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Linux", "Windows", "MacOS"
    ]
    found = set()
    up = text.upper()
    for sk in skill_keywords:
        if sk.upper() in up:
            found.add(sk)
    return sorted(found)

# ----------------------------
# Improved ATS Scoring
# ----------------------------

def calculate_ats_score(skills, text, jd_text=""):
    if not text:
        return 0

    score = 20  # base score for just having a resume

    # ---- Skill Matching ----
    jd_text_upper = jd_text.upper() if jd_text else ""
    matched_skills = [s for s in skills if jd_text_upper and s.upper() in jd_text_upper]

    if jd_text:  # If JD provided, weigh more on overlap
        skill_match_score = min(len(matched_skills) * 8, 50)
    else:  # If no JD, fallback to generic skill count
        skill_match_score = min(len(skills) * 5, 40)

    score += skill_match_score

    # ---- Section Presence ----
    section_keywords = ["experience", "education", "project", "certification"]
    section_score = sum(5 for kw in section_keywords if kw in text.lower())
    score += section_score

    # ---- Penalties for Missing Sections ----
    if "experience" not in text.lower():
        score -= 5
    if "education" not in text.lower():
        score -= 5

    # ---- Coverage Bonus ----
    if jd_text and skills:
        coverage = int((len(matched_skills) / max(1, len(set(jd_text.split())))) * 30)
        score += coverage

    # Final clamp
    return max(0, min(score, 100))

def improvement_suggestions(skills, all_skills, ats_score, jd_text=""):
    suggestions = []
    if ats_score < 60:
        suggestions.append("🔴 ATS score is below average. Add more relevant skills & keywords.")
    elif ats_score < 75:
        suggestions.append("🟡 ATS score is good but can be improved with more technical skills.")
    else:
        suggestions.append("🟢 Great ATS score! Resume is fairly optimized.")

    if jd_text:
        suggestions.append("📌 Tailor your resume to better match the job description provided.")

    missing = [s for s in all_skills if s not in skills]
    if missing:
        suggestions.append(f"💡 Consider adding: {', '.join(missing[:4])}")
    if len(skills) < 5:
        suggestions.append("📈 Add more technical skills to increase marketability.")

    suggestions.append("✨ Use action verbs and quantify achievements.")
    return suggestions

# ----------------------------
# Streamlit UI (Frontend)
# ----------------------------

st.set_page_config(
    page_title="ResumePro - Smart Resume Analyzer", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="📄"
)

# Custom CSS with professional styling and animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 4rem 0;
    margin: -1rem -1rem 3rem -1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -50%;
    width: 200%;
    height: 100%;
    background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shine 3s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 1rem;
    text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    animation: fadeInUp 1s ease-out;
}

.hero-subtitle {
    font-size: 1.3rem;
    color: rgba(255,255,255,0.9);
    margin-bottom: 2rem;
    animation: fadeInUp 1s ease-out 0.2s both;
}

.hero-features {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 2rem;
    animation: fadeInUp 1s ease-out 0.4s both;
}

.hero-feature {
    text-align: center;
    color: white;
}

.hero-feature-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    display: block;
}

.hero-feature-text {
    font-size: 0.9rem;
    opacity: 0.9;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.section-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.06);
    border: 1px solid rgba(255,255,255,0.18);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.section-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.12);
}

.section-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
}

.upload-area {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border: 2px dashed #667eea;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
}

.upload-area:hover {
    border-color: #764ba2;
    background: linear-gradient(135deg, #ffeef8 0%, #f0e6ff 100%);
}

.section-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.info-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    animation: slideInLeft 0.6s ease-out;
}

.info-item {
    display: flex;
    align-items: center;
    margin: 0.8rem 0;
    font-size: 1rem;
}

.info-icon {
    margin-right: 0.8rem;
    font-size: 1.2rem;
}

.skills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 1rem;
}

.skill-tag {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: 500;
    animation: bounceIn 0.6s ease-out;
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes bounceIn {
    0% {
        opacity: 0;
        transform: scale(0.3);
    }
    50% {
        opacity: 1;
        transform: scale(1.05);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    animation: pulse 2s infinite;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4);
    }
    50% {
        box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
    }
}

.suggestion-item {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 0.8rem 0;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    color: #1e40af;  /* 🔵 Professional dark blue text */
    font-weight: 600; /* (optional) make it bolder */
}

            
}

.suggestion-item:hover {
    transform: translateX(10px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.job-match {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    animation: slideInRight 0.6s ease-out;
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.stTextArea textarea {
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    transition: border-color 0.3s ease;
}

.stTextArea textarea:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Hide Streamlit default elements */
.stApp > header {
    background: transparent;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
/* --- Robust expander header + link styling (force black) --- */
.streamlit-expanderHeader,
.stExpanderHeader,
.st-expanderHeader,
details > summary,
section[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] > div[role="button"],
div[role="button"][aria-expanded] {
    color: #000000 !important;   /* black */
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}

/* Also style links inside expanders (make them black) */
section[data-testid="stExpander"] a,
div[data-testid="stExpander"] a,
details a,
.stExpander a,
details > summary a {
    color: #ff6600 !important;
    text-decoration: underline !important;
}

/* Extra fallback selectors (covers other markup variations) */
div[class*="expander"] summary,
div[class*="expander"] > button {
    color: #ff6600 !important;
    font-weight: 700 !important;
}




</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="main-header">
    <div class="hero-title">Smart Resume Analyzer</div>
    <div class="hero-subtitle">AI-Powered Resume Analysis & ATS Optimization</div>
    <div class="hero-features">
        <div class="hero-feature">
            <span class="hero-feature-icon">🎯</span>
            <div class="hero-feature-text">ATS Scoring</div>
        </div>
        <div class="hero-feature">
            <span class="hero-feature-icon">🔍</span>
            <div class="hero-feature-text">Smart Analysis</div>
        </div>
        <div class="hero-feature">
            <span class="hero-feature-icon">💡</span>
            <div class="hero-feature-text">Expert Tips</div>
        </div>
        <div class="hero-feature">
            <span class="hero-feature-icon">💼</span>
            <div class="hero-feature-text">Job Matching</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Job Description Section
st.markdown("""
<div class="section-card">
    <div class="section-title">
        📋 Job Description Analysis
    </div>
    <p style="color: #64748b; margin-bottom: 1rem;">Paste the job description below to get personalized ATS scoring and tailored recommendations.</p>
</div>
""", unsafe_allow_html=True)

jd_text = st.text_area("", height=150, placeholder="Paste job description here for enhanced analysis...")

# Upload Section
st.markdown("""
<div class="section-card">
    <div class="section-title">
        📄 Resume Upload
    </div>
    <div class="upload-area">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
        <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">Upload Your Resume</div>
        <div style="color: #64748b;">Supports PDF format • Best results with text-based PDFs</div>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded_file is not None:
    uploaded_bytes = uploaded_file.read()
    extracted_text = extract_text_from_pdf_bytes(uploaded_bytes)

    # Raw text preview
    with st.expander("🔍 View Extracted Text Preview"):
        if extracted_text:
            st.text_area("", value=extracted_text[:3000], height=250, label_visibility="collapsed")
        else:
            st.warning("⚠ No selectable text found. Your PDF might be scanned. Try using a text-based PDF for better results.")

    # Extract information
    name = extract_name(extracted_text)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)

    # Information Display
    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            📊 Resume Analysis Results
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">👤 Personal Information</div>
            <div class="info-item">
                <span class="info-icon">📝</span>
                <strong>Name:</strong> {name}
            </div>
            <div class="info-item">
                <span class="info-icon">📧</span>
                <strong>Email:</strong> {email}
            </div>
            <div class="info-item">
                <span class="info-icon">📱</span>
                <strong>Phone:</strong> {phone}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">🛠 Technical Skills</div>
            <div style="color: rgba(255,255,255,0.9);">Detected {len(skills)} skills from your resume</div>
        </div>
        """, unsafe_allow_html=True)
        
        if skills:
            skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in skills])
            st.markdown(f'<div class="skills-container">{skills_html}</div>', unsafe_allow_html=True)

    # ATS Score Section
    ats_score = calculate_ats_score(skills, extracted_text, jd_text)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            🎯 ATS Compatibility Score
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{ats_score}</div>
            <div class="metric-label">ATS Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 1rem; animation-delay: 0.2s;">
            <div class="metric-value">{len(skills)}</div>
            <div class="metric-label">Skills Found</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ats_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ATS Compatibility Score", 'font': {'size': 20, 'color': '#2d3748'}},
            delta={'reference': 75},
            gauge={
                'axis': {'range': [None, 100], 'tickcolor': '#667eea'},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': '#fed7d7'},
                    {'range': [50, 75], 'color': '#fef5e7'},
                    {'range': [75, 100], 'color': '#c6f6d5'}
                ],
                'threshold': {
                    'line': {'color': "#764ba2", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig.update_layout(height=300, font={'color': '#2d3748'})
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        if ats_score >= 80:
            st.success("🎉 Excellent Score!")
        elif ats_score >= 60:
            st.info("👍 Good Score")
        else:
            st.error("⚠ Needs Improvement")

    # Skills WordCloud
    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            ☁ Skills Visualization
        </div>
    </div>
    """, unsafe_allow_html=True)

    if skills:
        wc = WordCloud(
            width=800, 
            height=400, 
            background_color="white", 
            max_words=100,
            colormap='viridis',
            relative_scaling=0.5
        ).generate(" ".join(skills))
        
        fig_wc, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        fig_wc.patch.set_facecolor('white')
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    else:
        st.info("💭 No skills detected to create visualization")

    # Improvement Suggestions
    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            💡 Improvement Recommendations
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_skills = [
        "Python", "Java", "C++", "C", "R", "JavaScript", "HTML", "CSS",
        "AI", "ML", "Data Science", "Machine Learning", "Deep Learning",
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch",
        "SQL", "MongoDB", "PostgreSQL", "Git", "Docker", "AWS", "Azure"
    ]
    
    suggestions = improvement_suggestions(skills, all_skills, ats_score, jd_text)
    
    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(f"""
        <div class="suggestion-item">
            <strong>{i}.</strong> {suggestion}
        </div>
        """, unsafe_allow_html=True)

    # Job Matching Section
    job_database = {
        "Python": ["Python Developer at Infosys", "Data Scientist at TCS"],
        "SQL": ["Data Engineer at Snowflake", "DB Admin at Oracle"],
        "JavaScript": ["Frontend Dev at Zomato", "Full Stack at Paytm"],
        "AI": ["AI Engineer at Google", "ML Engineer at OpenAI"]
    }
    
    matched_jobs = set()
    for sk in skills:
        if sk in job_database:
            matched_jobs.update(job_database[sk])

    if matched_jobs:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">
                💼 Potential Job Matches
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        for job in list(matched_jobs)[:6]:
            st.markdown(f"""
            <div class="job-match">
                🎯 {job}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 Upload a resume with technical skills to see job recommendations")

    # === ✅ YouTube Course Recommendations (must be indented here) ===
    with st.expander("🎥 Recommended YouTube Courses"):
        yt_courses = {
            "Python": [
                ("Python for Beginners", "https://www.youtube.com/watch?v=kqtD5dpn9C8"),
                ("Advanced Python Tutorial", "https://www.youtube.com/watch?v=HGOBQPFzWKo")
            ],
            "SQL": [
                ("SQL Full Course", "https://www.youtube.com/watch?v=HXV3zeQKqGY")
            ],
            "JavaScript": [
                ("JavaScript Crash Course", "https://www.youtube.com/watch?v=hdI2bqOjy3c")
            ],
            "AI": [
                ("Intro to Artificial Intelligence", "https://www.youtube.com/watch?v=JMUxmLyrhSk")
            ],
            "Data Science": [
                ("Data Science Full Course", "https://www.youtube.com/watch?v=-ETQ97mXXF0")
            ]
        }

        shown = False
        for sk in skills:
            if sk in yt_courses:
                st.markdown(
                    f"<div style='font-weight:600; color:#b30000; margin-top:10px;'>📌 {sk} Courses:</div>",
                    unsafe_allow_html=True
                )
                for title, link in yt_courses[sk]:
                    st.markdown(f"- [{title}]({link})")
                shown = True

        if not shown:
            st.info("No specific YouTube courses found for your skills. Try adding more technical keywords.")

