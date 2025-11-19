# src/llm/extract.py

import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices/receipts.
    Returns a pydantic-like object with .model_dump() for server compatibility.
    """

    # IMPORTANT: Create the client here, NOT at import time.
    # This prevents import failures in server.py.
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    You are an invoice/receipt parsing engine.
    Extract structured data from the following OCR text:

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
