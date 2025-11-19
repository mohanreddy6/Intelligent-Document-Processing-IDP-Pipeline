# src/llm/extract.py

import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices/receipts.
    """

    # Create client inside function
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    Extract structured invoice/receipt data from this text:

    {raw_text}

    Return ONLY valid JSON in this structure:

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
      "raw_text": ""
    }}
    """

    # FIRST CALL — generation
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0
    )

    raw = resp.output[0].content[0].text.strip()

    # If JSON loads fine, return
    try:
        data = json.loads(raw)

    except json.JSONDecodeError:
        # Repair JSON
        repair_prompt = f"""
        The following text is INVALID JSON. Fix it and output ONLY valid JSON:

        {raw}
        """

        repair = client.responses.create(
            model="gpt-4o-mini",
            input=repair_prompt,
            temperature=0
        )

        fixed = repair.output[0].content[0].text.strip()
        data = json.loads(fixed)

    class DummyModel:
        def __init__(self, d):
            self.d = d

        def model_dump(self):
            return self.d

    return DummyModel(data)
