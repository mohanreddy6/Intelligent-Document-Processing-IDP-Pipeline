import pytesseract
from PIL import Image
import io

def ocr_text(file_stream):
    """
    Performs OCR on the uploaded image using Tesseract.
    """
    # Open image from the file stream
    image = Image.open(file_stream.stream).convert("RGB")

    # Perform OCR
    text = pytesseract.image_to_string(image)

    return text
