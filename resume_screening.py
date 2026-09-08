import string

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from PyPDF2 import PdfReader


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        text += page.extract_text() or ""

    return text


# ============================================================
# NLP SETUP
# ============================================================

lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words("english"))


# ============================================================
# TEXT PREPROCESSING
# ============================================================

def preprocess_text(text):

    text = text.lower()

    tokens = word_tokenize(text)

    tokens = [
        word for word in tokens
        if word not in stop_words
    ]

    tokens = [
        word for word in tokens
        if word not in string.punctuation
    ]

    tokens = [
        lemmatizer.lemmatize(word)
        for word in tokens
    ]

    return " ".join(tokens)


# ============================================================
# TF-IDF SCORE
# ============================================================

def calculate_tfidf_score(job_description, resumes):

    clean_job_description = preprocess_text(job_description)

    clean_resumes = []

    for resume in resumes:

        clean_resume = preprocess_text(resume)

        clean_resumes.append(clean_resume)


    # Put job description first
    documents = [clean_job_description] + clean_resumes


    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)


    scores = []


    # Compare job description with every resume
    for i in range(1, len(resumes) + 1):

        similarity = cosine_similarity(
            tfidf_matrix[0],
            tfidf_matrix[i]
        )

        match_score = similarity[0][0] * 100

        scores.append(match_score)


    return scores


# ============================================================
# SKILL DATABASE
# ============================================================

skill_database = [

    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "html",
    "css",
    "react",
    "node.js",
    "flask",
    "django",

    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",

    "git",
    "github",
    "docker",
    "aws",
    "azure",

    "data structures",
    "algorithms",
    "oop",
    "rest api"

]


# ============================================================
# SKILL ALIASES
# ============================================================

skill_aliases = {

    "ml": "machine learning",

    "ai": "artificial intelligence",

    "nlp": "nlp",

    "js": "javascript",

    "reactjs": "react",

    "nodejs": "node.js",

    "sklearn": "scikit-learn",

    "postgres": "postgresql",

    "mongo": "mongodb",

    "ds": "data structures"

}


# ============================================================
# EXTRACT REQUIRED SKILLS FROM JOB DESCRIPTION
# ============================================================

def extract_required_skills(job_description):

    text = job_description.lower()

    required_skills = []


    for skill in skill_database:

        if skill in text:

            required_skills.append(skill)


    # Check aliases
    for alias, actual_skill in skill_aliases.items():

        if alias in text and actual_skill not in required_skills:

            required_skills.append(actual_skill)


    return required_skills


# ============================================================
# MATCH RESUME SKILLS
# ============================================================

def match_resume_skills(resumes, required_skills):

    results = []


    for resume in resumes:

        resume_text = resume.lower()

        matched_skills = []

        missing_skills = []


        for skill in required_skills:

            if skill in resume_text:

                matched_skills.append(skill)

            else:

                missing_skills.append(skill)


        # Calculate skill match percentage
        if len(required_skills) > 0:

            skill_score = (
                len(matched_skills)
                / len(required_skills)
            ) * 100

        else:

            skill_score = 0


        results.append(
            (
                skill_score,
                matched_skills,
                missing_skills
            )
        )


    return results


# ============================================================
# CALCULATE FINAL SCORE
# ============================================================

def calculate_final_scores(tfidf_scores, skill_results):

    final_results = []


    for i in range(len(tfidf_scores)):

        tfidf_score = tfidf_scores[i]

        skill_score = skill_results[i][0]

        matched_skills = skill_results[i][1]

        missing_skills = skill_results[i][2]


        # TF-IDF = 40%
        # Skill Matching = 60%

        final_score = (
            (tfidf_score * 0.40)
            +
            (skill_score * 0.60)
        )


        final_results.append(
            (
                i + 1,
                tfidf_score,
                skill_score,
                final_score,
                matched_skills,
                missing_skills
            )
        )


    return final_results


# ============================================================
# RANK RESUMES
# ============================================================

def rank_resumes(final_results):

    final_results.sort(
        key=lambda x: x[3],
        reverse=True
    )


    return final_results



def get_match_status(final_score):

    if final_score >= 90:
        return "Excellent Match"

    elif final_score >= 75:
        return "Strong Match"

    elif final_score >= 60:
        return "Good Match"

    elif final_score >= 40:
        return "Moderate Match"

    else:
        return "Low Match"