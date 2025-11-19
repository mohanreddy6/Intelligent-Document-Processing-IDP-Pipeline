# src/llm/extract.py
import os
import json
from openai import OpenAI

def extract_structured(raw_text: str):
    """
    LLM-based structured extraction with safe JSON repair.
    Never throws JSONDecodeError.
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 1. Ask model for JSON
    prompt = f"""
You are an OCR invoice parser. 
Extract structured JSON ONLY.

TEXT:
{raw_text}

Return ONLY this JSON structure:

{{
  "vendor": {{
    "name": "",
    "address": "",
    "phone": "",
    "date": "",
    "time": "",
    "invoice_no": ""
  }},
  "items": [],
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
  "raw_text": ""
}}
    """

    # Ask LLM
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    raw_output = resp.output[0].content[0].text.strip()

    # 2. If output is empty → fallback
    if not raw_output:
        return _fallback_model()

    # 3. Try load JSON directly
    try:
        data = json.loads(raw_output)
        return _wrap(data)
    except:
        pass  # Continue to repair step

    # 4. Try repairing JSON
    repair_prompt = f"Fix this so it becomes valid JSON ONLY:\n\n{raw_output}"
    fix = client.responses.create(
        model="gpt-4.1-mini",
        input=repair_prompt,
        temperature=0
    )

    fixed = fix.output[0].content[0].text.strip()

    try:
        data = json.loads(fixed)
        return _wrap(data)
    except:
        return _fallback_model()


# ---------- helper wrappers ----------
class DummyModel:
    def __init__(self, d):
        self.d = d
    def model_dump(self):
        return self.d

def _wrap(d):
    return DummyModel(d)

def _fallback_model():
    # return empty safe structure instead of crashing
    return DummyModel({
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
        "_math": { "status": "failed", "note": "LLM returned invalid JSON" },
        "raw_text": ""
    })
