import os, json, re
from pathlib import Path
from pdfminer.high_level import extract_text as pdf_text
import docx
from openai import AzureOpenAI
from dotenv import load_dotenv
import typing as _t
from json import JSONDecodeError



# ------------------------------------------------------------------ #
#  module‑level one‑time setup                                        #
# ------------------------------------------------------------------ #
load_dotenv()                           # pulls values from .env

AZ_ENDPOINT  = os.getenv("AZURE_OPENAI_ENDPOINT")
AZ_KEY       = os.getenv("AZURE_OPENAI_API_KEY")
AZ_API_VER   = os.getenv("AZURE_OPENAI_API_VERSION")   # e.g. 2024‑05‑01‑preview
AZ_DEPLOY    = os.getenv("AZURE_OPENAI_DEPLOYMENT")    # your deployment name

client = AzureOpenAI(                  # identical to the snippet you sent
    azure_endpoint = AZ_ENDPOINT,
    api_key        = AZ_KEY,
    api_version    = AZ_API_VER,
)
# ------------------------------------------------------------------ #
#  helper functions (text extraction unchanged)                       #
# ------------------------------------------------------------------ #
BASE_SAVE = Path(r"C:\Resume Code")
BASE_SAVE.mkdir(exist_ok=True)

# ---------- text extraction ----------
def extract_resume(pdf_path: Path) -> str:
    text = pdf_text(pdf_path)
    (BASE_SAVE / "Resume extracted.txt").write_text(text, encoding="utf-8")
    return text

def extract_jd(docx_path: Path) -> str:
    doc = docx.Document(docx_path)
    text = "\n".join(p.text for p in doc.paragraphs)
    (BASE_SAVE / "JD extracted.txt").write_text(text, encoding="utf-8")
    return text

# ------------------------------------------------------------------ #
#  NEW Azure OpenAI call                                              #
# ------------------------------------------------------------------ #
def keyword_match_stats(resume_text: str, jd_text: str) -> dict:
    """
    Returns {"JDKey": int, "MatchKey": int}
    """
    prompt = f"""
You are an API that returns ONLY JSON. 
1️⃣ Derive a unique lowercase keyword list from the Job Description (JD).  
2️⃣ Count how many keywords are in JD (JDKey).  
3️⃣ Count how many of those keywords also appear in the Resume (MatchKey).  
Return exactly: {{"JDKey": <int>, "MatchKey": <int>}}
JD:
\"\"\"{jd_text}\"\"\"
RESUME:
\"\"\"{resume_text}\"\"\"
    """.strip()

    messages = [
        {"role": "system", "content": "You are a helper agent."},
        {"role": "user",   "content": prompt},
    ]

    response = client.chat.completions.create(
        model      = AZ_DEPLOY,
        messages   = messages,
        max_tokens = 50,
        temperature= 0.1,
        top_p      = 0.05,
        frequency_penalty = 0,
        presence_penalty  = 0,
        response_format = {"type": "json_object"},
        stream     = False,
    )

    raw = response.choices[0].message.content.strip()
    print("DEBUG raw content:", repr(raw))          # ① quick visibility

    try:
        data = json.loads(raw)
        return {
            "JDKey":   int(data["JDKey"]),
            "MatchKey": int(data["MatchKey"]),
        }
    except (JSONDecodeError, KeyError, TypeError, ValueError):
        raise RuntimeError(f"Azure OpenAI did not return valid JSON: {raw!r}")
