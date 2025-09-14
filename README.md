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
  - <img width="1747" height="680" alt="image" src="https://github.com/user-attachments/assets/338da361-7bbd-47f7-8635-05514b985543" />
  

- 💡 Improved Recommendations:
  - Lists additional skills/courses to strengthen your profile.  
- 🎥 YouTube Course Recommendations:
  - Suggests curated courses for missing/required skills.  
- 🎨 Modern UI with custom theming and styling.  

---

## 🛠️ Installation  

Clone this repo:  


git clone https://github.com/your-username/ResumeAnalyser.git
cd ResumeAnalyser
Create a virtual environment (recommended):



python -m venv venv
source venv/bin/activate    # On Mac/Linux
venv\Scripts\activate       # On Windows
Install dependencies:



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


streamlit run app.py
Then open your browser at:
👉 http://localhost:8501

📊 How ATS Score is Calculated
Extracts text from the resume PDF.

Extracts text from the job description input.

Cleans and tokenizes both.

Compares overlap of skills/keywords.

Calculates match percentage:


Copy code
ATS Score = (Number of Matched Keywords ÷ Total Job Keywords) × 100
Displays score, missing skills, and recommendations.

📂 Project Structure

ResumeAnalyser/
│── app.py                # Main Streamlit app
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
│── assets/               # (Optional) icons, images, CSS
📸 Screenshots

Job Matches
<img width="1745" height="631" alt="image" src="https://github.com/user-attachments/assets/14a6e580-fcc3-4b88-ab47-e5bec422ab2b" />

Recommended YouTube Courses
<img width="862" height="382" alt="image" src="https://github.com/user-attachments/assets/accc7d07-e680-4685-8430-9a9f4235c73b" />


🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

📜 License
This project is licensed under the MIT License.
















