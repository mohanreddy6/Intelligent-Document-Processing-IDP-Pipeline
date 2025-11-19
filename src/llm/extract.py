# src/llm/extract.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices/receipts.
    Returns a pydantic-like dict (server expects .model_dump()).
    """
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

    Ensure JSON is strictly valid.
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    # Extract the text JSON
    json_str = response.output[0].content[0].text

    # Return dict (server expects .model_dump())
    class DummyModel:
        def __init__(self, data):
            self.data = data
        def model_dump(self):
            return self.data

    import json
    return DummyModel(json.loads(json_str))
