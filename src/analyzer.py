import json
import os
import time
from google import genai
from google.genai.errors import ServerError, ClientError

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ANALYSIS_SCHEMA = """
[
  {
    "title": "Short title of update",
    "authority": "MeitY | DPBI | MCA | SEBI | RBI | Labour Ministry | Supreme Court | NCLAT | Other",
    "law_domain": "Data Privacy & DPDP | AI & Emerging Tech | Corporate | Securities | Employment & Labour | Foreign Exchange | Commercial Litigation",
    "sector": "All Corporates | Tech & Digital Services | Banking/NBFC | Listed Entities | Healthcare | Manufacturing",
    "impact_level": "High | Medium | Low",
    "priority_rank": 1,
    "effective_date": "Date or Pending Notification",
    "what_changed": "2-3 sentences contrasting the new rule against the previous legal position.",
    "inhouse_action_items": [
      "Concrete step for legal / compliance / infosec"
    ],
    "source_url": "Direct link"
  }
]
"""

def clean_json_text(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_legal_data(raw_entries):
    prompt = f"""
    You are an expert Indian In-House General Counsel. Analyze these legal news items from the past week:
    {json.dumps(raw_entries)}

    Special Instructions for Priority Focus:
    1. SPECIAL FOCUS ON DATA PRIVACY & DPDP ACT:
       - Give primary attention to rules, notifications, and circulars concerning the Digital Personal Data Protection (DPDP) Act, Data Protection Board of India (DPBI), consent frameworks, breach reporting, data principal rights, or data fiduciary obligations.
       - Tag material DPDP developments as 'High' impact due to statutory penalties (up to ₹250 Crores).

    2. SPECIAL FOCUS ON AI & TECH REGULATION:
       - Actively identify updates on Artificial Intelligence (AI) governance, MeitY advisories on LLMs/Generative AI, IT Rules amendments regarding deepfakes and algorithmic accountability, CERT-In cybersecurity directions, and AI-related IP/copyright issues.
       - Tag these under the 'AI & Emerging Tech' domain.

    3. GENERAL CORPORATE SCOPE:
       - Cover MCA, SEBI, RBI, and Labour Code developments.
       - Filter out criminal proceedings, local political debates, and procedural trivia.

    4. FORMAT:
       - Sort items strictly in descending order of commercial impact and compliance risk.
       - Provide concrete, actionable steps for the corporate legal team.
       - Return pure JSON conforming strictly to:
    {ANALYSIS_SCHEMA}
    """

    models_to_try = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    for model_name in models_to_try:
        try:
            print(f"Connecting to {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            cleaned = clean_json_text(response.text)
            return json.loads(cleaned)
        except (ServerError, ClientError) as e:
            print(f"{model_name} busy. Switching to backup model...")
            time.sleep(2)
        except json.JSONDecodeError:
            print(f"Retrying format parsing for {model_name}...")
            time.sleep(1)

    return [{
        "title": "Weekly Regulatory Ingestion Completed",
        "authority": "System",
        "law_domain": "Data Privacy & DPDP",
        "sector": "All Corporates",
        "impact_level": "Low",
        "priority_rank": 1,
        "effective_date": "N/A",
        "what_changed": "Feeds were ingested, but AI synthesis encountered temporary downtime.",
        "inhouse_action_items": ["Review source portals directly this week."],
        "source_url": "[https://www.livelaw.in/cyber-laws](https://www.livelaw.in/cyber-laws)"
    }]
