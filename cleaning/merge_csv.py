"""
merge_csv.py  —  Run this ONCE from your project root:
    python merge_csv.py

It reads all 4 course CSV files, normalizes their columns,
and writes a single clean  data/courses.csv  for Flask to use.
"""

import pandas as pd
import os

# ─── STEP 1: Configure your files here ───────────────────────────────────────
# For each file, specify:
#   "file"     : path to the CSV
#   "platform" : platform name to tag each row with
#   "rename"   : map YOUR column names → standard names
#
# Standard column names used by Flask app:
#   course_name     — title of the course
#   description     — what the course covers
#   skills_covered  — comma-separated skills (used for TF-IDF matching)
#   platform        — Coursera / Udemy / YouTube / etc.
#   url             — link to the course (can be empty)

FILES = [
    {
        "file": "data/cleaned_data/coursera1_tech_cleaned.csv",
        "platform": "Coursera",
        "rename": {
            # "your column name" : "standard name"
            "Course Name"        : "course_name",
            "Course Description"  : "description",
            "Skills"       : "skills_covered",
            "Course URL"   : "url"
        }
    },
    {
        "file": "data/cleaned_data/coursera2_tech_cleaned.csv",
        "platform": "Coursera",
        "rename": {
            "Title"  : "course_name",   # already correct, keep it
            # "topic"        : "description",
            "Skills": "skills_covered",
            # "url"          : "url",
        }
    },
    {
        "file": "data/cleaned_data/coursera3_tech_cleaned.csv",
        "platform": "Coursera",
        "rename": {
            "Title"         : "course_name",
            "course_description"     : "description",
            "Skills"         : "skills_covered",
            # no url column in this file — it will be filled with empty string
        }
    },
    {
        "file": "data/cleaned_data/udemy1_tech_cleaned.csv",
        "platform": "Udemy",
        "rename": {
            # fill in your actual column names here
            "course_title"        : "course_name",
            # "subject"        : "description",
            "subject"     : "skills_covered",
             "url"          : "url",
        }
    },
]

# ─── STEP 2: Columns we want in the final output ──────────────────────────────
FINAL_COLUMNS = ["course_name", "description", "skills_covered", "platform", "url"]


# ─── STEP 3: Merge logic (no need to edit below this line) ───────────────────

def load_and_normalize(config: dict) -> pd.DataFrame:
    filepath = config["file"]
    platform = config["platform"]
    rename_map = config["rename"]

    if not os.path.exists(filepath):
        print(f"  [SKIP] File not found: {filepath}")
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    print(f"  [OK]   Loaded {filepath}  —  {len(df)} rows, columns: {list(df.columns)}")

    # Rename columns to standard names
    df = df.rename(columns=rename_map)

    # Add platform column
    df["platform"] = platform

    # Keep only the columns we need (ignore extras)
    existing = [c for c in FINAL_COLUMNS if c in df.columns]
    df = df[existing]

    # Add any missing standard columns as empty strings
    for col in FINAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[FINAL_COLUMNS]


def merge_all():
    print("\n── UpTrail CSV Merger ────────────────────────────────────")
    frames = []

    for config in FILES:
        df = load_and_normalize(config)
        if not df.empty:
            frames.append(df)

    if not frames:
        print("\n[ERROR] No files were loaded. Check your file paths in FILES config.")
        return

    merged = pd.concat(frames, ignore_index=True)

    # Clean up
    merged = merged.drop_duplicates(subset=["course_name"])   # remove duplicate courses
    merged = merged.dropna(subset=["course_name"])             # drop rows with no title
    merged["course_name"]    = merged["course_name"].str.strip()
    merged["skills_covered"] = merged["skills_covered"].fillna("").str.strip()
    merged["description"]    = merged["description"].fillna("").str.strip()
    merged["url"]            = merged["url"].fillna("").str.strip()

    # Save
    os.makedirs("data", exist_ok=True)
    out_path = "data/courses.csv"
    merged.to_csv(out_path, index=False)

    print(f"\n[DONE] Merged {len(merged)} courses → {out_path}")
    print(f"       Columns: {list(merged.columns)}")
    print(f"\nSample:\n{merged.head(3).to_string()}\n")


if __name__ == "__main__":
    merge_all()
