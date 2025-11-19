# src/app/server.py
from __future__ import annotations

import base64
import io
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError

# --- OCR + parsing ---
from src.ocr.ocr import ocr_text
from src.ocr.parse import parse_invoice
from src.ocr.validate import reconcile_payment

# --------------------------------------------------------------
# DISABLE LLM (FREE MODE)
# --------------------------------------------------------------
HAS_LLM = False
llm_extract_structured = None

# --------------------------------------------------------------
# App setup
# --------------------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

CORS(app, resources={r"/*": {"origins": ["https://mohanreddy6.github.io"]}})

# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------
def _json_error(msg: str, code: int = 400):
    return jsonify({"error": msg}), code

def _load_image_from_upload() -> Image.Image | None:
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
    try:
        return ocr_text(img)
    except TypeError:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return ocr_text(buf.getvalue())

# --------------------------------------------------------------
# RULE-BASED ONLY — NO LLM
# --------------------------------------------------------------
def _parse_structured(text: str) -> Dict[str, Any]:
    return parse_invoice(text)

# --------------------------------------------------------------
# Routes
# --------------------------------------------------------------
@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/extract")
def extract():
    if request.content_type and "multipart/form-data" in request.content_type:
        img = _load_image_from_upload()
        if img is None:
            return _json_error("file missing or invalid image")
        text = _run_ocr(img)
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "rule_based"})

    data = request.get_json(silent=True) or {}
    if "text" in data:
        text = str(data["text"])
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "rule_based"})

    if "image_b64" in data:
        img = _load_image_from_b64(str(data["image_b64"]))
        if img is None:
            return _json_error("invalid image_b64")
        text = _run_ocr(img)
        parsed = reconcile_payment(_parse_structured(text))
        return jsonify({"text": text, "parsed": parsed, "parser": "rule_based"})

    return _json_error("provide 'file' or 'image_b64' or 'text'")

@app.post("/extract_structured")
def extract_structured_api():
    if request.content_type and "multipart/form-data" in request.content_type:
        img = _load_image_from_upload()
        if img is None:
            return _json_error("file missing or invalid image")
        text = _run_ocr(img)
        return jsonify(reconcile_payment(_parse_structured(text)))

    data = request.get_json(silent=True) or {}
    if "text" in data:
        return jsonify(reconcile_payment(_parse_structured(str(data["text"]))))

    if "image_b64" in data:
        img = _load_image_from_b64(str(data["image_b64"]))
        if img is None:
            return _json_error("invalid image_b64")
        text = _run_ocr(img)
        return jsonify(reconcile_payment(_parse_structured(text)))

    return _json_error("provide 'file' or 'image_b64' or 'text'")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
