"""
LegalMetriX Rule Engine
Deterministic compliance validation based on the official Legal Metrology (Packaged Commodities) Rules, 2011.

Evaluates structured extracted packaging declarations against statutory requirements.
Statuses returned: 'pass', 'fail', 'review', 'missing', 'non-standard'.
"""

import re
import json
import os
from typing import List, Dict, Any, Tuple
from backend.models import ExtractedProductData, ComplianceCheckResult, InspectionReport


# Statutory Rule References from LMR 2011 (G.S.R. 202(E))
RULES_REF = {
    "LM_MFR": "Rule 6(1)(a) & Rule 10, Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_NAME": "Rule 6(1)(b), Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_QTY": "Rule 6(1)(c) & Rules 11, 12, 13, Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_MRP": "Rule 6(1)(e) & Rule 2(m), Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_DATE": "Rule 6(1)(d) & Rule 6(1) Expl. I, Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_CARE": "Rule 6(2), Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_COO": "Rule 6(1)(a) & Rule 10(1) Proviso, Legal Metrology (Packaged Commodities) Rules, 2011",
    "LM_USP": "Rule 6(1)(e) Amendment / Proviso, Legal Metrology Rules",
    "LM_EXP": "Rule 6(1)(d) Proviso & FSSA/Drugs Rules, Legal Metrology Rules"
}


def is_ocr_corrupted(text: str) -> bool:
    """Detects OCR corruption markers such as black squares, replacement characters, or garbled text."""
    if not text:
        return False
    corrupted_markers = ["■", "□", "", "CPCP Regn"]
    return any(marker in text for marker in corrupted_markers if marker)



