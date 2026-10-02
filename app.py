"""
LegalMetriX: Packaged Commodity Compliance & Authenticity Verification System
Flask Application Server (Phase 1, Phase 2 & Phase 3 PDF Reports)
"""

import os
import uuid
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from backend.models import (
    ExtractedProductData,
    InspectionReport,
    SafetyIndicatorResult,
    AuthenticityReport,
    NutritionInfo,
    NutrientItem,
    AlternateProduct,
    DualPanelCoherenceResult
)
from backend.image_service import (
    allowed_file,
    analyze_image_quality,
    analyze_placement,
    MAX_IMAGE_SIZE_MB
)
from backend.gemini_service import extract_declarations_from_image, get_effective_api_key
from backend.rule_engine import run_compliance_checks, calculate_screening_summary
from backend.authenticity_engine import evaluate_authenticity_risk
from backend.nutrition_service import evaluate_nutrition_details
from backend.web_verification import discover_alternate_products
from backend.coherence_engine import evaluate_dual_panel_coherence, merge_dual_panel_declarations
from backend.pdf_report_generator import generate_inspection_pdf_report
from backend.sample_data import SAMPLE_PRESETS

# Initialize Flask app
app = Flask(__name__)
# Enable ProxyFix to respect custom domain reverse proxy headers (X-Forwarded-Host, X-Forwarded-Proto)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['SAMPLE_FOLDER'] = os.path.join(os.path.dirname(__file__), 'sample_images')
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'generated_reports')
app.config['MAX_CONTENT_LENGTH'] = MAX_IMAGE_SIZE_MB * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAMPLE_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# In-memory cache for recent inspection reports to enable direct PDF downloads
REPORT_CACHE: dict = {}


def build_inspection_report(
    image_filename: str,
    image_path: str,
    extracted_data: ExtractedProductData,
    api_key: str = None,
    preset_authenticity: AuthenticityReport = None,
    preset_nutrition: NutritionInfo = None,
    preset_alternates: list = None,
    coherence: DualPanelCoherenceResult = None
) -> InspectionReport:
    """Runs deterministic compliance checks, readability analysis, authenticity risk evaluation, nutrition analysis, and market alternates."""
    effective_key = get_effective_api_key(api_key)

    # 1. Deterministic Legal Metrology rule checks (Phase 1)
    compliance_checks = run_compliance_checks(extracted_data)
    score, overall_status, passed, total, review, failed = calculate_screening_summary(compliance_checks)

    # 2. Visual readability & quality analysis
    readability = analyze_image_quality(image_path, extracted_data.regions)

    # 3. Placement analysis
    placement = analyze_placement(extracted_data)

    # 4. Safety indicators
    safety = SafetyIndicatorResult(
        expiry_or_best_before=extracted_data.expiry_date or extracted_data.best_before,
        warnings_found=extracted_data.warnings,
        certifications_found=extracted_data.certification_marks,
        ingredients_present=bool(extracted_data.ingredients)
    )

    # 5. Authenticity Risk & Product Verification Module (Phase 2)
    if preset_authenticity:
        authenticity = preset_authenticity
    else:
        try:
            authenticity = evaluate_authenticity_risk(extracted_data, api_key=effective_key)
        except Exception as e:
            authenticity = AuthenticityReport(
                service_available=False,
                risk_level="REVIEW REQUIRED",
                risk_score=50,
                assessment_title="AUTHENTICITY VERIFICATION UNAVAILABLE",
                assessment_summary=f"Authenticity verification service encountered an issue: {str(e)}. Legal Metrology screening remains active.",
                reasons=[f"Web research service error: {str(e)}"]
            )

    # 6. Nutritional details evaluation
    if preset_nutrition:
        nutrition = preset_nutrition
    else:
        nutrition = evaluate_nutrition_details(extracted_data)

    # 7. Alternate products discovery
    if preset_alternates:
        alternates = preset_alternates
    else:
        try:
            alternates = discover_alternate_products(
                brand=extracted_data.brand,
                product_name=extracted_data.product_name,
                generic_name=extracted_data.generic_name,
                net_quantity=extracted_data.net_quantity,
                mrp=extracted_data.mrp,
                api_key=effective_key
            )
        except Exception:
            alternates = []

    report = InspectionReport(
        inspection_id=f"INSP-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
        image_filename=image_filename,
        automated_screening_score=score,
        overall_status=overall_status,
        passed_checks=passed,
        total_applicable_checks=total,
        review_checks=review,
        failed_checks=failed,
        compliance_checks=compliance_checks,
        extracted_data=extracted_data,
        readability=readability,
        placement=placement,
        safety=safety,
        authenticity=authenticity,
        nutrition=nutrition,
        alternate_products=alternates,
        coherence=coherence
    )

    # Cache report and image path for PDF generation
    REPORT_CACHE[report.inspection_id] = {
        "report": report,
        "image_path": image_path
    }

    return report


@app.route('/')
def index():
    """Main application interface."""
    has_api_key = bool(get_effective_api_key())
    return render_template('index.html', has_api_key=has_api_key)


