[![CI](https://github.com/mohanreddy6/idp-pipeline/actions/workflows/main.yml/badge.svg)](https://github.com/mohanreddy6/idp-pipeline/actions/workflows/main.yml)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-informational)


# Intelligent Document Processing (IDP) Pipeline

## 1. Problem Story – Why This Project Exists

Imagine a small operations team in a company.

Every week they receive hundreds of receipts and invoices from employees, vendors, and delivery partners. These arrive as photos from mobile phones, scans from printers, or PDFs from email. Someone has to open each document, read it carefully, and type the following into a system:

- Vendor name  
- Date  
- Item names  
- Quantity  
- Price  
- Tax and totals  

It is repetitive, slow, and error-prone. A simple typo in an amount or a missing item later creates problems in accounting, reimbursement, and audits.

The goal of this project is to remove most of that manual work.

The **Intelligent Document Processing (IDP) Pipeline** is a small service that takes an image of a receipt or invoice and returns structured JSON with the useful information extracted. It can be used as a backend building block in:

- Expense management tools  
- Accounts payable automation  
- Back-office reconciliation systems  
- Logistics and delivery proof-of-purchase flows  
- Any workflow where receipts or invoices need to be digitised into structured data  

Instead of a human reading every document, the system does the initial extraction. Humans only review exceptions.

---

## 2. Where This Can Be Used

Some typical use cases:

- **Employee reimbursements**  
  Employees upload receipts in a portal or app. The backend hits this API to extract totals, vendors, and line items automatically.

- **Vendor invoice processing**  
  A finance team receives many vendor invoices by email or upload. This service converts them into structured JSON that can be pushed into an accounting system.

- **Retail or e-commerce operations**  
  Stores or warehouses scan receipts or invoices, and this service extracts line items for reconciliation and reporting.

- **Automation / RPA**  
  Bots or scripts can call this API instead of implementing OCR and parsing logic from scratch.

---

## 3.Project Diagram

This is the overall view of the system.

```
+------------------------------+
|        Client / System       |
| (Web app, backend, script)   |
+---------------+--------------+
                |
                | HTTP request
                v
+---------------+--------------+
|            Flask API         |
|  /extract, /extract_structured
+---------------+--------------+
                |
        +-------+-------+
        |               |
        v               v
+---------------+   +-----------------------+
|  OCR Module   |   |   Parser Module       |
|  (Tesseract)  |   | (LLM + rules-based)   |
+-------+-------+   +-----------+-----------+
        |                       |
        v                       v
+-----------------+      +---------------------------+
|  Raw OCR Text   |      | Structured JSON           |
+-----------------+      | (vendor, items, totals)   |
                         +---------------------------+
```

---

## 4. Pipeline Flowchart

This shows the step-by-step processing from input document to final result.

```
+------------------------------------------------+
|            Start: Document Received            |
+-------------------------+----------------------+
                          |
                          v
                +---------+----------+
                | Validate Request   |
                | (file present?)    |
                +---------+----------+
                          |
                    if invalid
                          v
                +---------+----------+
                |  Return HTTP 400   |
                |  (bad request)     |
                +--------------------+

                          |
                   if valid file
                          v
                +---------+----------+
                |  Run OCR Module    |
                |  (Tesseract)       |
                +---------+----------+
                          |
                          v
                +--------------------+
                |  Got Raw Text      |
                +---------+----------+
                          |
              +-----------+-----------+
              |                       |
              |  /extract endpoint    |
              |  (raw text only)     |
              v                       |
    +---------+----------+            |
    | Return JSON with   |            |
    | raw_text only      |            |
    +--------------------+            |
                                      |
                                      |
              |  /extract_structured endpoint
              v
    +----------------------------+
    | Decide Mode:              |
    | DRY_RUN = 1 or 0?         |
    +-------------+-------------+
                  |
        +---------+----------+
        | if DRY_RUN = 1    |
        | use mock parser   |
        +---------+---------+
                  |
                  v
        +---------------------------+
        | if DRY_RUN = 0           |
        | call LLM-based parser    |
        | (requires API key)       |
        +---------------------------+
                  |
                  v
        +---------------------------+
        | Build structured JSON     |
        | (vendor, items, totals,   |
        |  raw_text)                |
        +-------------+-------------+
                      |
                      v
             +--------+---------+
             | Return JSON      |
             | Response         |
             +------------------+
```

---

## 5. Project Structure

The repository is intentionally kept small and readable.

```
idp-pipeline/
├── app.py                 # Flask API entry point
├── scripts/
│   ├── ocr.py             # OCR-related functionality
│   └── parser.py          # Parsing logic (LLM + rules)
├── tests/
│   ├── test_ocr.py        # Unit tests for OCR
│   └── test_parser.py     # Unit tests for parser
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 6. Algorithm Flow Diagram

This diagram shows the full logic from receiving a file to returning structured JSON.

```
                     +----------------------+
                     |        (Start)       |   
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |   Input: File Upload |  
                     +----------+-----------+
                                |
                                v
                 +---------------------------------+
                 | Is a file present in the request?| 
                 +-----------------+---------------+
                                   |Yes
                                   |
                                   |            No
                                   |             \
                                   v              \
                     +----------------------+       \
                     | Load image from file |        \
                     +----------+-----------+         \
                                |                      \
                                v                       \
                     +----------------------+            \
                     | Preprocess image     |             \
                     | (resize, grayscale)  |              \
                     +----------+-----------+               \
                                |                            \
                                v                             \
                     +-------------------------+               \
                     | Run OCR (Tesseract)     |                \
                     +-----------+-------------+                 \
                                 |                                 \
                                 v                                  \
                     +---------------------------+                   \
                     |  Raw Text Extracted       |                    \
                     +-------------+-------------+                     \
                                   |                                   \
                                   v                                    \
                +-----------------------------------+                   \
                |  Endpoint: /extract used?         |          \
                +------------------+----------------+                     |
                                   |Yes                                 No|
                                   |                                      |
                                   v                                      v
              +--------------------------------------+    +-----------------------------+
              | Output raw_text as JSON and return    |    |  Endpoint: /extract_structured? |
              +----------------+-----------------------+    +--------------+------------------+
                                   |                                         |
                                   |                                         v
                                   |                          +---------------------------------+
                                   |                          |   Decide Mode (DRY_RUN ?)       |
                                   |                          +----------------+----------------+
                                   |                                         |
                                   |                              +----------+----------+
                                   |                              |   DRY_RUN == 1 ?    |  
                                   |                              +----+------------+---+
                                   |                                   |            |
                                   |                                   |Yes         |No
                                   |                                   v            v
                                   |                +--------------------+     +-------------------------+
                                   |                | Use Mock Parser    |     | Use LLM-based Parser    |
                                   |                | (Deterministic Data)|     | (Needs API key)         |
                                   |                +---------+----------+     +-----------+-------------+
                                   |                          |                      |
                                   |                          v                      v
                                   |                +-------------------------+   +---------------------------+
                                   |                | Build Structured JSON   |   | Build Structured JSON       |
                                   |                +------------+------------+   +-------------+---------------+
                                   |                             |                             |
                                   |                             v                             v
                                   |                +-----------------------------+             |
                                   |                | Return Final JSON Response  | 
                                   |                +--------------+--------------+
                                   |                               |
                                   v                               v
                        +----------------------++----------------------+
                        |      (End)           |       (End)           |  
                        +----------------------+------------------------+
```

## 7. Local Setup and Running the Service

### 7.1 Clone and Install

```bash
git clone https://github.com/mohanreddy6/idp-pipeline.git
cd idp-pipeline

python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate

pip install -r requirements.txt
```

### 7.2 Run the Server

```bash
python app.py
```

By default, the Flask app will be available at:

```
http://localhost:5000
```

---

## 8. Live Demo – Try It With a Real Invoice

The easiest way to understand the project is to try the hosted demo.

Demo URL:  
https://idp-pipeline.onrender.com

Suggested steps:

1. Open the URL in a browser.  
2. Choose the endpoint you want to test (`/extract` or `/extract_structured`).  
3. Upload an invoice or receipt image from your machine.  
4. Submit the request.  
5. Look at the JSON output and confirm that vendor, items, and totals are extracted.

---

## 9. Example API Usage

### 9.1 Using `curl`

```bash
curl -X POST "https://idp-pipeline.onrender.com/extract_structured" \
-F "file=@invoice.jpg"
```

### 9.2 Example JSON Response

```json
{
  "vendor": "Walmart",
  "items": [
    { "name": "Milk", "qty": 1, "price": 2.89 },
    { "name": "Bread", "qty": 2, "price": 3.50 }
  ],
  "subtotal": 9.89,
  "tax": 0.79,
  "total": 10.68,
  "raw_text": "WALMART SUPERCENTER..."
}
```

---

## 10. Limitations

- OCR quality depends heavily on image clarity and resolution.  
- Handwritten receipts may not parse correctly.  
- Real parsing mode depends on an external LLM and internet access.  
- Different invoice formats may require adjustments or more rules.

---

## 11. Testing

You can run the tests with:

```bash
pytest
```

This will run the unit tests for OCR and parsing logic.

---


This will make the project easier to understand for new developers and more convincing in a production or interview setting.