def check_manufacturer(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Manufacturer / Packer / Importer declaration under Rule 6(1)(a) & Rule 10.
    Requires name and complete postal address.
    CRITICAL: Does NOT treat 'MARKETED BY' as equivalent to Manufacturer / Packer / Importer.
    """
    mfr = data.manufacturer or data.packer or data.importer
    evidence = None
    if data.manufacturer:
        evidence = f"Manufacturer: {data.manufacturer}"
    elif data.packer:
        evidence = f"Packer: {data.packer}"
    elif data.importer:
        evidence = f"Importer: {data.importer}"

    all_text = " ".join([
        data.manufacturer or "",
        data.packer or "",
        data.importer or "",
        " ".join(data.other_visible_text or [])
    ]).upper()

    has_marketed_only = ("MARKETED BY" in all_text or "MKTD BY" in all_text) and not any(
        k in all_text for k in ["MFG BY", "MANUFACTURED BY", "PACKED BY", "PKD BY", "IMPORTED BY", "IMP BY"]
    )

    if has_marketed_only or (data.manufacturer and "MARKETED BY" in data.manufacturer.upper() and not any(
        k in data.manufacturer.upper() for k in ["MANUFACTURED BY", "PACKED BY", "IMPORTED BY", "MFG BY", "PKD BY"]
    )):
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="review",
            classification="role_ambiguity",
            ocr_status="uncertain",
            raw_ocr=mfr,
            detected_value=mfr or "MARKETED BY declaration only",
            expected="Name and complete postal address of Manufacturer, Packer, or Importer",
            confidence=0.75,
            rule_reference=RULES_REF["LM_MFR"],
            reason="A marketer declaration was detected, but the available evidence does not establish the required manufacturer/packer/importer information.",
            evidence=evidence or mfr,
            evidence_id="E-003",
            severity="high",
            mandatory=True
        )

    if not mfr or mfr.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="missing",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value=None,
            expected="Name and complete postal address of Manufacturer, Packer, or Importer",
            confidence=0.90,
            rule_reference=RULES_REF["LM_MFR"],
            reason="No manufacturer, packer, or importer declaration detected on visible label.",
            evidence=None,
            evidence_id=None,
            severity="high",
            mandatory=True
        )

    val = mfr.strip()

    if is_ocr_corrupted(val):
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value=val,
            expected="Clear Manufacturer / Packer name and postal address",
            confidence=0.60,
            rule_reference=RULES_REF["LM_MFR"],
            reason="Manufacturer text was detected but OCR interpretation was partially corrupted.",
            evidence=evidence or val,
            evidence_id="E-003",
            severity="high",
            mandatory=True
        )

    address_keywords = [
        r"\bpin\b", r"\b\d{6}\b", r"\bindustrial\b", r"\bind\b", r"\bplot\b",
        r"\broad\b", r"\brd\b", r"\bstreet\b", r"\bnagar\b", r"\bsector\b",
        r"\bdist\b", r"\bstate\b", r"\bindia\b", r"\bltd\b", r"\bpvt\b",
        r"\bmfg\b", r"\bmanufactured by\b", r"\bpacked by\b"
    ]
    has_address_cue = any(re.search(kw, val, re.IGNORECASE) for kw in address_keywords)

    if len(val) >= 12 and has_address_cue:
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="pass",
            classification="compliant",
            ocr_status="detected",
            detected_value=val,
            expected="Name and complete address of Manufacturer / Packer / Importer",
            confidence=0.92,
            rule_reference=RULES_REF["LM_MFR"],
            reason="Manufacturer/Packer identity and address cues detected on packaging.",
            evidence=evidence or val,
            evidence_id="E-003",
            severity="high",
            mandatory=True
        )
    elif len(val) >= 3:
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="review",
            classification="role_ambiguity",
            ocr_status="uncertain",
            detected_value=val,
            expected="Complete address with City, State, and Postal PIN Code",
            confidence=0.75,
            rule_reference=RULES_REF["LM_MFR"],
            reason="Entity name detected, but full postal address details (PIN code/city) appear incomplete or partially cropped.",
            evidence=evidence or val,
            evidence_id="E-003",
            severity="high",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-001",
            field_name="Manufacturer / Packer / Importer",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            detected_value=val,
            expected="Name and complete address of Manufacturer / Packer / Importer",
            confidence=0.60,
            rule_reference=RULES_REF["LM_MFR"],
            reason="Uncertain manufacturer text detected; manual inspection required.",
            evidence=evidence or val,
            evidence_id="E-003",
            severity="high",
            mandatory=True
        )


def check_product_name(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Common / Generic name of commodity under Rule 6(1)(b).
    """
    name = data.product_name or data.generic_name or data.brand
    evidence = []
    if data.product_name:
        evidence.append(f"Product: {data.product_name}")
    if data.generic_name:
        evidence.append(f"Generic: {data.generic_name}")
    if data.brand:
        evidence.append(f"Brand: {data.brand}")
    ev_str = " | ".join(evidence) if evidence else None

    if not name or name.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-002",
            field_name="Product Name / Generic Name",
            status="review",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value="NOT RELIABLY DETECTED",
            expected="Common or generic name of the commodity",
            confidence=0.92,
            rule_reference=RULES_REF["LM_NAME"],
            reason="Product commodity / generic name could not be reliably extracted from visible label panel.",
            evidence=None,
            evidence_id=None,
            severity="high",
            mandatory=True
        )

    val = name.strip()
    if is_ocr_corrupted(val):
        return ComplianceCheckResult(
            finding_id="LM-002",
            field_name="Product Name / Generic Name",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value="NOT RELIABLY DETECTED (Corrupted OCR)",
            expected="Common or generic name of commodity",
            confidence=0.65,
            rule_reference=RULES_REF["LM_NAME"],
            reason="Product name text was detected but OCR interpretation was corrupted.",
            evidence=ev_str or val,
            evidence_id="E-002",
            severity="high",
            mandatory=True
        )

    if len(val) >= 3:
        return ComplianceCheckResult(
            finding_id="LM-002",
            field_name="Product Name / Generic Name",
            status="pass",
            classification="compliant",
            ocr_status="detected",
            detected_value=val,
            expected="Common or generic name of the commodity",
            confidence=0.94,
            rule_reference=RULES_REF["LM_NAME"],
            reason="Product commodity / generic identification detected.",
            evidence=ev_str or val,
            evidence_id="E-002",
            severity="high",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-002",
            field_name="Product Name / Generic Name",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            detected_value=val,
            expected="Clear common or generic commodity name",
            confidence=0.70,
            rule_reference=RULES_REF["LM_NAME"],
            reason="Detected product name is very short or ambiguous; visual review recommended.",
            evidence=ev_str or val,
            evidence_id="E-002",
            severity="high",
            mandatory=True
        )


