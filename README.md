# LegalMetriX

An automated compliance inspection, label verification, and statutory notice system for packaged commodities in India, built in reference to the **Legal Metrology (Packaged Commodities) Rules, 2011** and the **Legal Metrology Act, 2009**.

---

## Overview

In retail and e-commerce supply chains, verifying consumer packaging against statutory requirements is a labor-intensive manual task. Non-compliant labeling (e.g. missing unit sale prices, inadequate font heights, incomplete manufacturer addresses, or missing consumer care information) leads to consumer disputes, regulatory notices, and penalties under Section 36 of the Legal Metrology Act.

**LegalMetriX** is an end-to-end inspection console that extracts label declarations from packaging photographs, validates them against statutory rules, detects cross-panel mismatches, checks market authenticity signals, and generates official 2-page A4 PDF inspection reports and statutory show-cause notices.

---

## Key Features

### 1. Dual-Panel Guided Upload & Mismatch Prevention
- **Single or Dual Mode**: Upload a flat unfolded package, or inspect the Principal Display Panel (PDP) and Back Information Panel side-by-side.
- **Automated Mismatch Shield**: Compares brand identity, commodity category, and net quantity across front and back photographs. Rejects conflicting uploads with HTTP 422 before running checks to prevent fraudulent label pairing.

### 2. Live Camera Packaging Scanner
- Capture packaging labels in real-time directly from a connected webcam or mobile device camera.
- Supports multi-camera device switching with high-resolution frame capture for immediate analysis.

### 3. Statutory Legal Metrology Rule Engine
- **Rule 6(1)(a)**: Manufacturer / Packer / Importer name and complete address verification.
- **Rule 6(1)(b)**: Generic name and commodity identity check.
- **Rule 6(1)(c)**: Net quantity and standardized measurement units.
- **Rule 6(1)(d)**: Month and year of manufacture, packing, or import.
- **Rule 6(1)(da)**: Unit Sale Price (USP) calculation and rounding validation.
- **Rule 6(1)(e)**: Consumer care details (name, address, telephone, email).
- **Rule 6(2)**: Maximum Retail Price (MRP) declaration including taxes format.
- **Table-I Font & Numeral Height Check**: Evaluates declared font sizes against net quantity capacity thresholds.

### 4. Authenticity Risk & Corroboration Engine
- Evaluates label credibility across barcode consistency, price-to-weight sanity thresholds, and manufacturer presence.
- Cross-references declarations against verified public catalog listings and retail references without transmitting sensitive session data.

### 5. Nutrition & Front-of-Pack Evaluation
- Extracts declared nutrient metrics (energy, protein, carbohydrates, added sugars, saturated fats, sodium).
- Applies FSSAI traffic light indicators to highlight elevated sugar, saturated fat, or sodium levels. Automatically identifies non-food consumer commodities (e.g. cosmetics or cleaners) and notes statutory exemptions.

### 6. Alternate Products Discovery
- Identifies market alternatives, healthier reformulations, and value choices available in the Indian market with comparative unit pricing.

### 7. Statutory Legal Notice & Seizure Memo Generator
- Generates an immediate legal notice draft citing contraventions under Section 36(1) and compounding rights under Section 48 of the Legal Metrology Act, 2009.
- Ready for clipboard export or printing by field inspectors.

### 8. Interactive Rulebook Navigator Modal
- Searchable clause handbook covering mandatory declarations, Table-I numeral heights, and compounding provisions.
- Includes an interactive numeral height calculator for quick verification across different package sizes.

### 9. Professional 2-Page A4 PDF Inspection Dossier
- Generates structured, tamper-evident inspection reports using ReportLab with 12 standardized sections, embedded visual evidence, and page numbering.

---

## Architecture

```
                    PACKAGING IMAGE(S)
                (Front PDP / Back Info Panel)
                              |
                    Multimodal Vision OCR
                              |
                   Extracted Declarations
                              |
         +--------------------+--------------------+
         v                    v                    v
[ Mismatch Shield ]   [ Rule Engine ]     [ Authenticity & Web ]
(Cross-Panel Check)   (Rule 6, USP, Ht)   (Barcode, MRP, Catalogs)
         |                    |                    |
         +--------------------+--------------------+
                              |
                              v
                  [ Consolidated Report ]
                              |
         +--------------------+--------------------+
         v                                         v
[ Web Inspection Dashboard ]             [ ReportLab Engine ]
(Badges, Signals, Notice)                (Official 2-Page PDF)
```

