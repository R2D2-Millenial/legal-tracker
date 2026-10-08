import json
import os
from google import genai

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
      "Concrete step for legal / compliance",
      "Notice / policy revision required"
    ],
    "source_url": "Direct link"
  }
]
"""

def analyze_legal_data(raw_entries):
    prompt = f"""
    You are an expert Indian In-House General Counsel. Analyze the following legal news items and circulars from the past week:
    {json.dumps(raw_entries)}

    Rules:
    1. Filter out minor criminal matters, political debates, or routine procedural notices. Focus strictly on corporate, compliance, regulatory, employment, commercial, and tech law.
    2. Sort results in descending order of commercial and compliance priority.
    3. Tag 'High' impact to items with significant penalty exposure, immediate operational changes, or statutory deadlines.
    4. Provide concrete, non-generic operational action items for the legal team.
    5. Return pure JSON conforming strictly to this format:
    {ANALYSIS_SCHEMA}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={'response_mime_type': 'application/json'}
    )
    return json.loads(response.text)
