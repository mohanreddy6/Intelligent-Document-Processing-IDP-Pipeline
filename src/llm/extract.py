# src/llm/extract.py
import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    schema = """
{
  "vendor": {
    "name": "",
    "address": "",
    "phone": "",
    "date": "",
    "time": "",
    "invoice_no": ""
  },
  "items": [
    {
      "description": "",
      "qty": 0,
      "unit_price": 0,
      "total": 0
    }
  ],
  "payment": {
    "method": "",
    "currency": "USD",
    "subtotal": 0,
    "tax": 0,
    "tip": 0,
    "total": 0
  },
  "_math": {
    "status": "ok",
    "note": ""
  },
  "raw_text": ""
}
"""

    prompt = f"""
Extract structured invoice data from the text below.

TEXT:
{raw_text}

Return ONLY valid JSON matching this schema:
{schema}
"""

    # MAIN extraction
    resp = client.responses.create(
        model="gpt-4.1",    # stronger model
        input=prompt,
        temperature=0
    )

    output = resp.output[0].content[0].text.strip()

    data = _safe_json(output)
    if data:
        data["raw_text"] = raw_text
        return DummyModel(data)

    # Try repair
    repair_prompt = f"Fix this so it is valid JSON ONLY:\n\n{output}"

    fix = client.responses.create(
        model="gpt-4.1",
        input=repair_prompt,
        temperature=0
    )

    fixed = fix.output[0].content[0].text.strip()

    data = _safe_json(fixed)
    if data:
        data["raw_text"] = raw_text
        return DummyModel(data)

    # Fallback
    return DummyModel(_fallback(raw_text))


def _safe_json(text):
    try:
        return json.loads(text)
    except:
        return None


def _fallback(raw):
    return {
        "vendor": {
            "name": "",
            "address": "",
            "phone": "",
            "date": "",
            "time": "",
            "invoice_no": ""
        },
        "items": [],
        "payment": {
            "method": "",
            "currency": "USD",
            "subtotal": 0,
            "tax": 0,
            "tip": 0,
            "total": 0
        },
        "_math": {"status": "failed", "note": "LLM could not parse"},
        "raw_text": raw
    }


class DummyModel:
    def __init__(self, d):
        self.d = d
    def model_dump(self):
        return self.d