---

## Project Structure

```
legalMatrix/
|-- app.py                     # Main Flask application and API routes
|-- requirements.txt           # Python dependencies
|-- .env.example               # Environment variables configuration template
|-- CUSTOM_DOMAIN_SETUP.md     # Production deployment and domain setup guide
|-- backend/
|   |-- models.py              # Pydantic data schemas
|   |-- rule_engine.py         # Legal Metrology 2011 rule verification logic
|   |-- authenticity_engine.py # Authenticity risk assessment engine
|   |-- coherence_engine.py    # Cross-panel mismatch prevention gatekeeper
|   |-- image_service.py       # OpenCV sharpness, resolution, and quality checks
|   |-- gemini_service.py      # Vision extraction integration
|   |-- nutrition_service.py   # Nutrition extraction and FSSAI indicators
|   |-- web_verification.py    # Reference catalog and alternate product discovery
|   |-- pdf_report_generator.py# ReportLab 2-page A4 PDF generator
|   +-- sample_data.py         # Calibrated demo presets for testing
|-- data/
|   |-- legal_metrology_rules.json   # Structured regulatory clauses
|   +-- legalmetrix_repository.db    # Reference product database
|-- sample_images/             # Calibrated demo packaging images
|-- static/
|   |-- css/style.css          # Design system stylesheet
|   |-- js/app.js              # Client application logic
|   +-- favicon.svg            # Vector emblem favicon
|-- templates/
|   |-- index.html             # Main inspection interface
|   |-- privacy.html           # Statutory Privacy Policy page
|   +-- terms.html             # Terms and Operational Conditions page
+-- tests/
    |-- test_api_integration.py     # Endpoint and page integration tests
    |-- test_authenticity_engine.py # Authenticity engine unit tests
    |-- test_pdf_report.py          # PDF generation tests
    +-- test_rule_engine.py         # Rule compliance check unit tests
```

---

## Quickstart

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Yashvin186/LegalMatrix.git
cd LegalMatrix
```

### 2. Set Up Virtual Environment
```bash
# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and configure your Gemini API key (optional if using the built-in demo presets):
```bash
cp .env.example .env
```

Edit `.env`:
```ini
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=development
PORT=5000
```

### 5. Run the Application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## Running the Automated Test Suite

The project includes unit and integration tests covering the rule engine, authenticity calculations, PDF compilation, and HTTP endpoints:

```bash
python -m pytest tests/ -v
```

All 28 tests should pass out of the box without requiring external network connectivity or paid API credentials.

---

## Production Deployment & Custom Domains

For deploying LegalMetriX to a public server with a custom domain (e.g. `inspect.yourdomain.com`) and Let's Encrypt SSL, refer to the complete deployment guide in [CUSTOM_DOMAIN_SETUP.md](CUSTOM_DOMAIN_SETUP.md).

Key highlights:
- `ProxyFix` is enabled in `app.py` for handling reverse-proxy headers (`X-Forwarded-Host`, `X-Forwarded-Proto`).
- Includes turnkey Nginx site configuration, systemd service setup, and SSL renewal instructions.

---

## Regulatory Reference & Statutory Disclaimer

LegalMetriX evaluates package declarations strictly in reference to:
1. **The Legal Metrology Act, 2009** (Act No. 1 of 2010).
2. **The Legal Metrology (Packaged Commodities) Rules, 2011** (as amended).
3. **The Food Safety and Standards (Packaging and Labelling) Regulations**.

**Disclaimer**: LegalMetriX is an automated decision-support system designed for preliminary inspection, auditing, and report generation. Final legal enforcement, seizure notices under Section 15, and compounding orders under Section 48 must be executed by an authorized Legal Metrology Officer following physical examination of the packaged commodity.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