@app.route('/privacy')
def privacy_policy():
    """Official Statutory Privacy Policy page."""
    return render_template('privacy.html')


@app.route('/terms')
def terms_and_conditions():
    """Official Terms and Operational Conditions page."""
    return render_template('terms.html')


@app.route('/favicon.ico')
def favicon():
    """Serve official vector favicon emblem."""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images for evidence viewing."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/sample_images/<filename>')
def sample_file(filename):
    """Serve sample demo images."""
    return send_from_directory(app.config['SAMPLE_FOLDER'], filename)


@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Return the structured Legal Metrology ruleset."""
    rules_path = os.path.join(os.path.dirname(__file__), 'data', 'legal_metrology_rules.json')
    if os.path.exists(rules_path):
        import json
        with open(rules_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Rules data not found"}), 404


@app.route('/api/demo/<preset_id>', methods=['POST', 'GET'])
def run_demo(preset_id):
    """Instant demo using calibrated sample data presets (Phase 1, Phase 2 & Phase 3)."""
    if preset_id not in SAMPLE_PRESETS:
        return jsonify({"success": False, "error": f"Unknown preset: {preset_id}"}), 404

    preset = SAMPLE_PRESETS[preset_id]
    image_filename = preset["filename"]
    image_path = os.path.join(app.config['SAMPLE_FOLDER'], image_filename)
    extracted_data = preset["extracted_data"]
    preset_authenticity = preset.get("preset_authenticity")
    preset_nutrition = preset.get("preset_nutrition")
    preset_alternates = preset.get("preset_alternates")
    preset_coherence = preset.get("preset_coherence")

    # If this is a deliberate mismatch preset, trigger gatekeeper rejection
    if preset_coherence and preset_coherence.status == "MISMATCH_REJECTED":
        return jsonify({
            "success": False,
            "error_type": "PANEL_MISMATCH",
            "is_demo": True,
            "preset_name": preset["name"],
            "image_url": f"/sample_images/{image_filename}",
            "coherence": preset_coherence.model_dump(),
            "message": "Cross-panel mismatch detected. The front PDP and back info panel belong to conflicting commodities."
        }), 422

    report = build_inspection_report(
        image_filename,
        image_path,
        extracted_data,
        preset_authenticity=preset_authenticity,
        preset_nutrition=preset_nutrition,
        preset_alternates=preset_alternates,
        coherence=preset_coherence
    )
    return jsonify({
        "success": True,
        "is_demo": True,
        "preset_name": preset["name"],
        "image_url": f"/sample_images/{image_filename}",
        "report": report.model_dump()
    })


@app.route('/api/verify-authenticity', methods=['POST'])
def standalone_authenticity_check():
    """Standalone API endpoint to verify product identity & authenticity risk."""
    data = request.get_json(silent=True) or {}
    try:
        extracted = ExtractedProductData(
            product_name=data.get("product_name"),
            brand=data.get("brand"),
            manufacturer=data.get("manufacturer"),
            mrp=data.get("mrp"),
            net_quantity=data.get("net_quantity"),
            barcode=data.get("barcode")
        )
        custom_key = request.headers.get("X-Gemini-Key") or data.get("gemini_key")
        effective_key = get_effective_api_key(custom_key)

        report = evaluate_authenticity_risk(extracted, api_key=effective_key)
        return jsonify({"success": True, "authenticity": report.model_dump()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/report/pdf/<inspection_id>', methods=['GET'])
def download_pdf_report(inspection_id):
    """Generates and serves professional PDF inspection report for cached or demo inspection."""
    cache_item = REPORT_CACHE.get(inspection_id)
    if not cache_item:
        return jsonify({"error": "Inspection report not found or expired. Please re-run scan."}), 404

    report: InspectionReport = cache_item["report"]
    image_path: str = cache_item["image_path"]

    pdf_filename = f"LegalMetriX_Report_{inspection_id}.pdf"
    pdf_path = os.path.join(app.config['REPORTS_FOLDER'], pdf_filename)

    try:
        generate_inspection_pdf_report(report, image_path, pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF report: {str(e)}"}), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_from_payload():
    """Generates PDF report from client JSON payload."""
    data = request.get_json(silent=True) or {}
    report_dict = data.get("report")
    image_filename = data.get("image_filename")

    if not report_dict:
        return jsonify({"error": "Report payload missing"}), 400

    try:
        report = InspectionReport(**report_dict)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], report.image_filename)
        if not os.path.exists(image_path):
            image_path = os.path.join(app.config['SAMPLE_FOLDER'], report.image_filename)

        pdf_filename = f"LegalMetriX_Report_{report.inspection_id}.pdf"
        pdf_path = os.path.join(app.config['REPORTS_FOLDER'], pdf_filename)

        generate_inspection_pdf_report(report, image_path, pdf_path)
        return jsonify({
            "success": True,
            "pdf_url": f"/api/report/pdf/{report.inspection_id}",
            "filename": pdf_filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500


@app.route('/api/inspect', methods=['POST'])
def inspect_image():
    """
    Main image upload & inspection pipeline:
    Supports:
    1. Single-panel scan ('image')
    2. Dual-panel scan ('image_front' & 'image_back') with Automated Mismatch Prevention gatekeeper
    """
    scan_mode = request.form.get("scan_mode", "single")
    is_dual = (scan_mode == "dual") or ("image_front" in request.files and "image_back" in request.files)

    # API Key check early
    custom_key = request.headers.get("X-Gemini-Key") or request.form.get("gemini_key")
    effective_key = get_effective_api_key(custom_key)

    if not effective_key:
        return jsonify({
            "success": False,
            "error_type": "NO_API_KEY",
            "error": (
                "GEMINI_API_KEY is not set on the server. Please provide an API key in the UI "
                "or test with one of the built-in sample demo presets."
            )
        }), 400

    if is_dual:
        # Dual panel inspection
        if 'image_front' not in request.files or 'image_back' not in request.files:
            return jsonify({"success": False, "error": "Both Front PDP and Back Info Panel images are required for Dual-Panel scan."}), 400

        file_front = request.files['image_front']
        file_back = request.files['image_back']

        if file_front.filename == '' or file_back.filename == '':
            return jsonify({"success": False, "error": "Both Front and Back images must be selected."}), 400

        if not allowed_file(file_front.filename) or not allowed_file(file_back.filename):
            return jsonify({"success": False, "error": "Unsupported file format. Please upload JPG, JPEG, PNG, or WEBP."}), 400

        try:
            # Save front file
            ext_front = file_front.filename.rsplit('.', 1)[1].lower()
            name_front = f"front_{uuid.uuid4().hex[:10]}.{ext_front}"
            path_front = os.path.join(app.config['UPLOAD_FOLDER'], name_front)
            file_front.save(path_front)

            # Save back file
            ext_back = file_back.filename.rsplit('.', 1)[1].lower()
            name_back = f"back_{uuid.uuid4().hex[:10]}.{ext_back}"
            path_back = os.path.join(app.config['UPLOAD_FOLDER'], name_back)
            file_back.save(path_back)

            # Extract declarations from both panels
            front_data = extract_declarations_from_image(path_front, api_key=effective_key)
            back_data = extract_declarations_from_image(path_back, api_key=effective_key)

            # Evaluate cross-panel coherence
            with open(path_front, 'rb') as f1, open(path_back, 'rb') as f2:
                coherence = evaluate_dual_panel_coherence(front_data, back_data, f1.read(), f2.read())

            # Hard Gatekeeper: Mismatch Prevention
            if not coherence.is_coherent:
                return jsonify({
                    "success": False,
                    "error_type": "PANEL_MISMATCH",
                    "scan_mode": "dual",
                    "image_url": f"/uploads/{name_front}",
                    "image_url_back": f"/uploads/{name_back}",
                    "coherence": coherence.model_dump(),
                    "message": f"Cross-panel mismatch detected ({coherence.coherence_score}% Coherence). The Front PDP and Back Info Panel belong to conflicting commodities."
                }), 422

            # Merge declarations across panels
            merged_data, _ = merge_dual_panel_declarations(front_data, back_data)

            # Run compliance, authenticity, nutrition & alternates on merged product
            report = build_inspection_report(name_front, path_front, merged_data, api_key=effective_key, coherence=coherence)

            return jsonify({
                "success": True,
                "is_demo": False,
                "scan_mode": "dual",
                "image_url": f"/uploads/{name_front}",
                "image_url_back": f"/uploads/{name_back}",
                "report": report.model_dump()
            })

        except ValueError as ve:
            return jsonify({"success": False, "error": str(ve)}), 400
        except Exception as e:
            return jsonify({"success": False, "error": f"Dual-panel inspection failed: {str(e)}"}), 500

    else:
        # Single-panel scan (standard workflow)
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image file provided in request."}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "No image file selected."}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Unsupported file format. Please upload JPG, JPEG, PNG, or WEBP."
            }), 400

        try:
            # Save file securely
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"scan_{uuid.uuid4().hex[:10]}.{ext}"
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(saved_path)

            # Step 1: AI Multimodal Extraction via Gemini
            extracted_data = extract_declarations_from_image(saved_path, api_key=effective_key)

            # Step 2: Legal Metrology Rule Engine & Authenticity Risk Engine
            report = build_inspection_report(unique_name, saved_path, extracted_data, api_key=effective_key)

            return jsonify({
                "success": True,
                "is_demo": False,
                "image_url": f"/uploads/{unique_name}",
                "report": report.model_dump()
            })

        except ValueError as ve:
            return jsonify({"success": False, "error": str(ve)}), 400
        except Exception as e:
            return jsonify({"success": False, "error": f"Inspection failed: {str(e)}"}), 500


if __name__ == '__main__':
    print("==================================================================")
    print(" LegalMetriX: Packaged Commodity Inspection & PDF Report System  ")
    print(" SIH Problem Statement ID: 26034 (Phase 1, Phase 2 & Phase 3 PDF) ")
    print(" Running at: http://127.0.0.1:5000                                ")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
