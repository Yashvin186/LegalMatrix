"""
Unit & Integration Tests for Phase 2 Authenticity Engine & Web Verification
"""

import pytest
import json
from backend.models import ExtractedProductData
from backend.authenticity_engine import evaluate_authenticity_risk
from backend.web_verification import verify_product_identity_online
from app import app


def test_genuine_product_low_risk():
    data = ExtractedProductData(
        product_name="Britannia Treat Butter Cookies",
        brand="Britannia",
        manufacturer="Britannia Industries Ltd, Kolkata",
        mrp="₹ 30.00",
        net_quantity="120 g",
        barcode="8901063012345"
    )
    report = evaluate_authenticity_risk(data)

    assert report.risk_level == "LOW"
    assert report.risk_score <= 25
    assert "LOW AUTHENTICITY RISK" in report.assessment_title
    assert any(s.name == "brand_corroboration" and s.status == "pass" for s in report.signals)


def test_synthetic_fake_brand_high_risk():
    data = ExtractedProductData(
        product_name="All In One Mixture",
        brand="Too Yumms",  # Synthetic fake brand
        manufacturer="Unverified Local Packers",
        mrp="₹ 65.00",
        net_quantity="200 g"
    )
    report = evaluate_authenticity_risk(data)

    assert report.risk_level == "HIGH"
    assert report.risk_score >= 60
    assert "HIGH AUTHENTICITY RISK" in report.assessment_title
    assert any(s.name == "brand_corroboration" and s.status == "fail" for s in report.signals)
    assert any("lacks credible online reference" in r for r in report.reasons)


def test_mrp_anomaly_elevated_risk():
    data = ExtractedProductData(
        product_name="All In One",
        brand="Too Yumm!",
        manufacturer="Guiltfree Industries",
        mrp="₹ 999.00",  # Anomaly: ₹999 vs standard ₹65
        net_quantity="200 g"
    )
    # Test heuristic web verification for MRP mismatch
    web_res = {
        "service_available": True,
        "brand_found": True,
        "product_found": True,
        "manufacturer_matched": True,
        "mrp_matched": False,  # Anomaly
        "sources": []
    }
    report = evaluate_authenticity_risk(data, web_evidence=web_res)

    assert report.risk_level in ["MEDIUM", "HIGH"]
    assert any(s.name == "mrp_consistency" and s.status == "review" for s in report.signals)
    assert any("MRP Anomaly" in r for r in report.reasons)


def test_web_verification_fallback_handled_gracefully():
    data = ExtractedProductData(
        product_name="Test Product",
        brand="Test Brand"
    )
    web_res = {
        "service_available": False,
        "error": "Network timeout",
        "brand_found": False,
        "product_found": False,
        "sources": []
    }
    report = evaluate_authenticity_risk(data, web_evidence=web_res)

    assert report.service_available is False
    assert report.risk_level == "REVIEW REQUIRED"
    assert "UNAVAILABLE" in report.assessment_title


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_verify_authenticity_endpoint(client):
    payload = {
        "brand": "Britannia",
        "product_name": "Treat Butter Cookies",
        "mrp": "₹30",
        "net_quantity": "120 g"
    }
    response = client.post('/api/verify-authenticity', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "authenticity" in data
    assert data["authenticity"]["risk_level"] == "LOW"
