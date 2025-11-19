# src/ocr/ocr.py

import os
import io
import base64
from openai import OpenAI
from PIL import Image


def ocr_text(image: Image.Image) -> str:
    """
    OCR using OpenAI Vision. Returns plain text.
    """

    # Create client from environment variable
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Convert PIL image → PNG bytes
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    # Base64 encode into data URL
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    # LLM vision OCR using correct content types
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": data_url},
                    {
                        "type": "input_text",
                        "text": "Extract all the text from this image accurately. Return plain text only."
                    }
                ],
            }
        ],
        temperature=0
    )

    # Extract raw text
    return response.output[0].content[0].text
