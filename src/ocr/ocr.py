import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_receipt(raw_text: str) -> dict:
    """
    Parse raw OCR text into structured fields using OpenAI.
    """

    prompt = f"""
    You are a receipt parsing engine. 
    Extract structured data from the following text:

    {raw_text}

    Return ONLY valid JSON with this structure:

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

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return response.output[0].content[0].text
