# Smart-Resume-and-Job-Analyser
# 🎯 Smart Resume × Job Matcher

> An intelligent resume analyzer that uses AI to match your resume with job descriptions, providing contextual insights beyond simple keyword matching.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)


## ✨ Features

🔍 **Smart Semantic Analysis**
- Uses sentence transformers for contextual understanding
- Goes beyond keyword matching to understand actual experience relevance

🎯 **Intelligent Skill Matching**
- Recognizes synonyms and related technologies
- Fuzzy matching for technical terms
- Domain-specific skill categorization

📊 **Visual Analytics**
- Interactive skill match visualization
- Comprehensive scoring breakdown
- Beautiful, modern UI with professional styling

💡 **Actionable Recommendations**
- Optimized resume bullet points
- Interview preparation tips
- Skill development suggestions
- Application strategy advice

📄 **Multi-format Support**
- PDF, DOCX, and TXT file uploads
- Direct text paste functionality
- Robust text extraction

## 🚀 Getting Started

You can just test the app by using this link :
OR proceed as below : 

### Prerequisites

Make sure you have Python 3.8+ installed on your system.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-resume-analyzer.git
   cd smart-resume-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required NLTK and spaCy models**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   python -m spacy download en_core_web_sm
   ```

### Usage

1. **Run the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload your resume** (PDF, DOCX, or TXT) or paste the text directly

4. **Paste the job description** you want to match against

5. **Click "Analyze Match"** and get your personalized insights! 🎉

## 🛠️ Technology Stack

- **Streamlit** - Web application framework
- **Sentence Transformers** - Semantic text analysis
- **scikit-learn** - Cosine similarity calculations
- **spaCy & NLTK** - Natural language processing
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing
- **Matplotlib** - Data visualization

## 📁 Project Structure

```
smart-resume-analyzer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation

```

## 🎨 Key Features Explained

### Semantic Matching
The app uses advanced NLP models to understand the context and meaning of your experience, not just matching keywords. This provides more accurate assessments of how well your background aligns with job requirements.

### Skill Synonym Recognition
Built-in knowledge of technical term synonyms (e.g., "JS" = "JavaScript", "ML" = "Machine Learning") ensures no relevant skills are missed.

### Domain Intelligence
Recognizes different industries and adjusts scoring based on domain-specific requirements and terminology.

### Fuzzy Matching
Handles variations in spelling and terminology to ensure comprehensive skill detection.

## 📊 Scoring System

- **Overall Match Score**: Weighted combination of semantic alignment and technical skill overlap
- **Experience Relevance**: How well your experience aligns with job responsibilities
- **Technical Skills Match**: Percentage of required technical skills you possess



## 📝 Requirements

Create a `requirements.txt` file with:

```txt
streamlit==1.19.0
sentence-transformers==2.2.2
scikit-learn
PyPDF2
python-docx
nltk
spacy
openai
matplotlib
numpy
pandas

## 🔧 Troubleshooting

**Model Loading Issues**
- Ensure you have sufficient disk space for the sentence transformer models
- Check your internet connection during first run

**File Upload Problems**
- Verify file format (PDF, DOCX, TXT only)
- Check file size limits
- Try pasting text directly if upload fails

**SpaCy Model Missing**
```bash
python -m spacy download en_core_web_sm
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Sentence Transformers library for semantic analysis capabilities
- Streamlit team for the amazing web framework
- Open source NLP community for tools and models

## 📬 Contact

Have questions or suggestions? Feel free to reach out!

⭐ **If this project helped you, please give it a star!** ⭐

*Built with 💜 for job seekers everywhere*
