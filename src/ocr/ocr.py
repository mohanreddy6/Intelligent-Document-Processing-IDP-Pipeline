# src/ocr/ocr.py
from openai import OpenAI
import os

def ocr_text(image):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Convert to bytes
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "user", "content": [
                {"type": "input_image", "image": img_bytes},
                {"type": "text", "text": "Extract all text accurately."}
            ]}
        ]
    )

    return response.output[0].content[0].text
