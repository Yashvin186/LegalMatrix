"""
Unit and Integration Tests for Phase 3 PDF Report Generation System
"""

import os
import json
import pytest
from backend.pdf_report_generator import generate_inspection_pdf_report
from backend.sample_data import SAMPLE_PRESETS
from app import app, build_inspection_report


def test_pdf_generation_compliant(tmp_path):
    preset = SAMPLE_PRESETS["biscuit_compliant"]
    image_path = os.path.join("sample_images", preset["filename"])
    extracted = preset["extracted_data"]
    preset_auth = preset.get("preset_authenticity")

    report = build_inspection_report(preset["filename"], image_path, extracted, preset_authenticity=preset_auth)

    output_pdf = str(tmp_path / "test_compliant_report.pdf")
    generated_path = generate_inspection_pdf_report(report, image_path, output_pdf)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 5000  # Non-empty multi-page PDF

    with open(generated_path, 'rb') as f:
        header = f.read(5)
        assert header == b"%PDF-"


def test_pdf_generation_deficient(tmp_path):
    preset = SAMPLE_PRESETS["shampoo_non_compliant"]
    image_path = os.path.join("sample_images", preset["filename"])
    extracted = preset["extracted_data"]
    preset_auth = preset.get("preset_authenticity")

    report = build_inspection_report(preset["filename"], image_path, extracted, preset_authenticity=preset_auth)

    output_pdf = str(tmp_path / "test_deficient_report.pdf")
    generated_path = generate_inspection_pdf_report(report, image_path, output_pdf)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 5000


def test_pdf_generation_fake_brand(tmp_path):
    preset = SAMPLE_PRESETS["synthetic_fake"]
    image_path = os.path.join("sample_images", preset["filename"])
    extracted = preset["extracted_data"]
    preset_auth = preset.get("preset_authenticity")

    report = build_inspection_report(preset["filename"], image_path, extracted, preset_authenticity=preset_auth)

    output_pdf = str(tmp_path / "test_fake_brand_report.pdf")
    generated_path = generate_inspection_pdf_report(report, image_path, output_pdf)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 5000


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_download_pdf_endpoint(client):
    # Run demo endpoint to cache report
    demo_res = client.post('/api/demo/biscuit_compliant')
    assert demo_res.status_code == 200
    data = json.loads(demo_res.data)
    insp_id = data["report"]["inspection_id"]

    # Request PDF download
    pdf_res = client.get(f'/api/report/pdf/{insp_id}')
    assert pdf_res.status_code == 200
    assert pdf_res.mimetype == 'application/pdf'
    assert pdf_res.data.startswith(b"%PDF-")
