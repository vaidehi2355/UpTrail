
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import json
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import google.generativeai as genai
import pdfplumber

load_dotenv(dotenv_path=".env")
# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-flash-latest")


import google.generativeai as genai

# ─── App Setup ───────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "uptrail_secret_key_change_in_production"

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"pdf" , "png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Data Loaders ─────────────────────────────────────────────────────────────

def load_skills_data():
    """Load skills JSON — returns dict of {domain: [skill, ...]}"""
    path = os.path.join("data", "cleaned_data", "tech_skills_datasetupdated.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def load_courses():
    """Load merged courses CSV. Columns: course_name, description, skills_covered, platform, url"""
    path = os.path.join("data", "cleaned_data", "courses.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def load_roles():
    """Load roles from Excel. Columns: Role Name, Required Skills"""
    path = os.path.join("data", "cleaned_data", "tech_roles_dataset.xlsx")
    return pd.read_excel(path) if os.path.exists(path) else pd.DataFrame()


def load_internships():
    """Load internships CSV. Columns: title, company, role, skills, link"""
    path = os.path.join("data", "cleaned_data", "internships.csv")
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_matching_courses(missing_skills: list, top_n: int = 10) -> list:
    """TF-IDF + cosine similarity to rank courses by relevance to missing skills."""
    courses_df = load_courses()
    if courses_df.empty or not missing_skills:
        return []

    # Convert skills_covered to string and handle NaN properly
    courses_df = courses_df.copy()
    courses_df["skills_covered"] = courses_df["skills_covered"].apply(
        lambda x: "" if (isinstance(x, float) and pd.isna(x)) else str(x)
    )

    query             = " ".join(missing_skills)
    corpus            = courses_df["skills_covered"].tolist()
    corpus_with_query = corpus + [query]

    vectorizer   = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus_with_query)

    query_vec   = tfidf_matrix[-1]
    course_vecs = tfidf_matrix[:-1]
    scores      = cosine_similarity(query_vec, course_vecs).flatten()

    courses_df["similarity"] = scores
    top_courses = (
        courses_df.sort_values("similarity", ascending=False)
        .head(top_n)
        .to_dict(orient="records")
    )
    return top_courses


def get_matched_roles(user_skills: list) -> list:
    """Compare user skills against each role. Returns roles sorted by match %."""
    roles_df = load_roles()
    if roles_df.empty:
        return []

    results  = []
    user_set = set(s.lower().strip() for s in user_skills)

    for _, row in roles_df.iterrows():
        required     = [s.strip().lower() for s in str(row["Required Skills"]).split(",")]
        required_set = set(required)
        matched      = user_set & required_set
        match_pct    = round(len(matched) / len(required_set) * 100) if required_set else 0

        results.append({
            "role_name":       row["Role Name"],
            "description":     row.get("Description", ""),
            "required_skills": required,
            "matched_skills":  list(matched),
            "missing_skills":  list(required_set - user_set),
            "match_pct":       match_pct,
            "total_required":  len(required_set),
        })

    results.sort(key=lambda x: x["match_pct"], reverse=True)
    return results


def analyze_readiness(user_skills: list, role_name: str) -> dict:
    """Returns internship readiness analysis for a specific role."""
    roles_df = load_roles()
    if roles_df.empty:
        return {}

    role_row = roles_df[roles_df["Role Name"].str.lower() == role_name.lower()]
    if role_row.empty:
        return {}

    required     = [s.strip().lower() for s in str(role_row.iloc[0]["Required Skills"]).split(",")]
    user_set     = set(s.lower().strip() for s in user_skills)
    required_set = set(required)

    completed      = list(user_set & required_set)
    missing        = list(required_set - user_set)
    completion_pct = round(len(completed) / len(required_set) * 100) if required_set else 0

    return {
        "role":           role_name,
        "total_required": len(required_set),
        "completed":      completed,
        "missing":        missing,
        "completion_pct": completion_pct,
        "is_ready":       completion_pct >= 85,
    }


# ─── Auth Guard ───────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated




from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# ─── Routes ───────────────────────────────────────────────────────────────────

# Dashboard
# @app.route("/dashboard")
# @login_required
# def dashboard():
#     user_skills = session.get("user_skills", [])
#     role_name   = session.get("selected_role", "")
#     readiness   = analyze_readiness(user_skills, role_name) if role_name else {}
#     top_courses = get_matching_courses(readiness.get("missing", user_skills), top_n=5)

#     internships_df  = load_internships()
#     courses_df      = load_courses()
#     internship_count = len(internships_df) if not internships_df.empty else 0
#     course_count     = len(courses_df)     if not courses_df.empty     else 0

#     activities = [
#         {"label": "Skills submitted", "done": bool(user_skills)},
#         {"label": "Role selected",    "done": bool(role_name)},
#         {"label": "Analysis viewed",  "done": bool(role_name)},
#         {"label": "Courses reviewed", "done": False},
#     ]

#     return render_template(
#         "dashboard.html",
#         user_skills      = user_skills,
#         role             = role_name,
#         readiness        = readiness,
#         top_courses      = top_courses,
#         internship_count = internship_count,
#         course_count     = course_count,
#         activities       = activities,
#     )


# 1. Login / Sign-up
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        action   = request.form.get("action")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if action == "signup":
            session["user"] = username
            flash(f"Welcome, {username}! Your account has been created.", "success")
            return redirect(url_for("home"))

        elif action == "login":
            if username and password:
                session["user"] = username
                flash(f"Welcome back, {username}!", "success")
                return redirect(url_for("home"))
            else:
                flash("Please enter valid credentials.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# 2. Home — Skills Input
@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    skills_data = load_skills_data()
    roles_df    = load_roles()
    roles_list  = roles_df["Role Name"].tolist() if not roles_df.empty else []

    if request.method == "POST":
        selected_skills          = request.form.getlist("skills")
        session["user_skills"]   = list(set(selected_skills))
        session["selected_role"] = request.form.get("role", "")
        return redirect(url_for("roles"))

    return render_template(
        "home.html",
        skills_data   = skills_data,
        all_skills    = [s for skills in skills_data.values() for s in skills],
        user_skills   = session.get("user_skills", []),
        roles         = roles_list,
        selected_role = session.get("selected_role", ""),
    )


# 3. Roles Page
@app.route("/roles")
@login_required
def roles():
    user_skills  = session.get("user_skills", [])
    explore_mode = request.args.get("explore") == "1"

    if explore_mode:
        session["user_skills"] = []

    matched_roles = get_matched_roles(user_skills)

    return render_template(
        "roles.html",
        roles        = matched_roles,
        user_skills  = user_skills,
        explore_mode = explore_mode,
    )


@app.route("/roles/select/<role_name>")
@login_required
def select_role(role_name):
    session["selected_role"] = role_name
    return redirect(url_for("analysis"))


# 4. Analysis Page
@app.route("/analysis")
@login_required
def analysis():
    user_skills = session.get("user_skills", [])
    role_name   = session.get("selected_role", "")

    if not role_name:
        flash("Please select a role first.", "warning")
        return redirect(url_for("roles"))

    readiness   = analyze_readiness(user_skills, role_name)
    top_courses = get_matching_courses(readiness.get("missing", []), top_n=6)

    return render_template(
        "analysis.html",
        readiness   = readiness,
        top_courses = top_courses,
        role        = role_name,
    )


# 5. Courses Page
@app.route("/courses")
@login_required
def courses():
    user_skills    = session.get("user_skills", [])
    role_name      = session.get("selected_role", "")
    readiness      = analyze_readiness(user_skills, role_name) if role_name else {}
    missing_skills = readiness.get("missing", user_skills)

    # Ensure missing_skills is a list of strings (not floats or other types)
    if isinstance(missing_skills, list):
        missing_skills = [str(s) for s in missing_skills if s is not None and not isinstance(s, float)]
    else:
        missing_skills = []

    # If role and skills are selected, show personalized courses; otherwise show all courses
    if role_name and missing_skills:
        all_courses = get_matching_courses(missing_skills, top_n=20)
    else:
        # Show all courses when no role/skills selected
        courses_df = load_courses()
        if not courses_df.empty:
            # Sort by platform for proper groupby in template
            courses_df = courses_df.sort_values(by='platform', na_position='last')
            all_courses = courses_df.to_dict(orient="records")
        else:
            all_courses = []

    # Preprocess all fields to handle NaN/float values
    for course in all_courses:
        # Handle skills_covered
        skills = course.get("skills_covered", "")
        if isinstance(skills, float) or (isinstance(skills, str) and skills.lower() in ("nan", "none", "")):
            course["skills_list"] = []
            course["skills_covered"] = ""
        else:
            raw_skills = str(skills).split(",")
            course["skills_list"] = [s.strip() for s in raw_skills if isinstance(s, str)]

        # Handle description - ensure it's always a string
        desc = course.get("description", "")
        if isinstance(desc, float) or (isinstance(desc, str) and desc.lower() in ("nan", "none", "")):
            course["description"] = ""
        else:
            course["description"] = str(desc)

    return render_template(
        "courses.html",
        courses        = all_courses,
        role           = role_name,
        missing_skills = missing_skills,
    )


# 6. Internship Page
@app.route("/internship")
@login_required
def internship():
    role_name      = session.get("selected_role", "")
    user_skills    = session.get("user_skills", [])
    user_skills_lower = [s.lower().strip() for s in user_skills]  # For case-insensitive comparison
    internships_df = load_internships()
    internships    = []

    if not internships_df.empty:
        if role_name:
            # Filter by selected role
            filtered    = internships_df[
                internships_df["role"].str.lower().str.contains(role_name.lower(), na=False)
            ]
            internships = filtered.to_dict(orient="records")
        else:
            # No role selected — show all internships
            internships = internships_df.to_dict(orient="records")

        # Preprocess skills field to handle NaN/None values
        for intern in internships:
            skills = intern.get("skills", "")
            if isinstance(skills, float) or (isinstance(skills, str) and skills.lower() in ("nan", "none", "")):
                intern["skills"] = ""
            else:
                intern["skills"] = str(skills)


    activities = session.get("activities", [
        {"label": "Skills submitted", "done": bool(user_skills)},
        {"label": "Role selected",    "done": bool(role_name)},
        {"label": "Analysis viewed",  "done": bool(role_name)},
        {"label": "Courses reviewed", "done": False},
    ])

    return render_template(
        "internship.html",
        internships      = internships,
        role             = role_name,
        activities       = activities,
        user_skills      = user_skills,
        user_skills_lower = user_skills_lower,
    )

# 6. Internship Page
# @app.route("/internship")
# @login_required
# def internship():
#     role_name   = session.get("selected_role", "")
#     user_skills = session.get("user_skills", [])

#     internships_df = load_internships()
#     internships    = []

#     if not internships_df.empty:
#         if role_name:
#             # Try matching role against title column
#             filtered = internships_df[
#                 internships_df["role"].str.lower().str.contains(
#                     role_name.lower(), na=False
#                 )
#             ]
#             # If no matches found, show all internships
#             if filtered.empty:
#                 filtered = internships_df
#                 flash(f"No exact matches for '{role_name}' — showing all internships.", "info")
#         else:
#             # No role selected — show everything
#             filtered = internships_df

#         internships = filtered.to_dict(orient="records")

#     activities = session.get("activities", [
#         {"label": "Skills submitted", "done": bool(user_skills)},
#         {"label": "Role selected",    "done": bool(role_name)},
#         {"label": "Analysis viewed",  "done": bool(role_name)},
#         {"label": "Courses reviewed", "done": False},
#     ])

#     return render_template(
#         "internship.html",
#         internships = internships,
#         role        = role_name,
#         activities  = activities,
#         user_skills = user_skills,
#     )

@app.route('/auth/google/login')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    print("Redirect URI:", redirect_uri)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token['userinfo']

    # Store user in session
    session["user"] = user_info["email"]

    flash("Logged in with Google!", "success")
    return redirect(url_for("home"))


# ─── Resume Helpers ───────────────────────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extract all text from a PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[PDF ERROR] {e}")
    return text.strip()


def analyse_resume_with_gemini(resume_text: str, role_name: str, required_skills: list) -> dict:
    """
    Send resume text to Gemini and get structured analysis back.
    Returns a dict with score, summary, strengths, improvements, suggestions,
    skills_found, skills_matched, skills_missing.
    """
    skills_str = ", ".join(required_skills) if required_skills else "general tech skills"

    prompt = f"""
You are an expert resume reviewer helping a student land a {role_name} internship.

Analyse the resume below and return ONLY a valid JSON object with exactly these keys:
{{
  "score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
  "suggestions": ["<actionable suggestion 1>", "<actionable suggestion 2>"],
  "skills_found": ["<skill found in resume 1>", "<skill found in resume 2>", ...]
}}

Rules:
- score should reflect how well this resume fits a {role_name} internship
- strengths: what the candidate does well
- improvements: specific things to fix or add
- suggestions: actionable next steps tailored to {role_name}
- skills_found: list ONLY skills you can actually see mentioned in the resume

Required skills for {role_name}: {skills_str}

Resume:
\"\"\"
{resume_text[:4000]}
\"\"\"

Return ONLY the JSON object, no markdown, no explanation.
"""

    try:
        response = gemini_model.generate_content(prompt)
        raw      = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        # Compute skill match from skills_found vs required_skills
        found_lower    = [s.lower().strip() for s in data.get("skills_found", [])]
        required_lower = [s.lower().strip() for s in required_skills]

        skills_matched = [s for s in required_skills if s.lower().strip() in found_lower]
        skills_missing = [s for s in required_skills if s.lower().strip() not in found_lower]

        return {
            "score":          data.get("score"),
            "summary":        data.get("summary", ""),
            "strengths":      data.get("strengths", []),
            "improvements":   data.get("improvements", []),
            "suggestions":    data.get("suggestions", []),
            "skills_found":   data.get("skills_found", []),
            "skills_matched": skills_matched,
            "skills_missing": skills_missing,
        }

    except json.JSONDecodeError:
        return _fallback_result("Gemini returned an unexpected response format. Please try again.")
    except Exception as e:
        return _fallback_result(f"Gemini error: {str(e)}")
    # except Exception as e:
    #     print("Gemini error:", e)
    #     return "Error analyzing resume. Please try again."

def _fallback_result(message: str) -> dict:
    return {
        "score":          None,
        "summary":        message,
        "strengths":      [],
        "improvements":   [],
        "suggestions":    [],
        "skills_found":   [],
        "skills_matched": [],
        "skills_missing": [],
    }

 

# 7. Resume Analyser
@app.route("/resume-analyser", methods=["GET", "POST"])
@login_required
def resume_analyser():
    analysis_result = None
    roles_df        = load_roles()
    roles_list      = roles_df["Role Name"].tolist() if not roles_df.empty else []

    if request.method == "POST":
        resume_file   = request.files.get("resume")
        role_override = request.form.get("role_override", "")
        role_name     = role_override or session.get("selected_role", "")

        if not resume_file or not allowed_file(resume_file.filename):
            flash("Please upload a PDF, PNG, or JPG file.", "danger")
        else:
            filename  = secure_filename(resume_file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            resume_file.save(save_path)

            # Extract text (PDF only — images need OCR, skip for now)
            if filename.lower().endswith(".pdf"):
                resume_text = extract_text_from_pdf(save_path)
            else:
                resume_text = ""

            if not resume_text:
                flash("Could not extract text from your file. Please upload a text-based PDF.", "warning")
                resume_text = "(No text extracted)"

            # Get required skills for the selected role
            required_skills = []
            if role_name and not roles_df.empty:
                role_row = roles_df[roles_df["Role Name"].str.lower() == role_name.lower()]
                if not role_row.empty:
                    required_skills = [
                        s.strip() for s in
                        str(role_row.iloc[0]["Required Skills"]).split(",")
                    ]

            # Call Gemini
            result = analyse_resume_with_gemini(resume_text, role_name, required_skills)
            result["filename"] = filename
            result["role"]     = role_name
            analysis_result    = result

    return render_template(
        "resume_analyser.html",
        result = analysis_result,
        roles  = roles_list,
    )





# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run()
