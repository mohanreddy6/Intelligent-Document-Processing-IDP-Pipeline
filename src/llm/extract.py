# src/llm/extract.py

import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices/receipts.
    Returns a dict via DummyModel().model_dump() to match server expectations.
    """

    key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=key)

    prompt = f"""
Extract structured invoice or receipt data from the following text:

{raw_text}

Return ONLY valid JSON in this exact format:

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

    # Call LLM
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    json_str = resp.output[0].content[0].text
    data = json.loads(json_str)

    # Match server expectation
    class DummyModel:
        def __init__(self, d):
            self.d = d
        def model_dump(self):
            return self.d

    return DummyModel(data)
