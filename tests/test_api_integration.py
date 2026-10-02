"""
Integration tests for LegalMetriX Flask Endpoints
"""

import io
import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"LegalMetriX" in response.data
    assert b"Legal Metrology" in response.data


def test_privacy_page(client):
    response = client.get('/privacy')
    assert response.status_code == 200
    assert b"Privacy Policy" in response.data
    assert b"Digital Personal Data Protection Act" in response.data


def test_terms_page(client):
    response = client.get('/terms')
    assert response.status_code == 200
    assert b"Terms" in response.data
    assert b"Legal Metrology Act, 2009" in response.data


def test_favicon_endpoint(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.content_type.startswith("image/svg+xml")


def test_rules_endpoint(client):
    response = client.get('/api/rules')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "rules" in data
    assert len(data["rules"]) >= 8


def test_demo_preset_compliant(client):
    response = client.post('/api/demo/biscuit_compliant')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["report"]["automated_screening_score"] == 100
    assert data["report"]["overall_status"] == "PRELIMINARY PASS"
    assert data["report"]["passed_checks"] == 9


def test_demo_preset_partial_review(client):
    response = client.post('/api/demo/noodles_partial_review')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["report"]["overall_status"] == "REVIEW REQUIRED"
    assert data["report"]["review_checks"] > 0


def test_demo_preset_non_compliant(client):
    response = client.post('/api/demo/shampoo_non_compliant')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "FAIL" in data["report"]["overall_status"]
    assert data["report"]["failed_checks"] >= 2


def test_inspect_upload_validation(client):
    # Test uploading without file
    response = client.post('/api/inspect', data={})
    assert response.status_code == 400

    # Test invalid file format
    response = client.post('/api/inspect', data={
        'image': (io.BytesIO(b"fake text data"), 'test.txt')
    })
    assert response.status_code == 400
    assert b"Unsupported file format" in response.data
