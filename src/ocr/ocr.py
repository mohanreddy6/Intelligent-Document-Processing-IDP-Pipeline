import pytesseract
from PIL import Image
import io

def ocr_text(file_or_image):
    """
    Handles both:
    - Flask uploaded file stream
    - Pillow Image objects
    """

    # CASE 1: Already a Pillow Image (common in your pipeline)
    if isinstance(file_or_image, Image.Image):
        image = file_or_image

    else:
        # CASE 2: Raw file upload stream
        # Convert the raw stream into a Pillow image
        image = Image.open(file_or_image).convert("RGB")

    # Run OCR
    text = pytesseract.image_to_string(image)
    return text
