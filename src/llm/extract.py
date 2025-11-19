# src/llm/extract.py

import os
import json
from openai import OpenAI

def extract_structured(raw_text: str):
    """
    LLM-based structured extraction with JSON repair fallback.
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Prompt is SHORTER + MUCH SAFER (reduces JSON hallucination)
    prompt = f"""
Extract structured invoice data and return ONLY valid JSON.

Text:
{raw_text}

JSON format:
{{
  "vendor": {{
    "name": "",
    "address": "",
    "phone": "",
    "date": "",
    "time": "",
    "invoice_no": ""
  }},
  "items": [
    {{
      "description": "",
      "qty": 0,
      "unit_price": 0,
      "total": 0,
      "sku": ""
    }}
  ],
  "payment": {{
    "method": "",
    "currency": "USD",
    "subtotal": 0,
    "tax": 0,
    "tip": 0,
    "total": 0
  }},
  "_math": {{
    "status": "ok",
    "note": ""
  }},
  "raw_text": "{raw_text.replace('"', "'")}"
}}
"""

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    json_str = resp.output[0].content[0].text.strip()

    # -------- FIX: Repair JSON if broken ------
    try:
        data = json.loads(json_str)
    except Exception:
        # Ask model to fix JSON
        repair_prompt = f"""
Fix and return ONLY valid JSON:

{json_str}
"""
        repair = client.responses.create(
            model="gpt-4.1-mini",
            input=repair_prompt,
            temperature=0
        )
        data = json.loads(repair.output[0].content[0].text.strip())
    # ------------------------------------------

    class DummyModel:
        def __init__(self, d):
            self.d = d
        def model_dump(self):
            return self.d

    return DummyModel(data)
