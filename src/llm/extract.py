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
