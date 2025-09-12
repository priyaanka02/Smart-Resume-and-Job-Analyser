# app.py
import streamlit as st
import spacy
import subprocess
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2, docx, io, os, re, json
from collections import Counter, defaultdict
#import openai
from difflib import SequenceMatcher
import altair as alt
import matplotlib.pyplot as plt

# Load spaCy model with better error handling
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    try:
        # Try to download the model
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
    except:
        st.warning("SpaCy model could not be loaded. Some features may be limited.")
        nlp = None

# error handling for NLTK downloads
try:
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)  
    nltk.download("wordnet", quiet=True)
    from nltk.corpus import stopwords, wordnet
    STOP_WORDS = set(stopwords.words('english'))
except:
    STOP_WORDS = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])

# -------------------------
# Modern Professional Styling
# -------------------------
def modern_ui_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Quicksand:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
        
        /* Main Background and Container */
        .stApp {
            background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 25%, #f3e8ff 50%, #e0f2fe 75%, #f0f9ff 100%);
            font-family: 'Quicksand', sans-serif;
        }
        
        /* Main Content Container */
        .main-container {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(15px);
            border-radius: 25px;
            padding: 2.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 20px 40px rgba(219, 39, 119, 0.1), 0 0 30px rgba(236, 72, 153, 0.05);
            border: 2px solid rgba(251, 207, 232, 0.6);
            animation: float 6s ease-in-out infinite;
            transition: all 0.5s ease;
        }
        
        .main-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(219, 39, 119, 0.15), 0 0 40px rgba(236, 72, 153, 0.08);
        }
        
        /* Title Styling */
        .stTitle {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            font-size: 3rem !important;
            background: linear-gradient(135deg, #ec4899, #a855f7, #06b6d4) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            text-align: center;
            margin-bottom: 1.5rem;
            text-shadow: none;
            letter-spacing: 0.5px;
        }
        
        /* Subheader Styling */
        .stSubheader {
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
            background: linear-gradient(135deg, #be185d, #7c3aed) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            margin: 2rem 0 1.2rem 0;
            letter-spacing: 0.5px;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fce7f3, #f3e8ff);
            border-radius: 0 20px 20px 0;
        }
        
        /* Button Styling */
        button[kind="primary"] {
            background: linear-gradient(135deg, #f9a8d4, #c084fc, #7dd3fc) !important;
            color: white !important;
            font-weight: 600;
            border-radius: 20px !important;
            padding: 0.85rem 2.5rem !important;
            border: none !important;
            box-shadow: 0 8px 20px rgba(249, 168, 212, 0.4);
            transition: all 0.4s ease;
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1rem !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        button[kind="primary"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 25px rgba(249, 168, 212, 0.5);
            background: linear-gradient(135deg, #ec4899, #a855f7, #06b6d4) !important;
        }
        
        /* Input Fields Styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 15px !important;
            border: 2px solid #fbcfe8 !important;
            padding: 1rem !important;
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1rem !important;
            background: rgba(255, 255, 255, 0.8) !important;
            box-shadow: 0 4px 15px rgba(249, 168, 212, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border: 2px solid #f9a8d4 !important;
            box-shadow: 0 6px 20px rgba(249, 168, 212, 0.3);
            background: rgba(255, 255, 255, 0.95) !important;
        }
        
        /* Metric Box Styling */
        .metric-box {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(253, 242, 248, 0.8));
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(236, 72, 153, 0.1);
            text-align: center;
            margin: 1.5rem 0;
            border: 2px solid rgba(251, 207, 232, 0.4);
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
        }
        
        .metric-box:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(236, 72, 153, 0.15);
            border: 2px solid rgba(249, 168, 212, 0.6);
        }
        
        /* Score Styling */
        .score-big {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ec4899, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            font-family: 'Montserrat', sans-serif;
        }
        
        /* Bullet Card Styling */
        .bullet-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(254, 242, 242, 0.7));
            padding: 1.5rem;
            border-radius: 18px;
            margin: 1.2rem 0;
            border-left: 6px solid #f9a8d4;
            box-shadow: 0 10px 25px rgba(249, 168, 212, 0.15);
            font-size: 1.1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .bullet-card:hover {
            transform: translateX(8px);
            box-shadow: 0 15px 30px rgba(249, 168, 212, 0.2);
            border-left: 6px solid #ec4899;
        }
        
        /* Insight Card Styling */
        .insight-card {
            background: linear-gradient(135deg, rgba(253, 242, 248, 0.8), rgba(240, 249, 255, 0.6));
            padding: 2rem;
            border-radius: 20px;
            margin: 1.5rem 0;
            border-left: 6px solid #c084fc;
            box-shadow: 0 12px 25px rgba(192, 132, 252, 0.15);
            font-size: 1.2rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(8px);
        }
        
        .insight-card:hover {
            transform: translateX(8px);
            box-shadow: 0 15px 35px rgba(192, 132, 252, 0.2);
        }
        
        /* Skill Tag Styling */
        .tag-skill {
            display: inline-block;
            background: linear-gradient(135deg, #f9a8d4, #c084fc);
            color: white;
            padding: 0.6rem 1.2rem;
            margin: 0.5rem;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 500;
            box-shadow: 0 6px 15px rgba(249, 168, 212, 0.3);
            transition: all 0.3s ease;
        }
        
        .tag-skill:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(249, 168, 212, 0.4);
            background: linear-gradient(135deg, #ec4899, #a855f7);
        }
        
        /* Text Styling */
        .warning-text {
            color: #f87171;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .success-text {
            color: #4ade80;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        /* Section Headers */
        h3 {
            font-family: 'Montserrat', sans-serif !important;
            font-size: 1.8rem !important;
            background: linear-gradient(135deg, #be185d, #7c3aed) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            margin-top: 2rem !important;
            margin-bottom: 1.5rem !important;
            letter-spacing: 0.5px;
        }
        
        /* Regular Text */
        p, li, div {
            font-size: 1.15rem !important;
            line-height: 1.6 !important;
            color: #64748b !important;
        }
        
        /* Animations */
        @keyframes float {
            0% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-10px);
            }
            100% {
                transform: translateY(0px);
            }
        }
        
        /* File Uploader Styling */
        [data-testid="stFileUploader"] {
            border-radius: 15px !important;
            border: 2px dashed #fbcfe8 !important;
            padding: 1rem !important;
            background: rgba(255, 255, 255, 0.5) !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border: 2px dashed #f9a8d4 !important;
            background: rgba(255, 255, 255, 0.8) !important;
        }
        
        /* Download Button Styling */
        .stDownloadButton button {
            background: linear-gradient(135deg, #f9a8d4, #c084fc) !important;
            color: white !important;
            font-weight: 600;
            border-radius: 20px !important;
            padding: 0.85rem 2.5rem !important;
            border: none !important;
            box-shadow: 0 8px 20px rgba(249, 168, 212, 0.3);
            transition: all 0.4s ease;
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1rem !important;
            letter-spacing: 0.5px;
        }
        
        .stDownloadButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 25px rgba(249, 168, 212, 0.4);
        }
        
        /* Spinner Styling */
        .stSpinner > div {
            border-color: #f9a8d4 !important;
        }
        
        /* Error and Info Messages */
        .stAlert {
            border-radius: 15px !important;
            border: 2px solid #fbcfe8 !important;
            font-family: 'Quicksand', sans-serif;
            font-size: 1.1rem !important;
            background: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* Divider Styling */
        hr {
            border: none;
            height: 3px;
            background: linear-gradient(90deg, transparent, #f9a8d4, #c084fc, transparent);
            margin: 2rem 0;
        }
        
        /* Emoji Styling */
        .emoji-large {
            font-size: 2rem;
            margin-right: 0.5rem;
            vertical-align: middle;
        }
        
        /* Progress Bar Styling */
        .stProgress > div > div {
            background: linear-gradient(90deg, #f9a8d4, #c084fc) !important;
        }
        
        /* Checkbox Styling */
        .stCheckbox label {
            font-size: 1.1rem !important;
            color: #64748b !important;
        }
        
        /* Selectbox Styling */
        .stSelectbox > div > div {
            border-radius: 15px !important;
            border: 2px solid #fbcfe8 !important;
            background: rgba(255, 255, 255, 0.8) !important;
        }
        
        /* Tooltip Styling */
        .stTooltip {
            font-family: 'Quicksand', sans-serif;
            font-size: 1rem !important;
        }
        
        /* Skills Container */
        .skills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Two Column Layout */
        .two-column-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }
        
        @media (max-width: 768px) {
            .two-column-container {
                grid-template-columns: 1fr;
            }
        }
        
        /* Pie Chart Container */
        .chart-container {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(253, 242, 248, 0.7));
            padding: 1.5rem;
            border-radius: 20px;
            box-shadow: 0 12px 25px rgba(249, 168, 212, 0.15);
            margin: 1.5rem 0;
            border: 2px solid rgba(251, 207, 232, 0.4);
            backdrop-filter: blur(8px);
        }
        
        .chart-title {
            font-family: 'Montserrat', sans-serif;
            font-size: 1.4rem;
            font-weight: 600;
            background: linear-gradient(135deg, #ec4899, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

modern_ui_css()

# -------------------------
# Setup & resources
# -------------------------
st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")


@st.cache_resource(ttl=3600)
def load_model():
    try:
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        st.warning(f"Could not load sentence transformer model: {e}")
        return None

model = load_model()


# -------------------------
# Enhanced Matching Utilities
# -------------------------

# Skill synonym dictionary for common tech terms
SKILL_SYNONYMS = {
    # Programming Languages
    "python": ["py", "python3", "python programming"],
    "javascript": ["js", "ecmascript", "node.js", "nodejs", "node"],
    "typescript": ["ts"],
    "java": ["jdk", "j2ee", "java programming"],
    "c++": ["cpp", "c plus plus", "cplusplus"],
    "c#": ["csharp", "c sharp", ".net"],
    
    # Web Development
    "frontend": ["front-end", "front end", "client-side"],
    "backend": ["back-end", "back end", "server-side"],
    "fullstack": ["full-stack", "full stack"],
    "react": ["reactjs", "react.js"],
    "angular": ["angularjs", "angular.js"],
    "vue": ["vuejs", "vue.js"],
    
    # Cloud & DevOps
    "aws": ["amazon web services", "amazon cloud", "ec2", "s3", "lambda"],
    "azure": ["microsoft azure", "azure cloud", "microsoft cloud"],
    "gcp": ["google cloud", "google cloud platform"],
    "devops": ["dev ops", "development operations"],
    "ci/cd": ["ci cd", "continuous integration", "continuous deployment", "cicd"],
    "docker": ["container", "containerization", "docker container"],
    "kubernetes": ["k8s", "k-8", "kube"],
    
    # Security
    "cybersecurity": ["cyber security", "cyber-security", "information security", "infosec"],
    "penetration testing": ["pentest", "pen test", "pen-test", "pentesting"],
    "vulnerability assessment": ["vuln assessment", "vulnerability scanning", "vulnerability management"],
    "security assessment": ["security testing", "security evaluation", "security audit"],
    "secure sdlc": ["secure development lifecycle", "security sdlc", "secure software development"],
    "encryption": ["cryptography", "crypto", "cipher"],
    "compliance": ["regulatory compliance", "governance", "regulatory"],
    "iso 27001": ["iso27001", "27001", "iso 27k"],
    "nist": ["nist framework", "nist cybersecurity", "nist standards"],
    
    # Data Science
    "machine learning": ["ml", "ai", "artificial intelligence"],
    "data science": ["data analytics", "data analysis", "analytics"],
    "deep learning": ["neural networks", "dl", "neural nets"],
    "nlp": ["natural language processing", "text analytics", "text mining"],
    
    # Databases
    "sql": ["mysql", "postgresql", "oracle", "relational database", "rdbms"],
    "nosql": ["mongodb", "dynamodb", "cassandra", "non-relational database"],
    
    # Roles & Positions
    "software engineer": ["software developer", "programmer", "coder", "swe"],
    "security engineer": ["security developer", "application security engineer", "appsec engineer"],
    "data scientist": ["data analyst", "analytics engineer", "ml engineer"],
    "product manager": ["pm", "product owner", "product lead"],
    "project manager": ["project lead", "project coordinator", "technical project manager"],
}

# Function to get synonyms for a term
def get_synonyms(term):
    """Get common synonyms for technical terms"""
    term_lower = term.lower()
    
    # Check our custom tech synonym dictionary first
    for main_term, synonyms in SKILL_SYNONYMS.items():
        if term_lower == main_term or term_lower in synonyms:
            result = [main_term] + synonyms
            return [s for s in result if s != term_lower]
    
    # Try WordNet for general English synonyms
    synonyms = []
    try:
        for syn in wordnet.synsets(term_lower):
            for lemma in syn.lemmas():
                if lemma.name().lower() != term_lower and lemma.name().lower() not in synonyms:
                    synonyms.append(lemma.name().lower().replace('_', ' '))
    except:
        pass
    
    return synonyms[:5]  # Limit to top 5 synonyms to avoid noise

# Fuzzy matching function
def fuzzy_match(str1, str2, threshold=0.8):
    """Check if two strings match with a similarity above threshold"""
    if not str1 or not str2:
        return False
    
    # Direct match
    if str1.lower() == str2.lower():
        return True
    
    # Fuzzy match using sequence matcher
    similarity = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return similarity >= threshold

# Function to check if a skill is present in text, including synonyms and fuzzy matching
def skill_exists_in_text(skill, text, threshold=0.75):
    """Check if a skill or its synonyms exist in the text"""
    if not text:
        return False
        
    text_lower = text.lower()
    skill_lower = skill.lower()
    
    # Direct match
    if skill_lower in text_lower:
        return True
    
    # Check for skill with word boundaries
    skill_pattern = r'\b' + re.escape(skill_lower) + r'\b'
    if re.search(skill_pattern, text_lower):
        return True
    
    # Check synonyms
    synonyms = get_synonyms(skill_lower)
    for synonym in synonyms:
        if synonym in text_lower:
            return True
        
        # Check synonym with word boundaries
        synonym_pattern = r'\b' + re.escape(synonym) + r'\b'
        if re.search(synonym_pattern, text_lower):
            return True
    
    # Fuzzy matching for longer skills (to avoid false positives with short terms)
    if len(skill_lower) > 3:
        words = text_lower.split()
        for word in words:
            if fuzzy_match(skill_lower, word, threshold):
                return True
    
    return False

# -------------------------
# Core Analysis Functions
# -------------------------

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file"""
    name = uploaded_file.name.lower()
    content = uploaded_file.read()
    
    if name.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Could not read PDF file: {e}")
            return ""
    
    elif name.endswith(".docx"):
        try:
            doc = docx.Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Could not read DOCX file: {e}")
            return ""
    
    else:
        try:
            return content.decode("utf-8")
        except Exception as e:
            st.error(f"Could not read file: {e}")
            return ""

def parse_job_description(jd_text):
    """Parse job description to understand what they actually want"""
    
    # Clean the text
    jd_clean = re.sub(r'\s+', ' ', jd_text.strip())
    
    # Extract role context
    role_match = re.search(r'(intern|engineer|developer|analyst|manager|specialist|coordinator|professional|student)', jd_clean.lower())
    role_level = role_match.group(1) if role_match else "professional"
    
    # Find key responsibility sections
    sentences = []
    if nlp:
        doc = nlp(jd_clean)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 5]
    else:
        # Simple sentence splitting if spaCy is not available
        for sent in re.split(r'[.!?]+', jd_clean):
            if len(sent.split()) > 5:
                sentences.append(sent.strip())
    
    # Categorize sentences
    must_haves = []
    nice_to_haves = []
    responsibilities = []
    
    for sent in sentences:
        sent_lower = sent.lower()
        
        # Strong requirements
        if any(phrase in sent_lower for phrase in ['must have', 'required', 'essential', 'mandatory', 'need to have']):
            must_haves.append(sent.strip())
        
        # Preferences  
        elif any(phrase in sent_lower for phrase in ['prefer', 'nice to have', 'bonus', 'plus', 'advantage']):
            nice_to_haves.append(sent.strip())
            
        # Responsibilities
        elif any(phrase in sent_lower for phrase in ['will be', 'responsible for', 'duties include', 'you will', 'role involves', 'what you will be doing', 'you will be']):
            responsibilities.append(sent.strip())
    
    # Extract technical skills and tools - Enhanced with more patterns
    tech_keywords = []
    
    # Expanded tech patterns with more security-related terms
    tech_patterns = [
        r'\b(python|java|javascript|typescript|react|angular|vue|nodejs|php|ruby|go|rust|swift|kotlin|c\+\+|c#)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?(?:\s+programming)?\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible|cloud)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(mysql|postgresql|mongodb|redis|elasticsearch|sql|nosql|database)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(git|github|gitlab|jira|confluence|slack|teams)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(linux|unix|windows|macos|ubuntu|centos)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(html|css|sass|less|bootstrap|tailwind)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(api|rest|graphql|microservices|devops|ci/cd|agile|scrum)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(machine learning|ai|data science|analytics|big data|pandas|numpy|scikit-learn|tensorflow|pytorch)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(cybersecurity|security|penetration testing|vulnerability|compliance|encryption|cryptography|iso 27001|nist|secure sdlc)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(iso\s*\d+|gdpr|hipaa|sox|pci|nist)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(flask|django|express|spring|laravel|symfony)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(tableau|power bi|looker|data visualization)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b',
        r'\b(electron\.js|electron|desktop application)(?:\s+\d+(?:\.\d+)*)?(?:\s+(?:years?|yrs?))?(?:\s+(?:of\s+)?experience)?(?:\s+(?:with|in))?\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.finditer(pattern, jd_clean.lower())
        for match in matches:
            skill = match.group(1).strip()  # Extract just the skill name, not years
            if skill not in tech_keywords:
                tech_keywords.append(skill)
    
    # Also look for skills mentioned in bullet points or after colons
    skill_indicators = [
        r'skills[^\n:]*:([^\n]+)',
        r'technologies[^\n:]*:([^\n]+)',
        r'requirements[^\n:]*:([^\n]+)',
        r'qualifications[^\n:]*:([^\n]+)',
        r'experience with ([^.,;]+)',
        r'knowledge of ([^.,;]+)',
        r'proficient in ([^.,;]+)',
        r'familiarity with ([^.,;]+)'
    ]
    
    for pattern in skill_indicators:
        matches = re.finditer(pattern, jd_clean.lower())
        for match in matches:
            skill_text = match.group(1).strip()
            # Split by common separators
            for skill in re.split(r',|\s+and\s+|\s+or\s+|\s*/\s*|\s+\+\s+|\s+&\s+', skill_text):
                clean_skill = skill.strip()
                if clean_skill and len(clean_skill) > 2 and clean_skill not in tech_keywords:
                    tech_keywords.append(clean_skill)
    
    # Add some common skills that might be implied but not explicitly mentioned
    if "security" in jd_clean.lower() and "security" not in tech_keywords:
        tech_keywords.append("security")
    
    if "software" in jd_clean.lower() and "programming" not in tech_keywords:
        tech_keywords.append("programming")
        
    if "development" in jd_clean.lower() and "software development" not in tech_keywords:
        tech_keywords.append("software development")
    
    # Industry/Domain context
    domain_indicators = {
        'fintech': ['bank', 'finance', 'payment', 'trading', 'fintech', 'investment'],
        'healthcare': ['health', 'medical', 'patient', 'clinical', 'pharma'],
        'ecommerce': ['ecommerce', 'retail', 'shopping', 'marketplace', 'commerce'],
        'saas': ['saas', 'software as a service', 'subscription', 'platform'],
        'startup': ['startup', 'fast-paced', 'scale-up', 'growth'],
        'enterprise': ['enterprise', 'corporation', 'large scale', 'fortune'],
        'energy': ['energy', 'power', 'solar', 'renewable', 'grid', 'utility'],
        'security': ['security', 'cybersecurity', 'infosec', 'compliance', 'risk', 'protection']
    }
    
    domain = 'general'
    for dom, keywords in domain_indicators.items():
        if any(keyword in jd_clean.lower() for keyword in keywords):
            domain = dom
            break
    
    return {
        'role_level': role_level,
        'domain': domain,
        'must_haves': must_haves[:5],  # Increased from 3 to 5
        'nice_to_haves': nice_to_haves[:5],  # Increased from 3 to 5
        'responsibilities': responsibilities[:5],  # Increased from 3 to 5
        'tech_keywords': tech_keywords,
        'all_sentences': sentences
    }

def parse_resume_intelligently(resume_text):
    """Parse resume to understand candidate's actual experience"""
    
    # Clean and structure
    resume_clean = re.sub(r'\s+', ' ', resume_text.strip())
    
    # Extract structured information
    parsed_resume = {
        'experience_bullets': [],
        'skills_mentioned': [],
        'education_info': [],
        'projects': [],
        'certifications': [],
        'achievements': []
    }
    
    # Split into lines for better parsing
    lines = resume_clean.split('\n')
    current_section = 'general'
    
    # Enhanced section detection patterns
    section_patterns = {
        'experience': r'(experience|work|employment|professional|career|work history)',
        'education': r'(education|degree|academic|university|college|school)',
        'skills': r'(skills|technical|technologies|tools|competenc|proficienc)',
        'projects': r'(projects|portfolio|work samples)',
        'certifications': r'(certification|certificate|license|credential)',
        'summary': r'(summary|profile|objective|about)'
    }
    
    # First pass: identify sections
    section_boundaries = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line.split()) < 1:
            continue
            
        line_lower = line.lower()
        
        # Detect section headers
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line.split()) <= 5:
                section_boundaries.append((i, section))
    
    # Add an end boundary
    section_boundaries.append((len(lines), 'end'))
    
    # Second pass: extract content by section
    for i in range(len(section_boundaries) - 1):
        current_section = section_boundaries[i][1]
        start_line = section_boundaries[i][0] + 1  # Skip the header
        end_line = section_boundaries[i+1][0]
        
        section_content = lines[start_line:end_line]
        
        # Process based on section type
        if current_section == 'experience':
            # Extract experience bullets
            for line in section_content:
                line = line.strip()
                if not line or len(line.split()) < 3:
                    continue
                
                # Clean bullet points
                clean_bullet = re.sub(r'^[•\-\*\+]+\s*', '', line).strip()
                if clean_bullet and not any(x in clean_bullet.lower() for x in ['email', 'phone', 'linkedin', 'github']):
                    parsed_resume['experience_bullets'].append(clean_bullet)
        
        elif current_section == 'skills':
            # Extract skills - both as a list and from paragraphs
            skills_text = ' '.join(section_content)
            
            # First try to find skills listed with commas or bullets
            skills_list = re.split(r'[,•\-\*\+]|\s+and\s+', skills_text)
            for skill in skills_list:
                skill = skill.strip()
                if skill and len(skill) > 2 and skill.lower() not in STOP_WORDS:
                    parsed_resume['skills_mentioned'].append(skill)
            
            # Also look for skills mentioned in context
            skill_patterns = [
                r'proficient in ([^.,;]+)',
                r'experience with ([^.,;]+)',
                r'knowledge of ([^.,;]+)',
                r'skilled in ([^.,;]+)',
                r'familiar with ([^.,;]+)'
            ]
            
            for pattern in skill_patterns:
                matches = re.finditer(pattern, skills_text.lower())
                for match in matches:
                    skill_text = match.group(1).strip()
                    if skill_text and len(skill_text) > 2:
                        parsed_resume['skills_mentioned'].append(skill_text)
        
        elif current_section == 'education':
            for line in section_content:
                line = line.strip()
                if line and len(line.split()) > 2:
                    parsed_resume['education_info'].append(line)
        
        elif current_section == 'certifications':
            for line in section_content:
                line = line.strip()
                if line and len(line.split()) > 1:
                    parsed_resume['certifications'].append(line)
        
        elif current_section == 'projects':
            for line in section_content:
                line = line.strip()
                if line and len(line.split()) > 3:
                    parsed_resume['projects'].append(line)
        
        elif current_section == 'summary':
            # Extract skills mentioned in summary
            summary_text = ' '.join(section_content)
            
            # Look for technical terms in summary
            tech_patterns = [
                r'\b(python|java|javascript|typescript|react|angular|vue|nodejs|php|ruby|go|rust|swift|kotlin|c\+\+|c#)\b',
                r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible|cloud)\b',
                r'\b(mysql|postgresql|mongodb|redis|elasticsearch|sql|nosql|database)\b',
                r'\b(git|github|gitlab|jira|confluence|slack|teams)\b',
                r'\b(linux|unix|windows|macos|ubuntu|centos)\b',
                r'\b(html|css|sass|less|bootstrap|tailwind)\b',
                r'\b(api|rest|graphql|microservices|devops|ci/cd|agile|scrum)\b',
                r'\b(machine learning|ai|data science|analytics|big data|pandas|numpy|scikit-learn|tensorflow|pytorch)\b',
                r'\b(cybersecurity|security|penetration testing|vulnerability|compliance|encryption|cryptography|iso 27001|nist|secure sdlc)\b',
                r'\b(iso\s*\d+|gdpr|hipaa|sox|pci|nist)\b',
                r'\b(flask|django|express|spring|laravel|symfony)\b',
                r'\b(tableau|power bi|looker|data visualization)\b'
            ]
            
            for pattern in tech_patterns:
                matches = re.finditer(pattern, summary_text.lower())
                for match in matches:
                    skill = match.group(1).strip()
                    if skill not in parsed_resume['skills_mentioned']:
                        parsed_resume['skills_mentioned'].append(skill)
    
    # If no sections were found, try a simpler approach
    if not section_boundaries or len(section_boundaries) <= 1:
        # Look for skills throughout the resume
        tech_patterns = [
            r'\b(python|java|javascript|typescript|react|angular|vue|nodejs|php|ruby|go|rust|swift|kotlin|c\+\+|c#)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible|cloud)\b',
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch|sql|nosql|database)\b',
            r'\b(git|github|gitlab|jira|confluence|slack|teams)\b',
            r'\b(linux|unix|windows|macos|ubuntu|centos)\b',
            r'\b(html|css|sass|less|bootstrap|tailwind)\b',
            r'\b(api|rest|graphql|microservices|devops|ci/cd|agile|scrum)\b',
            r'\b(machine learning|ai|data science|analytics|big data|pandas|numpy|scikit-learn|tensorflow|pytorch)\b',
            r'\b(cybersecurity|security|penetration testing|vulnerability|compliance|encryption|cryptography|iso 27001|nist|secure sdlc)\b',
            r'\b(iso\s*\d+|gdpr|hipaa|sox|pci|nist)\b',
            r'\b(flask|django|express|spring|laravel|symfony)\b',
            r'\b(tableau|power bi|looker|data visualization)\b',
            r'\b(electron\.js|electron|desktop application)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, resume_clean.lower())
            for match in matches:
                skill = match.group(1).strip()
                if skill not in parsed_resume['skills_mentioned']:
                    parsed_resume['skills_mentioned'].append(skill)
        
        # Look for bullet points that might be experience
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                clean_bullet = re.sub(r'^[•\-\*\+]+\s*', '', line).strip()
                if clean_bullet and len(clean_bullet.split()) > 5:
                    parsed_resume['experience_bullets'].append(clean_bullet)
    
    # Extract achievements (lines with numbers/percentages)
    for bullet in parsed_resume['experience_bullets']:
        if re.search(r'\d+[%$]?|\$\d+|increased|improved|reduced|saved|achieved|developed|implemented|created|designed', bullet.lower()):
            parsed_resume['achievements'].append(bullet)
    
    # If no skills were found in a dedicated section, try to extract them from experience
    if not parsed_resume['skills_mentioned']:
        experience_text = ' '.join(parsed_resume['experience_bullets'])
        
        # Common technical skills to look for
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node', 
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'git', 'github', 'gitlab', 'jira', 'confluence',
            'linux', 'unix', 'windows', 'macos',
            'html', 'css', 'sass', 'bootstrap', 'tailwind',
            'api', 'rest', 'graphql', 'microservices', 'devops', 'ci/cd', 'agile', 'scrum',
            'machine learning', 'ai', 'data science', 'analytics', 'pandas', 'numpy',
            'cybersecurity', 'security', 'penetration testing', 'vulnerability', 'compliance',
            'iso 27001', 'nist', 'gdpr', 'hipaa',
            'flask', 'django', 'express', 'spring',
            'tableau', 'power bi', 'data visualization',
            'encryption', 'cryptography', 'secure sdlc'
        ]
        
        for skill in common_skills:
            if skill_exists_in_text(skill, experience_text):
                parsed_resume['skills_mentioned'].append(skill)
    
    # Add some common skills that might be implied but not explicitly mentioned
    if "security" in resume_clean.lower() and "security" not in [s.lower() for s in parsed_resume['skills_mentioned']]:
        parsed_resume['skills_mentioned'].append("security")
    
    if any(term in resume_clean.lower() for term in ["develop", "code", "program", "software"]) and "programming" not in [s.lower() for s in parsed_resume['skills_mentioned']]:
        parsed_resume['skills_mentioned'].append("programming")
    
    # Remove duplicates while preserving order
    parsed_resume['skills_mentioned'] = list(dict.fromkeys(parsed_resume['skills_mentioned']))
    
    return parsed_resume

def intelligent_matching(resume_data, job_data):
    """Smart matching that understands context, not just keywords"""
    
    # Initialize default values to prevent KeyError
    default_result = {
        'overall_match': 0,
        'semantic_score': 0,
        'tech_score': 0,
        'tech_matches': [],
        'job_tech_keywords': job_data.get('tech_keywords', []),
        'explanation': "Insufficient content to analyze",
        'recommendations': []
    }
    
    # Prepare texts for semantic analysis
    resume_experience_text = ' '.join(resume_data['experience_bullets'][:10])  # Top bullets
    resume_skills_text = ' '.join(resume_data['skills_mentioned'])
    
    # Combine all resume text for better context
    all_resume_text = resume_experience_text + " " + resume_skills_text
    for section in ['education_info', 'certifications', 'projects', 'achievements']:
        all_resume_text += " " + ' '.join(resume_data.get(section, []))
    
    job_requirements_text = ' '.join(job_data['must_haves'] + job_data['responsibilities'])
    job_all_text = ' '.join(job_data['all_sentences'])
    
    # Ensure we have enough content to analyze
    if len(all_resume_text.split()) < 10 or len(job_requirements_text.split()) < 10:
        # Try a simplified approach if we don't have enough structured content
        job_tech_keywords = job_data.get('tech_keywords', [])
        resume_skills = resume_data.get('skills_mentioned', [])
        
        # Find matches using fuzzy matching and synonyms
        tech_matches = []
        for job_skill in job_tech_keywords:
            # Direct match
            if job_skill.lower() in [skill.lower() for skill in resume_skills]:
                tech_matches.append(job_skill)
                continue
            
            # Check if any resume skill is a synonym of this job skill
            job_skill_synonyms = get_synonyms(job_skill)
            for resume_skill in resume_skills:
                if resume_skill.lower() in [syn.lower() for syn in job_skill_synonyms]:
                    tech_matches.append(job_skill)
                    break
            
            # Check if the skill exists in the entire resume text
            if job_skill not in tech_matches and skill_exists_in_text(job_skill, all_resume_text):
                tech_matches.append(job_skill)
        
        # Calculate tech score with a minimum baseline
        tech_score = len(tech_matches) / max(len(job_tech_keywords), 1) if job_tech_keywords else 0.5
        
        # Ensure a minimum tech score if we have any matches
        if tech_matches and tech_score < 0.2:
            tech_score = 0.2
        
        # Calculate overall match (simplified)
        overall_match = tech_score * 100
        
        # Ensure a minimum overall score if we have good indicators
        if len(tech_matches) >= 3 and overall_match < 40:
            overall_match = 40
        
        # Generate explanation
        explanation_parts = []
        
        if tech_score > 0.7:
            explanation_parts.append("Excellent technical skills match")
        elif tech_score > 0.5:
            explanation_parts.append("Strong technical skills match")
        elif tech_score > 0.3:
            explanation_parts.append("Good technical skills match")
        elif tech_score > 0.1:
            explanation_parts.append("Some relevant technical skills identified")
        else:
            explanation_parts.append("Technical skills gap identified")
        
        explanation = ". ".join(explanation_parts) + "."
        
        return {
            'overall_match': round(overall_match, 1),
            'semantic_score': 50.0,  # Default moderate score
            'tech_score': round(tech_score * 100, 1),
            'tech_matches': tech_matches,
            'job_tech_keywords': job_tech_keywords,
            'explanation': explanation
        }
    
    # Semantic similarity - enhanced with multiple comparisons
    try:
        if model:
            # Compare resume experience to job requirements
            resume_exp_emb = model.encode([resume_experience_text]) if resume_experience_text else model.encode([""])
            job_req_emb = model.encode([job_requirements_text])
            exp_req_similarity = cosine_similarity(resume_exp_emb, job_req_emb)[0][0] if resume_experience_text else 0.0
            
            # Compare all resume text to all job text for broader context
            all_resume_emb = model.encode([all_resume_text])
            job_all_emb = model.encode([job_all_text])
            all_similarity = cosine_similarity(all_resume_emb, job_all_emb)[0][0]
            
            # Compare resume skills to job tech keywords
            resume_skills_emb = model.encode([resume_skills_text]) if resume_skills_text else model.encode([""])
            job_tech_text = ' '.join(job_data.get('tech_keywords', []))
            job_tech_emb = model.encode([job_tech_text]) if job_tech_text else model.encode([""])
            skills_similarity = cosine_similarity(resume_skills_emb, job_tech_emb)[0][0] if resume_skills_text and job_tech_text else 0.0
            
            # Weighted combination of similarities
            semantic_score = (0.4 * exp_req_similarity) + (0.4 * all_similarity) + (0.2 * skills_similarity)
        else:
            # Fallback if model is not available
            semantic_score = 0.5  # Default moderate score
    except Exception as e:
        st.error(f"Error in semantic matching: {e}")
        semantic_score = 0.5  # Default moderate score
    
    # Domain/Role alignment
    role_alignment = 0.7  # Default decent alignment
    
    # Adjust based on role level
    if job_data['role_level'] == 'intern' or job_data['role_level'] == 'student':
        # For internships, focus on potential and relevant coursework
        if any(word in all_resume_text.lower() for word in ['student', 'course', 'project', 'learn', 'university', 'college', 'education']):
            role_alignment += 0.2
    elif job_data['role_level'] in ['senior', 'lead', 'manager']:
        # For senior roles, look for leadership experience
        leadership_words = ['led', 'managed', 'directed', 'supervised', 'coordinated', 'leadership', 'team', 'strategy']
        if any(word in all_resume_text.lower() for word in leadership_words):
            role_alignment += 0.2
    
    # Technical skills overlap - Enhanced with fuzzy matching and synonyms
    job_tech_keywords = job_data.get('tech_keywords', [])
    resume_skills = resume_data.get('skills_mentioned', [])
    
    # Combine explicit skills with skills extracted from experience
    all_resume_skills = resume_skills.copy()
    
    # Extract skills from experience bullets that might not be in skills section
    for bullet in resume_data.get('experience_bullets', []):
        for tech in job_tech_keywords:
            if skill_exists_in_text(tech, bullet) and tech not in all_resume_skills:
                all_resume_skills.append(tech)
    
    # Find matches using fuzzy matching and synonyms
    tech_matches = []
    for job_skill in job_tech_keywords:
        # Direct match
        if job_skill.lower() in [skill.lower() for skill in all_resume_skills]:
            tech_matches.append(job_skill)
            continue
        
        # Check if any resume skill is a synonym of this job skill
        job_skill_synonyms = get_synonyms(job_skill)
        for resume_skill in all_resume_skills:
            if resume_skill.lower() in [syn.lower() for syn in job_skill_synonyms]:
                tech_matches.append(job_skill)
                break
        
        # Check if the skill exists in the entire resume text
        if job_skill not in tech_matches and skill_exists_in_text(job_skill, all_resume_text):
            tech_matches.append(job_skill)
    
    # Calculate tech score with a minimum baseline
    tech_score = len(tech_matches) / max(len(job_tech_keywords), 1) if job_tech_keywords else 0.5
    
    # Ensure a minimum tech score if we have any matches
    if tech_matches and tech_score < 0.2:
        tech_score = 0.2
    
    # Calculate overall match (weighted combination)
    overall_match = (
        0.4 * semantic_score +          # How well experience aligns
        0.3 * role_alignment +          # Role level fit  
        0.3 * tech_score                # Technical skills match
    ) * 100
    
    # Ensure a minimum overall score if we have good indicators
    if semantic_score > 0.5 and overall_match < 30:
        overall_match = 30
    
    if len(tech_matches) >= 3 and overall_match < 40:
        overall_match = 40
    
    # Generate explanation
    explanation_parts = []
    
    if semantic_score > 0.6:
        explanation_parts.append("Strong alignment between your experience and job responsibilities")
    elif semantic_score > 0.4:
        explanation_parts.append("Good alignment - relevant experience found")
    elif semantic_score > 0.2:
        explanation_parts.append("Moderate alignment - some relevant experience found")
    else:
        explanation_parts.append("Limited direct experience match - consider highlighting transferable skills")
    
    if tech_score > 0.7:
        explanation_parts.append("Excellent technical skills match")
    elif tech_score > 0.5:
        explanation_parts.append("Strong technical skills match")
    elif tech_score > 0.3:
        explanation_parts.append("Good technical skills match")
    elif tech_score > 0.1:
        explanation_parts.append("Some relevant technical skills identified")
    else:
        explanation_parts.append("Technical skills gap identified")
    
    explanation = ". ".join(explanation_parts) + "."
    
    return {
        'overall_match': round(overall_match, 1),
        'semantic_score': round(semantic_score * 100, 1),
        'tech_score': round(tech_score * 100, 1),
        'tech_matches': tech_matches,
        'job_tech_keywords': job_data.get('tech_keywords', []),
        'explanation': explanation
    }

def generate_smart_recommendations(resume_data, job_data, match_results):
    """Generate contextual, intelligent recommendations"""
    
    recommendations = {
        'resume_bullets': [],
        'interview_prep': [],
        'skill_development': [],
        'application_strategy': []
    }
    
    # Generate better resume bullets from actual experience
    if resume_data.get('experience_bullets', []):
        # Get most relevant bullets using semantic similarity
        job_context = ' '.join(job_data.get('must_haves', []) + job_data.get('responsibilities', []))
        
        if job_context.strip():
            try:
                if model:
                    job_emb = model.encode([job_context])
                    bullet_scores = []
                    
                    for bullet in resume_data['experience_bullets'][:8]:  # Top 8 bullets
                        if len(bullet.split()) > 4:  # Substantial bullets only
                            bullet_emb = model.encode([bullet])
                            score = cosine_similarity(job_emb, bullet_emb)[0][0]
                            bullet_scores.append((bullet, score))
                    
                    # Get top scoring bullets
                    top_bullets = sorted(bullet_scores, key=lambda x: x[1], reverse=True)[:4]
                    
                    for bullet, score in top_bullets:
                        # Clean and improve the bullet
                        clean_bullet = re.sub(r'^[•\-\*]+\s*', '', bullet).strip()
                        
                        # Ensure it starts with action verb
                        action_verbs = ['Developed', 'Led', 'Implemented', 'Designed', 'Managed', 'Created', 'Built', 'Optimized']
                        if not any(clean_bullet.startswith(verb) for verb in action_verbs):
                            # Add appropriate verb based on content
                            if any(word in clean_bullet.lower() for word in ['develop', 'build', 'create']):
                                clean_bullet = "Developed " + clean_bullet.lower()
                            elif any(word in clean_bullet.lower() for word in ['manage', 'lead', 'coordinate']):
                                clean_bullet = "Led " + clean_bullet.lower()
                            else:
                                clean_bullet = "Implemented " + clean_bullet.lower()
                        
                        recommendations['resume_bullets'].append("• " + clean_bullet)
                else:
                    # Fallback if model is not available
                    for bullet in resume_data.get('experience_bullets', [])[:4]:
                        clean_bullet = re.sub(r'^[•\-\*]+\s*', '', bullet).strip()
                        recommendations['resume_bullets'].append("• " + clean_bullet)
                    
            except Exception as e:
                # Fallback to top experience bullets
                for bullet in resume_data.get('experience_bullets', [])[:3]:
                    clean_bullet = re.sub(r'^[•\-\*]+\s*', '', bullet).strip()
                    recommendations['resume_bullets'].append("• " + clean_bullet)
    
    # Interview preparation based on job requirements
    if job_data.get('must_haves', []):
        recommendations['interview_prep'].append(
            f"Prepare specific examples related to: {', '.join([req.split('.')[0] for req in job_data['must_haves'][:3]])}"
        )
    
    # Safely get tech_matches with default empty list
    tech_matches = match_results.get('tech_matches', [])
    if tech_matches:
        recommendations['interview_prep'].append(
            f"Be ready to discuss your experience with: {', '.join(tech_matches[:5])}"
        )
    
    recommendations['interview_prep'].append(
        "Prepare questions about the company's technology stack and team structure"
    )
    
    # Skill development suggestions - safely get tech keywords
    job_tech_keywords = job_data.get('tech_keywords', [])
    missing_skills = set(job_tech_keywords) - set(tech_matches)
    if missing_skills:
        recommendations['skill_development'].append(
            f"Consider gaining experience with: {', '.join(list(missing_skills)[:5])}"
        )
    
    # Application strategy
    overall_match = match_results.get('overall_match', 0)
    if overall_match >= 70:
        recommendations['application_strategy'].append("Strong match - apply with confidence and highlight your relevant experience")
    elif overall_match >= 50:
        recommendations['application_strategy'].append("Good potential - emphasize transferable skills and enthusiasm to learn")
    else:
        recommendations['application_strategy'].append("Consider gaining more relevant experience or applying to similar but more entry-level positions")
    
    return recommendations

# Function to create a pie chart for skills match
def create_skills_match_chart(tech_matches, job_tech_keywords):
    import matplotlib.pyplot as plt
    import io
    import base64
    
    # Calculate matched and missing skills
    matched = len(tech_matches)
    missing = len(set(job_tech_keywords) - set(tech_matches))
    
    # Create data for pie chart
    labels = ['Matched Skills', 'Missing Skills']
    sizes = [matched, missing]
    colors = ['#f9a8d4', '#c084fc']
    explode = (0.1, 0)  # explode the 1st slice (Matched Skills)
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Skills Match Analysis', fontsize=14, fontweight='bold')
    
    # Save to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    # Encode the image to base64
    img_str = base64.b64encode(buf.read()).decode()
    
    # Create the HTML for the image
    html = f'<img src="data:image/png;base64,{img_str}" style="width:100%; max-width:400px; margin:0 auto; display:block;">'
    
    return html

# -------------------------
# Streamlit App
# -------------------------

st.title("🎯 Smart Resume × Job Matcher")

st.markdown("""
<div class="main-container">
<p style="text-align: center; color: #4361ee; font-size: 1.1rem; margin: 0;">
Intelligent analysis that understands context, not just keywords
</p>
</div>
""", unsafe_allow_html=True)

# Input sections
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload resume file", 
        type=["pdf", "docx", "txt"]
    )
    
    resume_text = st.text_area(
        "Or paste resume text", 
        height=200,
        placeholder="Paste your complete resume here..."
    )

with col2:
    st.markdown("### 💼 Job Description")
    job_text = st.text_area(
        "Paste the job requirements / qualifications here",
        height=300,
        placeholder="Include all details: requirements, responsibilities, qualifications..."
    )

# Analysis button
if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
    
    # Input validation
    if not job_text.strip():
        st.error("Please provide a job description to analyze against.")
        st.stop()
    
    if uploaded_file is None and not resume_text.strip():
        st.error("Please provide your resume (upload file or paste text).")
        st.stop()
    
    # Extract resume text
    if resume_text.strip():
        final_resume_text = resume_text
    else:
        final_resume_text = extract_text_from_file(uploaded_file)
        if not final_resume_text:
            st.error("Could not extract text from the uploaded file. Please try pasting the resume text directly.")
            st.stop()
    
    # Run analysis
    with st.spinner("🧠 Analyzing with AI..."):
        job_analysis = parse_job_description(job_text)
        resume_analysis = parse_resume_intelligently(final_resume_text)
        match_results = intelligent_matching(resume_analysis, job_analysis)
        recommendations = generate_smart_recommendations(resume_analysis, job_analysis, match_results)
    
    # Display Results
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Overall score
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="score-big">{match_results.get('overall_match', 0)}%</div>
            <h4 style="margin: 0.5rem 0; color: #3a0ca3; font-size: 1.5rem; font-family: 'Montserrat', sans-serif;">Overall Match Score</h4>
            <p style="color: #4361ee; margin: 0; font-size: 1.2rem; font-family: 'Quicksand', sans-serif;">{match_results.get('explanation', 'Analysis complete')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div style="font-size: 2.2rem; font-weight: 700; color: #4361ee; font-family: 'Montserrat', sans-serif;">{match_results.get('semantic_score', 0)}%</div>
            <p style="margin: 0.8rem 0; color: #3a0ca3; font-size: 1.2rem; font-family: 'Quicksand', sans-serif;">Experience<br>Relevance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div style="font-size: 2.2rem; font-weight: 700; color: #4361ee; font-family: 'Montserrat', sans-serif;">{match_results.get('tech_score', 0)}%</div>
            <p style="margin: 0.8rem 0; color: #3a0ca3; font-size: 1.2rem; font-family: 'Quicksand', sans-serif;">Technical<br>Skills Match</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills Match Pie Chart
    st.markdown("### 📊 Skills Match Visualization")
    tech_matches = match_results.get('tech_matches', [])
    job_tech_keywords = match_results.get('job_tech_keywords', [])
    
    if tech_matches and job_tech_keywords:
        chart_html = create_skills_match_chart(tech_matches, job_tech_keywords)
        st.markdown(f"""
        <div class="chart-container">
            <div class="chart-title">Skills Match Analysis</div>
            {chart_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Not enough skill data to generate visualization.")
    
    # Recommendations sections
    st.markdown("### ✨ Optimized Resume Bullets")
    if recommendations.get('resume_bullets', []):
        for bullet in recommendations['resume_bullets']:
            st.markdown(f"""
            <div class="bullet-card">
                {bullet}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Upload a more detailed resume to get personalized bullet points.")
    
    # Two column layout for insights
    st.markdown("""
    <div class="two-column-container">
        <div>
            <h3>🎯 Interview Preparation</h3>
    """, unsafe_allow_html=True)
    
    for tip in recommendations.get('interview_prep', []):
        st.markdown(f"""
        <div style="font-size: 1.2rem; margin: 0.8rem 0; font-family: 'Quicksand', sans-serif;">
            • {tip}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div>
            <h3>🛠️ Skills to Highlight</h3>
    """, unsafe_allow_html=True)
    
    if tech_matches:
        st.markdown("<p style='font-size: 1.2rem; font-weight: 600; color: #3a0ca3; margin: 1rem 0 0.5rem 0;'>✓ Matched Skills:</p>", unsafe_allow_html=True)
        st.markdown("<div class='skills-container'>", unsafe_allow_html=True)
        for skill in tech_matches[:10]:
            st.markdown(f'<span class="tag-skill">{skill}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    missing_skills = set(job_tech_keywords) - set(tech_matches)
    if missing_skills and len(missing_skills) <= 8:
        st.markdown("<p style='font-size: 1.2rem; font-weight: 600; color: #3a0ca3; margin: 1.5rem 0 0.5rem 0;'>📚 Consider Learning:</p>", unsafe_allow_html=True)
        for skill in list(missing_skills)[:5]:
            st.markdown(f"""
            <div style="font-size: 1.2rem; margin: 0.5rem 0; font-family: 'Quicksand', sans-serif;">
                • {skill}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Application strategy
    if recommendations.get('application_strategy', []):
        st.markdown("### 🎯 Application Strategy")
        st.markdown(f"""
        <div class="insight-card">
            <strong style="font-size: 1.3rem; color: #3a0ca3;">Recommendation:</strong> 
            <p style="font-size: 1.2rem; margin-top: 0.5rem;">{recommendations['application_strategy'][0]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Download report
    resume_bullets = recommendations.get('resume_bullets', [])
    interview_prep = recommendations.get('interview_prep', [])
    tech_matches = match_results.get('tech_matches', [])
    application_strategy = recommendations.get('application_strategy', [])
    
    if resume_bullets:
        report_content = f"""RESUME OPTIMIZATION REPORT
Match Score: {match_results.get('overall_match', 0)}%
Analysis: {match_results.get('explanation', 'No analysis available')}

OPTIMIZED RESUME BULLETS:
{chr(10).join(resume_bullets)}

INTERVIEW PREPARATION:
{chr(10).join(['• ' + tip for tip in interview_prep])}

TECHNICAL SKILLS MATCHED:
{', '.join(tech_matches) if tech_matches else 'None identified'}

APPLICATION STRATEGY:
{application_strategy[0] if application_strategy else 'N/A'}
"""
        st.download_button(
            "📥 Download Analysis Report",
            report_content,
            file_name="resume_job_analysis.txt",
            mime="text/plain",
            use_container_width=True
        )





