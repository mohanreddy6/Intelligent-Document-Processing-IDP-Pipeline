# src/llm/extract.py

import os
import json
from openai import OpenAI


def extract_structured(raw_text: str):
    """
    LLM-based structured extraction for invoices/receipts.
    """

    # CREATE CLIENT INSIDE FUNCTION, NEVER AT IMPORT TIME
    key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=key)

    # UNIVERSAL INVOICE PARSING PROMPT
    prompt = f"""
You are a highly accurate invoice/receipt parsing engine.

Extract structured data from the OCR text below and 
return ONLY valid JSON in this exact structure, regardless of invoice layout:

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
    "status": "",
    "note": ""
  }},
  "raw_text": ""
}}

RULES:
- Automatically identify all line items.
- Automatically extract vendor information.
- Automatically extract invoice number, date, time, phone, address.
- Automatically extract subtotal, tax, tip, total.
- Automatically detect payment method (ACH, VISA, Mastercard, Cash, etc).
