# 📄 ResumeAnalyser  

ResumeAnalyser is a Streamlit-based web app that analyzes resumes against job descriptions, calculates ATS (Applicant Tracking System) scores, and provides personalized skill improvement suggestions along with recommended YouTube courses.  

---

## 🚀 Features  

- 📤 Upload your resume in PDF format.  
- 📝 Paste or type a job description.  
- 📊 ATS Score Calculation:
  - Matches resume keywords with job description.  
  - Calculates percentage match.  
  - Highlights missing skills.  
- 💡 Improved Recommendations:
  - Lists additional skills/courses to strengthen your profile.  
- 🎥 YouTube Course Recommendations:
  - Suggests curated courses for missing/required skills.  
- 🎨 Modern UI with custom theming and styling.  

---

## 🛠️ Installation  

Clone this repo:  

```bash
git clone https://github.com/your-username/ResumeAnalyser.git
cd ResumeAnalyser
Create a virtual environment (recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate    # On Mac/Linux
venv\Scripts\activate       # On Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
📦 Dependencies
Main libraries used:

streamlit → Web app framework

PyPDF2 → Extract text from resumes (PDFs)

scikit-learn → Keyword extraction & similarity matching

nltk → Natural Language Processing for text cleaning

pandas → Data handling

numpy → Numerical operations

(Ensure all are listed in requirements.txt)

▶️ Usage
Run the app with:

bash
Copy code
streamlit run app.py
Then open your browser at:
👉 http://localhost:8501

📊 How ATS Score is Calculated
Extracts text from the resume PDF.

Extracts text from the job description input.

Cleans and tokenizes both.

Compares overlap of skills/keywords.

Calculates match percentage:

mathematica
Copy code
ATS Score = (Number of Matched Keywords ÷ Total Job Keywords) × 100
Displays score, missing skills, and recommendations.

📂 Project Structure
bash
Copy code
ResumeAnalyser/
│── app.py                # Main Streamlit app
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── assets/               # (Optional) icons, images, CSS
📸 Screenshots
Job Matches
(Example UI screenshot here)

Recommended YouTube Courses
(Example UI screenshot here)

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

📜 License
This project is licensed under the MIT License.

yaml
Copy code

---

Do you want me to also **generate a ready `requirements.txt`** file for you (with exact packages and versions), so your project can run anywhere?







Ask ChatGPT
