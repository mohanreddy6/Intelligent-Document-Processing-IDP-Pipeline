# src/ocr/ocr.py

import os
import io
import base64
from openai import OpenAI
from PIL import Image


def ocr_text(image: Image.Image) -> str:
    """
    OCR using OpenAI vision. Takes a PIL Image and returns plain text.
    """

    # Create client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Convert image to PNG bytes
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    # Base64 encode for data URL
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    # Call vision model
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": data_url},
                    {
                        "type": "text",
                        "text": "Read all text on this invoice/receipt and return it as plain text only."
                    },
                ],
            }
        ],
        temperature=0,
    )

    # Extract the text from the response
    return resp.output[0].content[0].text
