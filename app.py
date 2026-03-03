import streamlit as st
import re
import PyPDF2

st.set_page_config(page_title="ATS Resume Matcher", layout="centered")
st.title("📊 ATS Resume Matching System")

# -----------------------------
# FUNCTION TO READ PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


# -----------------------------
# INPUT SECTION
# -----------------------------

st.subheader("📄 Job Description Input")

jd_option = st.radio("Choose JD Input Method:", ["Paste Text", "Upload PDF"])

if jd_option == "Paste Text":
    jd_text = st.text_area("Paste Job Description Here")
else:
    jd_file = st.file_uploader("Upload JD PDF", type=["pdf"])
    if jd_file:
        jd_text = extract_text_from_pdf(jd_file)
    else:
        jd_text = ""


st.subheader("📑 Resume Input")

resume_option = st.radio("Choose Resume Input Method:", ["Paste Text", "Upload PDF"])

if resume_option == "Paste Text":
    resume_text = st.text_area("Paste Resume Text Here")
else:
    resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
    if resume_file:
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = ""


# -----------------------------
# CALCULATION BUTTON
# -----------------------------

if st.button("Calculate ATS Score"):

    if jd_text.strip() == "" or resume_text.strip() == "":
        st.warning("Please provide both Job Description and Resume.")
    else:

        jd_text = jd_text.lower()
        resume_text = resume_text.lower()

        # -----------------------------
        # DATABASES
        # -----------------------------

        skills_db = [
            "python", "sql", "excel", "power bi",
            "tableau", "statistics", "r",
            "machine learning", "data science",
            "aiml"
        ]

        education_db = [
            "bachelor", "bachelor’s", "bachelors",
            "bsc", "b.sc",
            "btech", "b.tech",
            "be", "b.e",
            "mtech", "m.tech",
            "msc", "m.sc",
            "computer science", "cse",
            "engineering"
        ]

        other_db = [
            "communication", "analytical",
            "problem solving", "teamwork",
            "leadership"
        ]

        final_score = 0
        total_weight = 0

        # -----------------------------
        # 1️⃣ SKILLS (50%)
        # -----------------------------
        jd_skills = [s for s in skills_db if s in jd_text]
        resume_skills = [s for s in skills_db if s in resume_text]
        matched_skills = list(set(jd_skills) & set(resume_skills))

        skill_score = len(matched_skills) / len(jd_skills) if jd_skills else 0

        final_score += 0.5 * skill_score
        total_weight += 0.5

        # -----------------------------
        # 2️⃣ EDUCATION (20%)
        # -----------------------------
        jd_edu = [e for e in education_db if e in jd_text]

        if jd_edu:
            resume_edu = [e for e in education_db if e in resume_text]
            matched_edu = list(set(jd_edu) & set(resume_edu))
            edu_score = len(matched_edu) / len(jd_edu)

            final_score += 0.2 * edu_score
            total_weight += 0.2
        else:
            edu_score = None

        # -----------------------------
        # 3️⃣ EXPERIENCE (20%)
        # -----------------------------
        jd_exp_match = re.search(r'(\d+)\+?\s*years?', jd_text)

        if jd_exp_match:
            jd_years = int(jd_exp_match.group(1))
            resume_exp_match = re.search(r'(\d+)\+?\s*years?', resume_text)
            resume_years = int(resume_exp_match.group(1)) if resume_exp_match else 0

            exp_score = 1 if resume_years >= jd_years else resume_years / jd_years

            final_score += 0.2 * exp_score
            total_weight += 0.2
        else:
            exp_score = None

        # -----------------------------
        # 4️⃣ OTHER (10%)
        # -----------------------------
        jd_other = [o for o in other_db if o in jd_text]

        if jd_other:
            resume_other = [o for o in other_db if o in resume_text]
            matched_other = list(set(jd_other) & set(resume_other))
            other_score = len(matched_other) / len(jd_other)

            final_score += 0.1 * other_score
            total_weight += 0.1
        else:
            other_score = None

        # -----------------------------
        # NORMALIZE SCORE
        # -----------------------------
        final_percentage = round((final_score / total_weight) * 100, 2)

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------
        st.subheader("📋 Matching Report")

        st.write("### 🔹 Matched Skills:", matched_skills)
        st.write("### 🔹 Skill Match:", round(skill_score * 100, 2), "%")

        if edu_score is not None:
            st.write("### 🎓 Education Match:", round(edu_score * 100, 2), "%")
        else:
            st.write("### 🎓 Education: Not Required in JD")

        if exp_score is not None:
            st.write("### 💼 Experience Match:", round(exp_score * 100, 2), "%")
        else:
            st.write("### 💼 Experience: Not Required in JD")

        st.success(f"🔥 Final ATS Score: {final_percentage}%")
