import pytesseract
from PIL import Image
import io

def ocr_text(file_or_image):
    """
    Real OCR with image resizing to prevent Render memory crash.
    """

    # CASE 1: Already a Pillow Image
    if isinstance(file_or_image, Image.Image):
        image = file_or_image.convert("RGB")
    else:
        # CASE 2: Flask file upload
        image = Image.open(file_or_image).convert("RGB")

    # RESIZE LARGE IMAGES (critical for Render free tier)
    MAX_WIDTH = 1200
    if image.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(image.width)
        new_height = int(image.height * ratio)
        image = image.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    # Run Tesseract
    text = pytesseract.image_to_string(image)
    return text
