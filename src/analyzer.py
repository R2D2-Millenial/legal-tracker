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
    "authority": "MCA | SEBI | RBI | MeitY | Labour Ministry | Supreme Court | NCLAT | Other",
    "law_domain": "Corporate | Securities | Employment & Labour | Privacy & Tech | Foreign Exchange | Sectoral | Commercial Litigation",
    "sector": "All Corporates | Banking/NBFC | Listed Entities | Tech/E-commerce | Pharma | Manufacturing",
    "impact_level": "High | Medium | Low",
    "priority_rank": 1,
    "effective_date": "Date or Pending Notification",
    "what_changed": "2-3 sentences contrasting the new rule against the previous legal position.",
    "inhouse_action_items": [
      "Concrete step for legal / compliance"
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

    Rules:
    1. Filter out minor criminal matters and political news. Focus strictly on corporate, compliance, regulatory, employment, commercial, and tech law.
    2. Sort in descending order of commercial/compliance priority.
    3. Tag 'High' impact to items with significant penalty exposure, immediate operational changes, or statutory deadlines.
    4. Provide concrete, non-generic operational action items for the legal team.
    5. Return pure JSON matching this structure:
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
            print(f"{model_name} busy. Switching to alternative model...")
            time.sleep(2)
        except json.JSONDecodeError:
            print(f"Retrying format parsing for {model_name}...")
            time.sleep(1)

    # Fallback response if all API models fail during an outage
    return [{
        "title": "Weekly Regulatory Ingestion Completed",
        "authority": "System",
        "law_domain": "Corporate",
        "sector": "All Corporates",
        "impact_level": "Low",
        "priority_rank": 1,
        "effective_date": "N/A",
        "what_changed": "Feeds were ingested, but AI synthesis encountered temporary downtime.",
        "inhouse_action_items": ["Review source legal portals directly this week."],
        "source_url": "[https://www.livelaw.in/corporate-laws](https://www.livelaw.in/corporate-laws)"
    }]
