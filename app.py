from flask import Flask, render_template, request
import os
import tempfile

from resume_screening import (
    extract_text_from_pdf,
    calculate_tfidf_score,
    extract_required_skills,
    match_resume_skills,
    calculate_final_scores,
    rank_resumes,
    get_match_status
)


app = Flask(__name__)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/screen", methods=["POST"])
def screen():

    # -----------------------------------------
    # Get Job Description
    # -----------------------------------------

    job_description = request.form["job_description"]


    # -----------------------------------------
    # Get Uploaded Resumes
    # -----------------------------------------

    uploaded_resumes = request.files.getlist("resumes")

    print("\n==============================")
    print("NUMBER OF UPLOADED RESUMES:", len(uploaded_resumes))
    print("==============================")

    for resume in uploaded_resumes:
        print("UPLOADED FILE:", resume.filename)
    
    resumes = []
    filenames = []


    # -----------------------------------------
    # Process Every Resume
    # -----------------------------------------

    for resume in uploaded_resumes:

        if resume.filename == "":
            continue

        if not resume.filename.lower().endswith(".pdf"):
            continue


        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_path = temp_file.name


        # Save uploaded PDF
        resume.save(temp_path)


        try:

            # Extract text from PDF
            text = extract_text_from_pdf(temp_path)

        except Exception as e:

            print("ERROR READING PDF:", resume.filename)
            print(e)

            text = ""

        finally:

            # Delete temporary PDF
            if os.path.exists(temp_path):
                os.remove(temp_path)


        # -----------------------------------------
        # DEBUG INFORMATION
        # -----------------------------------------

        print("\n==============================")
        print("RESUME:", resume.filename)
        print("==============================")

        print("EXTRACTED TEXT LENGTH:", len(text))

        print("EXTRACTED TEXT:")
        print(text[:1000])


        # Store resume information
        resumes.append(text)

        filenames.append(resume.filename)


        if not text.strip():

            print("WARNING: No text extracted from:", resume.filename)

            continue

    # -----------------------------------------
    # Check Resume Upload
    # -----------------------------------------

    if len(resumes) == 0:

        return "Please upload at least one PDF resume."


    # -----------------------------------------
    # TF-IDF SCORE
    # -----------------------------------------

    tfidf_scores = calculate_tfidf_score(
        job_description,
        resumes
    )


    # -----------------------------------------
    # REQUIRED SKILLS
    # -----------------------------------------

    required_skills = extract_required_skills(
        job_description
    )


    # -----------------------------------------
    # SKILL MATCHING
    # -----------------------------------------

    skill_results = match_resume_skills(
        resumes,
        required_skills
    )


    # -----------------------------------------
    # FINAL SCORE
    # -----------------------------------------

    final_results = calculate_final_scores(
        tfidf_scores,
        skill_results
    )


    # -----------------------------------------
    # RANK RESUMES
    # -----------------------------------------

    ranked_results = rank_resumes(
        final_results
    )


    # -----------------------------------------
    # Prepare Results
    # -----------------------------------------

    results = []


    for result in ranked_results:

        resume_number = result[0]

        tfidf_score = result[1]

        skill_score = result[2]

        final_score = result[3]

        matched_skills = result[4]

        missing_skills = result[5]


        filename = filenames[resume_number - 1]

        status = get_match_status(final_score)

        results.append({
            "filename": filename,
            "tfidf_score": tfidf_score,
            "skill_score": skill_score,
            "final_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "status": status,
        })


    # -----------------------------------------
    # Best Candidate
    # -----------------------------------------

    best_candidate = results[0]


    # -----------------------------------------
    # Send Results to HTML
    # -----------------------------------------

    return render_template(

        "result.html",

        results=results,

        best_candidate=best_candidate,

        required_skills=required_skills

    )


if __name__ == "__main__":

    app.run(debug=True)
