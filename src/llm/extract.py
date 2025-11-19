# src/llm/extract.py

import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices.
    Guarantees valid JSON (auto-repair if needed).
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    # FIRST TRY
    resp = client.responses.create(
        model="gpt-4.1-turbo",
        input=prompt,
        temperature=0
    )

    # Extract model output
    first = resp.output[0].content[0].text.strip()

    # Try to JSON-parse
    try:
        data = json.loads(first)
    except Exception:
        # SECOND TRY — JSON REPAIR
        repair_prompt = f"Fix this into valid JSON ONLY:\n{first}"

        repair = client.responses.create(
            model="gpt-4.1-turbo",
            input=repair_prompt,
            temperature=0
        )

        repaired = repair.output[0].content[0].text.strip()

        try:
            data = json.loads(repaired)
        except Exception:
            # FINAL FALLBACK — return safe empty object
            data = {
                "vendor": {},
                "items": [],
                "payment": {},
                "_math": {"status": "error", "note": "LLM failed twice"},
                "raw_text": raw_text
            }

    # Server expects .model_dump()
    class DummyModel:
        def __init__(self, d):
            self.d = d

        def model_dump(self):
            return self.d

    return DummyModel(data)