def check_net_quantity(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Net Quantity under Rule 6(1)(c) and Rules 11-13.
    Checks standard metric units (g, kg, ml, l, N, U, etc.) and prohibits misleading terms like 'when packed' / 'approx'.
    """
    qty = data.net_quantity
    if not qty or qty.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-003",
            field_name="Net Quantity",
            status="missing",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value=None,
            expected="Net quantity in standard metric units (g, kg, ml, l, or count N/U)",
            confidence=0.92,
            rule_reference=RULES_REF["LM_QTY"],
            reason="Net quantity declaration not detected on visible label.",
            evidence=None,
            evidence_id=None,
            severity="high",
            mandatory=True
        )

    val = qty.strip()

    if is_ocr_corrupted(val):
        return ComplianceCheckResult(
            finding_id="LM-003",
            field_name="Net Quantity",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value=f"{val} (Uncertain OCR)",
            expected="Net quantity in standard metric units",
            confidence=0.60,
            rule_reference=RULES_REF["LM_QTY"],
            reason="Net quantity text detected but OCR was partially corrupted.",
            evidence=f"Net Qty: {val}",
            evidence_id="E-004",
            severity="high",
            mandatory=True
        )

    prohibited_patterns = [r"\bwhen packed\b", r"\bapprox\b", r"\bapproximately\b", r"\bminimum\b", r"\bnot less than\b"]
    for pattern in prohibited_patterns:
        if re.search(pattern, val, re.IGNORECASE):
            return ComplianceCheckResult(
                finding_id="LM-003",
                field_name="Net Quantity",
                status="fail",
                classification="non_standard_format",
                ocr_status="detected",
                detected_value=val,
                expected="Net quantity without non-standard qualifiers (Rule 11(2), Rule 12(6))",
                confidence=0.95,
                rule_reference=RULES_REF["LM_QTY"],
                reason=f"Prohibited qualifier ('{re.search(pattern, val, re.IGNORECASE).group(0)}') found in quantity declaration.",
                evidence=f"Net Qty: {val}",
                evidence_id="E-004",
                severity="high",
                mandatory=True
            )

    metric_regex = r"(\d+(?:\.\d+)?)\s*(kg|g|gms|gm|gram|grams|mg|ml|l|ltr|litre|litres|liter|liters|cm|m|meter|meters|n|u|units|pcs|pieces|count)\b"
    match = re.search(metric_regex, val, re.IGNORECASE)

    if match:
        return ComplianceCheckResult(
            finding_id="LM-003",
            field_name="Net Quantity",
            status="pass",
            classification="compliant",
            ocr_status="detected",
            detected_value=val,
            expected="Net quantity in standardized metric units",
            confidence=0.95,
            rule_reference=RULES_REF["LM_QTY"],
            reason=f"Standard metric net quantity declaration detected ({match.group(0)}).",
            evidence=f"Net Quantity: {val}",
            evidence_id="E-004",
            severity="high",
            mandatory=True
        )
    elif any(char.isdigit() for char in val):
        return ComplianceCheckResult(
            finding_id="LM-003",
            field_name="Net Quantity",
            status="non_standard",
            classification="non_standard_format",
            ocr_status="uncertain",
            detected_value=val,
            expected="Net quantity with clear standard metric unit (e.g. g, kg, ml, l, N)",
            confidence=0.75,
            rule_reference=RULES_REF["LM_QTY"],
            reason="A numeric value was detected, but the quantity unit or declaration context could not be reliably established.",
            evidence=f"Net Quantity: {val}",
            evidence_id="E-004",
            severity="high",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-003",
            field_name="Net Quantity",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            detected_value=val,
            expected="Standard metric net quantity declaration",
            confidence=0.65,
            rule_reference=RULES_REF["LM_QTY"],
            reason="Uncertain net quantity format; manual review required.",
            evidence=f"Net Quantity: {val}",
            evidence_id="E-004",
            severity="high",
            mandatory=True
        )


def check_mrp(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Maximum Retail Price (MRP) declaration under Rule 6(1)(e) & Rule 2(m).
    Format required: 'MRP Rs. ... / ₹ ... incl. of all taxes'.
    Also checks for multiple conflicting MRP declarations (potentially misleading).
    """
    mrp_str = data.mrp
    if not mrp_str or mrp_str.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="missing",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value=None,
            expected="MRP declaration in the form 'MRP Rs. / ₹ ... incl. of all taxes'",
            confidence=0.93,
            rule_reference=RULES_REF["LM_MRP"],
            reason="Retail sale price / MRP declaration not detected on visible label.",
            evidence=None,
            evidence_id=None,
            severity="high",
            mandatory=True
        )

    val = mrp_str.strip()

    # Remove Unit Sale Price (USP) expressions (e.g., USP Rs.0.67/g, Rs 0.67/g, ₹5.00/g) from MRP conflict evaluation
    usp_pattern = r"(?:\(?\s*(?:USP|Unit Sale Price)?\s*(?:₹|Rs\.?|INR)\s*\d+(?:\.\d+)?\s*(?:/|per)\s*(?:g|gm|kg|ml|l|ltr|unit|n|pcs)\s*\)?)"
    mrp_text_clean = re.sub(usp_pattern, "", val + " " + " ".join(data.other_visible_text or []), flags=re.IGNORECASE).strip()

    # Find explicit MRP values (prefixed by MRP, M.R.P., Max Retail Price, Retail Sale Price)
    mrp_matches = re.findall(r"(?:mrp|maximum retail price|max retail price|retail sale price)\.?\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d{1,2})?)", mrp_text_clean, re.IGNORECASE)
    
    # Also find standalone prices in mrp_text_clean if no explicit MRP tag is matched
    if not mrp_matches:
        mrp_matches = re.findall(r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d{1,2})?)", mrp_text_clean, re.IGNORECASE)

    unique_mrp_prices = list(set(mrp_matches))

    # Only classify as potentially_misleading if two or more DISTINCT values are explicitly associated with MRP!
    if len(unique_mrp_prices) >= 2:
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="potentially_misleading",
            classification="potentially_misleading",
            ocr_status="uncertain",
            detected_value=f"Multiple conflicting MRP values: ₹{' and ₹'.join(unique_mrp_prices)}",
            expected="Single unambiguous Maximum Retail Price (MRP) declaration",
            confidence=0.80,
            rule_reference=RULES_REF["LM_MRP"],
            reason="Multiple potentially conflicting MRP values were detected on the supplied package image. Manual verification required.",
            evidence=f"Detected: {val} | Other: {' '.join(data.other_visible_text)}",
            evidence_id="E-005",
            severity="high",
            mandatory=True
        )

    if is_ocr_corrupted(val):
        nums = re.findall(r"\d+(?:\.\d{1,2})?", val)
        norm_val = f"MRP ₹{nums[0]}" if nums else val
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value=f"Raw OCR: '{val}' (Normalized: '{norm_val}')",
            expected="MRP in statutory format 'MRP ₹ ... incl. of all taxes'",
            confidence=0.60,
            rule_reference=RULES_REF["LM_MRP"],
            reason="The currency symbol/value representation is partially uncertain in the extracted text.",
            evidence=f"MRP: {val}",
            evidence_id="E-005",
            severity="high",
            mandatory=True
        )

    has_currency_or_mrp = any(term in val.lower() for term in ["mrp", "₹", "rs", "inr", "rupees", "price"])

    if has_currency_or_mrp and any(c.isdigit() for c in val):
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="pass",
            classification="compliant",
            ocr_status="detected",
            detected_value=val,
            expected="MRP / Retail Sale Price declaration inclusive of all taxes",
            confidence=0.94,
            rule_reference=RULES_REF["LM_MRP"],
            reason="Maximum Retail Price (MRP) declaration detected with statutory currency/price markers.",
            evidence=f"MRP: {val}",
            evidence_id="E-005",
            severity="high",
            mandatory=True
        )
    elif any(c.isdigit() for c in val):
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="review",
            classification="non_standard_format",
            ocr_status="uncertain",
            detected_value=val,
            expected="MRP in statutory format with 'MRP' or '₹/Rs.' prefix",
            confidence=0.72,
            rule_reference=RULES_REF["LM_MRP"],
            reason="Price numeral detected, but explicit 'MRP' descriptor or tax inclusion statement is ambiguous.",
            evidence=f"Detected: {val}",
            evidence_id="E-005",
            severity="high",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-004",
            field_name="Retail Sale Price (MRP)",
            status="review",
            classification="uncertain_extraction",
            ocr_status="uncertain",
            detected_value=val,
            expected="MRP / Retail Sale Price declaration",
            confidence=0.60,
            rule_reference=RULES_REF["LM_MRP"],
            reason="Detected MRP text is ambiguous; manual inspection recommended.",
            evidence=f"Detected: {val}",
            evidence_id="E-005",
            severity="high",
            mandatory=True
        )




