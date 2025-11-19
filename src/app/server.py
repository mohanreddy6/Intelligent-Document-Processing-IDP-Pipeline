# src/app/server.py
from __future__ import annotations



import base64
import io
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError

# --- OCR + parsing ---
from src.ocr.ocr import ocr_text            # your existing OCR
from src.ocr.parse import parse_invoice     # rule-based parser
from src.ocr.validate import reconcile_payment

# Try to import the LLM extractor (optional)
from src.llm.extract import extract_structured as llm_extract_structured
HAS_LLM = True


# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB uploads

# CORS: allow your GitHub Pages site to call this API
CORS(app, resources={r"/*": {"origins": ["https://mohanreddy6.github.io"]}})

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _json_error(msg: str, code: int = 400):
    return jsonify({"error": msg}), code


def _load_image_from_upload() -> Image.Image | None:
    """
    Read 'file' from multipart/form-data into a PIL Image.
    Returns None if missing or invalid.
    """
    f = request.files.get("file")
    if not f:
        return None
    try:
        return Image.open(f.stream)
    except UnidentifiedImageError:
        return None


def _load_image_from_b64(b64_str: str) -> Image.Image | None:
    try:
        img_bytes = base64.b64decode(b64_str)
        return Image.open(io.BytesIO(img_bytes))
    except Exception:
        return None


def _run_ocr(img: Image.Image) -> str:
    """
    Calls your OCR. If ocr_text expects bytes, convert the PIL image to PNG bytes.
    """
    try:
        # If your ocr_text accepts PIL.Image:
        return ocr_text(img)  # type: ignore[arg-type]
    except TypeError:
        # Fallback: provide bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return ocr_text(buf.getvalue())  # type: ignore[arg-type]


def _parse_structured(text: str) -> Dict[str, Any]:
    # Always use LLM parser
    result = llm_extract_structured(text)
    return result.model_dump()


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.get("/")
def home():
    # Serves: src/app/static/index.html
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/extract")
def extract():
    """
    Accepts:
      - multipart/form-data: file=<image>
      - application/json: {"image_b64": "..."} or {"text": "..."}
    Returns: {"text": "...", "parsed": {...}, "parser": "llm"|"rule_based"}
    """
    # multipart
    if request.content_type and "multipart/form-data" in request.content_type:
        img = _load_image_from_upload()
        if img is None:
            return _json_error("file missing or not a valid image", 400)
        text = _run_ocr(img)
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "llm" if HAS_LLM else "rule_based"})

    # json
    data = request.get_json(silent=True) or {}
    if "text" in data:
        text = str(data["text"])
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "llm" if HAS_LLM else "rule_based"})

    if "image_b64" in data:
        img = _load_image_from_b64(str(data["image_b64"]))
        if img is None:
            return _json_error("invalid image_b64", 400)
        text = _run_ocr(img)
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "llm" if HAS_LLM else "rule_based"})

    return _json_error("provide 'file' (multipart) or 'image_b64' or 'text'", 400)


@app.post("/extract_structured")
def extract_structured_api():
    """
    Same inputs as /extract, but returns only structured fields.
    Returns: {...parsed fields...}
    """
    # multipart
    if request.content_type and "multipart/form-data" in request.content_type:
        img = _load_image_from_upload()
        if img is None:
            return _json_error("file missing or not a valid image", 400)
        text = _run_ocr(img)
        return jsonify(reconcile_payment(_parse_structured(text)))

    # json
    data = request.get_json(silent=True) or {}
    if "text" in data:
        return jsonify(reconcile_payment(_parse_structured(str(data["text"]))))

    if "image_b64" in data:
        img = _load_image_from_b64(str(data["image_b64"]))
        if img is None:
            return _json_error("invalid image_b64", 400)
        text = _run_ocr(img)
        return jsonify(reconcile_payment(_parse_structured(text)))

    return _json_error("provide 'file' (multipart) or 'image_b64' or 'text'", 400)


if __name__ == "__main__":
    # Local dev only; production should use gunicorn from Dockerfile
    app.run(host="0.0.0.0", port=8000, debug=True)
