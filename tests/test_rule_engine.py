"""
Unit tests for LegalMetriX Rule Engine
Tests compliance checks against mock structured product extraction data.
"""

import pytest
from backend.models import ExtractedProductData, BoundingRegion
from backend.rule_engine import (
    check_manufacturer,
    check_product_name,
    check_net_quantity,
    check_mrp,
    check_date,
    check_consumer_care,
    check_country_of_origin,
    check_unit_sale_price,
    check_expiry_or_best_before,
    run_compliance_checks,
    calculate_screening_summary
)


def test_valid_compliant_product():
    data = ExtractedProductData(
        product_name="Crunchy Butter Cookies",
        brand="Britannia",
        manufacturer="Britannia Industries Ltd., Plot No. 12, Ind. Area, Bangalore, Karnataka - 560001, India",
        generic_name="Biscuits / Bakery Product",
        net_quantity="200 g",
        mrp="₹50.00 (Incl. of all taxes)",
        manufacturing_date="05/2026",
        consumer_care="1800-425-4444 / feedback@britannia.co.in",
        country_of_origin="India",
        unit_sale_price="₹0.25 / g",
        expiry_date="11/2026",
        batch_number="BCH-9921",
        barcode="8901063012345"
    )

    checks = run_compliance_checks(data)
    score, overall_status, passed, total, review, failed = calculate_screening_summary(checks)

    assert total == 9
    assert passed == 9
    assert failed == 0
    assert review == 0
    assert score == 100
    assert overall_status == "PRELIMINARY PASS"


def test_missing_mandatory_fields():
    data = ExtractedProductData(
        product_name=None,
        brand=None,
        manufacturer=None,
        net_quantity=None,
        mrp=None,
        manufacturing_date=None,
        consumer_care=None
    )

    checks = run_compliance_checks(data)
    score, overall_status, passed, total, review, failed = calculate_screening_summary(checks)

    # Mandatory checks should fail
    mfr_check = next(c for c in checks if c.field_name == "Manufacturer / Packer / Importer")
    name_check = next(c for c in checks if c.field_name == "Product Name / Generic Name")
    qty_check = next(c for c in checks if c.field_name == "Net Quantity")
    mrp_check = next(c for c in checks if c.field_name == "Retail Sale Price (MRP)")
    date_check = next(c for c in checks if c.field_name == "Manufacture / Packing / Import Date")
    care_check = next(c for c in checks if c.field_name == "Consumer Care Details")

    assert mfr_check.status in ["fail", "missing"]
    assert name_check.status in ["fail", "missing", "review"]
    assert qty_check.status in ["fail", "missing"]
    assert mrp_check.status in ["fail", "missing"]
    assert date_check.status in ["fail", "missing"]
    assert care_check.status in ["fail", "missing"]
    assert "FAIL" in overall_status



def test_prohibited_net_quantity_qualifiers():
    # Rule 11(2) prohibits "when packed" or "approx"
    data = ExtractedProductData(
        product_name="Herbal Soap",
        net_quantity="100 g when packed"
    )
    result = check_net_quantity(data)
    assert result.status == "fail"
    assert "Prohibited qualifier" in result.reason


def test_ambiguous_partial_fields_trigger_review():
    data = ExtractedProductData(
        product_name="A",  # Very short name
        manufacturer="ABC Corp",  # Name present without full address
        net_quantity="500",  # Number without standard unit
        mrp="50",  # Number without MRP/₹ indicator
        manufacturing_date="2026",  # Only year
        consumer_care="Call customer care"  # No phone number or email
    )

    assert check_product_name(data).status == "review"
    assert check_manufacturer(data).status == "review"
    assert check_net_quantity(data).status in ["review", "non_standard"]
    assert check_mrp(data).status == "review"
    assert check_date(data).status == "review"
    assert check_consumer_care(data).status == "review"



def test_missing_declaration():
    data = ExtractedProductData(
        consumer_care=None,
        net_quantity=None
    )
    res_care = check_consumer_care(data)
    res_qty = check_net_quantity(data)
    assert res_care.status == "missing"
    assert res_care.classification == "missing_declaration"
    assert res_qty.status == "missing"
    assert res_qty.classification == "missing_declaration"


def test_non_standard_quantity_without_unit():
    data = ExtractedProductData(net_quantity="100")
    res = check_net_quantity(data)
    assert res.status == "non_standard"
    assert res.classification == "non_standard_format"
    assert "unit or declaration context could not be reliably established" in res.reason


def test_potentially_misleading_conflicting_mrp():
    data = ExtractedProductData(
        mrp="MRP ₹50.00",
        other_visible_text=["MRP ₹80.00"]
    )
    res = check_mrp(data)
    assert res.status == "potentially_misleading"
    assert res.classification == "potentially_misleading"
    assert "Multiple potentially conflicting MRP values" in res.reason



def test_marketed_by_role_ambiguity():
    data = ExtractedProductData(
        manufacturer="MARKETED BY: ABC Foods Ltd., New Delhi"
    )
    res = check_manufacturer(data)
    assert res.status == "review"
    assert res.classification == "role_ambiguity"
    assert "marketer declaration was detected" in res.reason


def test_ocr_uncertainty_corrupted_symbol():
    data = ExtractedProductData(mrp="MRP ■ 10.00")
    res = check_mrp(data)
    assert res.status == "review"
    assert res.classification == "uncertain_extraction"
    assert "partially uncertain" in res.reason


def test_mrp_usp_separation_no_false_conflict():
    """
    CRITICAL SIH TEST CASE:
    M.R.P. ₹10.00 (USP Rs.0.67/g) (inclusive of all taxes)
    Must yield MRP: PASS and Unit Sale Price: PASS, NOT MISLEADING!
    """
    data = ExtractedProductData(
        mrp="M.R.P. ₹10.00 (USP Rs.0.67/g) (inclusive of all taxes)",
        net_quantity="22 g",
        other_visible_text=["Pkg. Mfd. By SHRINATH ROLPACK PVT. LTD."]
    )

    mrp_res = check_mrp(data)
    usp_res = check_unit_sale_price(data)

    assert mrp_res.status == "pass"
    assert mrp_res.classification == "compliant"
    assert mrp_res.status != "potentially_misleading"

    assert usp_res.status == "pass"
    assert "0.67" in usp_res.detected_value