def check_date(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Month and Year of Manufacture / Packing / Import under Rule 6(1)(d) & Expl. I.
    """
    mfg = data.manufacturing_date
    pkd = data.packing_date
    imp = data.import_date
    date_val = mfg or pkd or imp

    evidence_parts = []
    if mfg:
        evidence_parts.append(f"Mfg: {mfg}")
    if pkd:
        evidence_parts.append(f"Pkd: {pkd}")
    if imp:
        evidence_parts.append(f"Import: {imp}")
    ev_str = " | ".join(evidence_parts) if evidence_parts else None

    if not date_val or date_val.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-005",
            field_name="Manufacture / Packing / Import Date",
            status="missing",
            ocr_status="not_detected",
            detected_value=None,
            expected="Month and Year of manufacture, packing, or import (MM/YYYY or Month Year)",
            confidence=0.91,
            rule_reference=RULES_REF["LM_DATE"],
            reason="Month & year of manufacture/packing/import declaration not detected on visible label.",
            evidence=None,
            evidence_id=None,
            severity="high",
            mandatory=True
        )

    val = date_val.strip()

    if is_ocr_corrupted(val):
        return ComplianceCheckResult(
            finding_id="LM-005",
            field_name="Manufacture / Packing / Import Date",
            status="review",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value=f"{val} (Uncertain OCR)",
            expected="Month and year of manufacture or pre-packing",
            confidence=0.60,
            rule_reference=RULES_REF["LM_DATE"],
            reason="Date text detected but OCR was partially corrupted.",
            evidence=ev_str or val,
            evidence_id="E-006",
            severity="high",
            mandatory=True
        )

    date_patterns = [
        r"\b(?:0?[1-9]|1[0-2])[/\-\.](?:20\d{2}|\d{2})\b",  # MM/YYYY or MM/YY
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s/\-\.']*(?:20\d{2}|\d{2})\b",  # Month YYYY
        r"\b(?:20\d{2})[/\-\.](?:0?[1-9]|1[0-2])\b"  # YYYY/MM
    ]
    is_valid_format = any(re.search(p, val, re.IGNORECASE) for p in date_patterns)

    if is_valid_format:
        return ComplianceCheckResult(
            finding_id="LM-005",
            field_name="Manufacture / Packing / Import Date",
            status="pass",
            ocr_status="detected",
            detected_value=val,
            expected="Month and year of manufacture or pre-packing",
            confidence=0.93,
            rule_reference=RULES_REF["LM_DATE"],
            reason="Month and year of manufacture/packing detected in compliant format.",
            evidence=ev_str or val,
            evidence_id="E-006",
            severity="high",
            mandatory=True
        )
    elif any(c.isdigit() for c in val):
        return ComplianceCheckResult(
            finding_id="LM-005",
            field_name="Manufacture / Packing / Import Date",
            status="review",
            ocr_status="uncertain",
            detected_value=val,
            expected="Clear Month and Year (MM/YYYY or Month Year)",
            confidence=0.75,
            rule_reference=RULES_REF["LM_DATE"],
            reason="Date string detected, but month/year formatting or prefix (MFD/PKD) is ambiguous.",
            evidence=ev_str or val,
            evidence_id="E-006",
            severity="high",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-005",
            field_name="Manufacture / Packing / Import Date",
            status="review",
            ocr_status="uncertain",
            detected_value=val,
            expected="Month and year of manufacture/packing/import",
            confidence=0.60,
            rule_reference=RULES_REF["LM_DATE"],
            reason="Date text detected but format could not be verified automatically.",
            evidence=ev_str or val,
            evidence_id="E-006",
            severity="high",
            mandatory=True
        )


def check_consumer_care(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Consumer Care Contact Details under Rule 6(2).
    Requires name, address, telephone number, and/or email address for consumer complaints.
    """
    care = data.consumer_care
    if not care or care.strip().lower() in ["none", "null", "not detected", ""]:
        return ComplianceCheckResult(
            finding_id="LM-006",
            field_name="Consumer Care Details",
            status="missing",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value=None,
            expected="Name, address, telephone number, and email address for consumer complaints",
            confidence=0.88,
            rule_reference=RULES_REF["LM_CARE"],
            reason="No reliable consumer-care declaration was detected.",
            evidence=None,
            evidence_id=None,
            severity="medium",
            mandatory=True
        )


    val = care.strip()
    if is_ocr_corrupted(val):
        return ComplianceCheckResult(
            finding_id="LM-006",
            field_name="Consumer Care Details",
            status="review",
            ocr_status="uncertain",
            raw_ocr=val,
            detected_value=f"{val} (Uncertain OCR)",
            expected="Consumer care contact details for complaints",
            confidence=0.60,
            rule_reference=RULES_REF["LM_CARE"],
            reason="Consumer care text detected but OCR was partially corrupted.",
            evidence=f"Consumer Care: {val}",
            evidence_id="E-007",
            severity="medium",
            mandatory=True
        )

    has_phone = bool(re.search(r"(?:1800|\b\d{10}\b|\b\d{3,5}[-\s]\d{6,8}\b|\+91\b|tel|phone|toll[\s-]free)", val, re.IGNORECASE))
    has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", val))
    has_care_keyword = any(k in val.lower() for k in ["consumer", "customer", "care", "helpline", "feedback", "complaint", "contact"])

    if (has_phone or has_email) and (has_care_keyword or len(val) >= 10):
        return ComplianceCheckResult(
            finding_id="LM-006",
            field_name="Consumer Care Details",
            status="pass",
            ocr_status="detected",
            detected_value=val,
            expected="Consumer care contact channels (telephone / email / address)",
            confidence=0.91,
            rule_reference=RULES_REF["LM_CARE"],
            reason="Consumer care contact details (telephone / email / grievance cell) detected.",
            evidence=f"Consumer Care: {val}",
            evidence_id="E-007",
            severity="medium",
            mandatory=True
        )
    elif has_care_keyword or has_phone or has_email:
        return ComplianceCheckResult(
            finding_id="LM-006",
            field_name="Consumer Care Details",
            status="review",
            ocr_status="uncertain",
            detected_value=val,
            expected="Complete telephone number and email address for consumer complaints",
            confidence=0.75,
            rule_reference=RULES_REF["LM_CARE"],
            reason="Partial consumer care text found, but complete helpline number or email address could not be fully resolved.",
            evidence=f"Consumer Care: {val}",
            evidence_id="E-007",
            severity="medium",
            mandatory=True
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-006",
            field_name="Consumer Care Details",
            status="review",
            ocr_status="uncertain",
            detected_value=val,
            expected="Consumer grievance contact details",
            confidence=0.65,
            rule_reference=RULES_REF["LM_CARE"],
            reason="Phone or text found without explicit consumer-care context; manual verification required.",
            evidence=f"Consumer Care: {val}",
            evidence_id="E-007",
            severity="medium",
            mandatory=True
        )


def check_country_of_origin(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Country of Origin declaration (Rule 6(1)(a) & Rule 10(1) Proviso).
    """
    coo = data.country_of_origin
    if coo and coo.strip().lower() not in ["none", "null", "not detected", ""]:
        val = coo.strip()
        return ComplianceCheckResult(
            finding_id="LM-007",
            field_name="Country of Origin",
            status="pass",
            ocr_status="detected",
            detected_value=val,
            expected="Country of origin / manufacturing declaration",
            confidence=0.92,
            rule_reference=RULES_REF["LM_COO"],
            reason=f"Country of origin declared: {val}.",
            evidence=f"Country of Origin: {val}",
            evidence_id="E-008",
            severity="medium",
            mandatory=False
        )
    else:
        mfr_text = (data.manufacturer or "") + (data.packer or "")
        if "india" in mfr_text.lower():
            return ComplianceCheckResult(
                finding_id="LM-007",
                field_name="Country of Origin",
                status="pass",
                ocr_status="detected",
                detected_value="India (inferred from manufacturer address)",
                expected="Country of origin declaration",
                confidence=0.82,
                rule_reference=RULES_REF["LM_COO"],
                reason="Domestic Indian manufacturing address detected on packaging.",
                evidence=f"Address: {mfr_text[:40]}...",
                evidence_id="E-008",
                severity="medium",
                mandatory=False
            )
        else:
            return ComplianceCheckResult(
                finding_id="LM-007",
                field_name="Country of Origin",
                status="review",
                ocr_status="not_detected",
                detected_value="Not detected explicitly",
                expected="Country of origin declaration (mandatory for imported commodities)",
                confidence=0.70,
                rule_reference=RULES_REF["LM_COO"],
                reason="Country of origin not explicitly isolated; mandatory for imported goods and recommended for domestic products.",
                evidence=None,
                evidence_id=None,
                severity="medium",
                mandatory=False
            )


def check_unit_sale_price(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Unit Sale Price (USP) under Legal Metrology amendments where applicable.
    Recognizes USP formats such as USP Rs.0.67/g, Rs 0.25 / g, ₹ 5.00 / g, etc.
    """
    usp = data.unit_sale_price

    if not usp or usp.strip().lower() in ["none", "null", "not detected", ""]:
        combined_text = (data.mrp or "") + " " + " ".join(data.other_visible_text or [])
        if data.regions:
            combined_text += " " + " ".join([r.text for r in data.regions if r.text])

        usp_match = re.search(r"(?:USP|Unit Sale Price)?\s*(?:₹|Rs\.?|INR)\s*\d+(?:\.\d+)?\s*(?:/|per)\s*(?:g|gm|kg|ml|l|ltr|unit|n|pcs)\b", combined_text, re.IGNORECASE)
        if usp_match:
            usp = usp_match.group(0).strip()

    if usp and usp.strip().lower() not in ["none", "null", "not detected", ""]:
        val = usp.strip()
        return ComplianceCheckResult(
            finding_id="LM-008",
            field_name="Unit Sale Price (USP)",
            status="pass",
            classification="compliant",
            ocr_status="detected",
            detected_value=val,
            expected="Unit sale price (e.g. ₹ per g / ml / piece)",
            confidence=0.92,
            rule_reference=RULES_REF["LM_USP"],
            reason="Unit Sale Price declaration detected in statutory format.",
            evidence=f"USP: {val}",
            evidence_id="E-009",
            severity="low",
            mandatory=False
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-008",
            field_name="Unit Sale Price (USP)",
            status="review",
            classification="missing_declaration",
            ocr_status="not_detected",
            detected_value="Not detected",
            expected="Unit Sale Price (₹/g, ₹/ml, ₹/unit) where package net quantity exceeds 1g/1ml or multi-piece",
            confidence=0.75,
            rule_reference=RULES_REF["LM_USP"],
            reason="Unit Sale Price not detected; statutory requirement depends on packaging category and net quantity.",
            evidence=None,
            evidence_id=None,
            severity="low",
            mandatory=False
        )



def check_expiry_or_best_before(data: ExtractedProductData) -> ComplianceCheckResult:
    """
    Validates Expiry Date / Best Before declaration where applicable.
    """
    exp = data.expiry_date or data.best_before
    evidence_list = []
    if data.best_before:
        evidence_list.append(f"Best Before: {data.best_before}")
    if data.expiry_date:
        evidence_list.append(f"Expiry: {data.expiry_date}")
    ev_str = " | ".join(evidence_list) if evidence_list else None

    if exp and exp.strip().lower() not in ["none", "null", "not detected", ""]:
        val = exp.strip()
        return ComplianceCheckResult(
            finding_id="LM-009",
            field_name="Best Before / Expiry Date",
            status="pass",
            ocr_status="detected",
            detected_value=val,
            expected="Best before / Expiry date declaration where applicable",
            confidence=0.92,
            rule_reference=RULES_REF["LM_EXP"],
            reason="Shelf life / best-before / expiry declaration detected.",
            evidence=ev_str or val,
            evidence_id="E-010",
            severity="medium",
            mandatory=False
        )
    else:
        return ComplianceCheckResult(
            finding_id="LM-009",
            field_name="Best Before / Expiry Date",
            status="review",
            ocr_status="not_detected",
            detected_value="Not detected",
            expected="Best Before / Expiry date (mandatory for food, cosmetic, and perishable commodities)",
            confidence=0.75,
            rule_reference=RULES_REF["LM_EXP"],
            reason="Shelf life / expiry not detected; applicable primarily to food, cosmetic, and perishable products.",
            evidence=None,
            evidence_id=None,
            severity="medium",
            mandatory=False
        )


def run_compliance_checks(extracted_data: ExtractedProductData) -> List[ComplianceCheckResult]:
    """
    Runs the complete focused suite of Legal Metrology compliance checks.
    Order matches standard regulatory inspection protocol.
    """
    checks = [
        check_manufacturer(extracted_data),
        check_product_name(extracted_data),
        check_net_quantity(extracted_data),
        check_mrp(extracted_data),
        check_date(extracted_data),
        check_consumer_care(extracted_data),
        check_country_of_origin(extracted_data),
        check_unit_sale_price(extracted_data),
        check_expiry_or_best_before(extracted_data)
    ]
    return checks


def calculate_screening_summary(checks: List[ComplianceCheckResult]) -> Tuple[int, str, int, int, int, int]:
    """
    Calculates the Automated Screening Score and Overall Status.
    Returns: (score, overall_status, passed_count, total_applicable, review_count, failed_count)
    """
    total = len(checks)
    passed = sum(1 for c in checks if c.status == "pass")
    review = sum(1 for c in checks if c.status in ["review", "non_standard", "non-standard", "potentially_misleading"])
    failed = sum(1 for c in checks if c.status in ["fail", "missing"])

    # Automated Screening Score = (passed / total) * 100
    score = int(round((passed / total) * 100)) if total > 0 else 0

    # Determine overall status
    mandatory_fails = [c for c in checks if c.mandatory and c.status in ["fail", "missing"]]
    if mandatory_fails or failed >= 2:
        overall_status = "FAIL / DEFICIENCIES DETECTED"
    elif review > 0 or failed > 0:
        overall_status = "REVIEW REQUIRED"
    else:
        overall_status = "PRELIMINARY PASS"

    return score, overall_status, passed, total, review, failed


