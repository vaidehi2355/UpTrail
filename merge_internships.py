"""
merge_internships.py — Run once from your project root:
    python merge_internships.py

Merges postings.csv and internshala.csv into data/internships.csv
"""

import pandas as pd
import os

# ─── Standard columns used by Flask app ──────────────────────────────────────
# title, company, location, role, skills, link, duration, stipend, mode, source

def load_postings():
    path = os.path.join("data", "raw", "/Users/vaidehijadhav/Desktop/UPTRAIL/data/cleaned_data/postings.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return pd.DataFrame()

    df = pd.read_csv(path)
    print(f"  [OK] postings.csv — {len(df)} rows")

    out = pd.DataFrame()
    out["title"]    = df.get("job_title", "")
    out["company"]  = df.get("company", "")
    out["location"] = df.get("job_location", "")
    out["role"]     = df.get("job_title", "")       # use job_title as role for matching
    out["skills"]   = df.get("job_skills", "")
    out["link"]     = df.get("job_link", "")
    out["duration"] = df.get("job_type", "")
    out["stipend"]  = ""                             # not in this dataset
    out["mode"]     = ""                             # not in this dataset
    out["source"]   = "LinkedIn"

    return out


def load_internshala():
    path = os.path.join("data", "raw", "/Users/vaidehijadhav/Desktop/UPTRAIL/data/cleaned_data/Internshala.csv")
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return pd.DataFrame()

    df = pd.read_csv(path)
    print(f"  [OK] internshala.csv — {len(df)} rows")

    out = pd.DataFrame()
    out["title"]    = df.get("Title", "")
    out["company"]  = df.get("Company Name", "")
    out["location"] = df.get("Location", "")
    out["role"]     = df.get("Title", "")            # use Title as role for matching
    out["skills"]   = ""                             # not in this dataset
    out["link"]     = df.get("Links", "")
    out["duration"] = df.get("Duration", "")
    out["stipend"]  = df.get("Stipend", "")
    out["mode"]     = ""                             # derive below
    out["source"]   = "Internshala"

    # Derive mode from location
    out["mode"] = out["location"].apply(
        lambda loc: "Remote" if str(loc).lower() == "work from home" else "On-site"
    )

    return out


def merge_all():
    print("\n── UpTrail Internship Merger ─────────────────────────────────")

    frames = [load_postings(), load_internshala()]
    frames = [f for f in frames if not f.empty]

    if not frames:
        print("\n[ERROR] No files loaded. Check paths in data/raw/")
        return

    merged = pd.concat(frames, ignore_index=True)

    # Clean up
    merged = merged.dropna(subset=["title"])
    merged = merged.drop_duplicates(subset=["title", "company"])
    merged["title"]   = merged["title"].str.strip()
    merged["company"] = merged["company"].fillna("").str.strip()
    merged["skills"]  = merged["skills"].fillna("")
    merged["link"]    = merged["link"].fillna("")
    merged["stipend"] = merged["stipend"].fillna("")
    merged["mode"]    = merged["mode"].fillna("")

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "internships.csv")
    merged.to_csv(out_path, index=False)

    print(f"\n[DONE] {len(merged)} internships → {out_path}")
    print(f"       Columns: {list(merged.columns)}")
    print(f"\nSample:\n{merged.head(3).to_string()}\n")


if __name__ == "__main__":
    merge_all()
