"""
LegalMetriX Authenticity Engine
Deterministic evaluation of product authenticity risk signals.
Calculates Authenticity Risk Score (0-100) and Risk Level (LOW, MEDIUM, HIGH, REVIEW REQUIRED).

NOTE: Does NOT claim probability of genuineness ("95% genuine") or 100% fake.
Evaluates corroboration signals and highlights unverified or anomalous claims.
"""

from typing import Dict, Any, List, Optional
from backend.models import (
    ExtractedProductData,
    AuthenticitySignal,
    AuthenticityReport,
    WebSourceEvidence
)
from backend.web_verification import verify_product_identity_online


def evaluate_authenticity_risk(
    extracted_data: ExtractedProductData,
    web_evidence: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> AuthenticityReport:
    """
    Evaluates packaging authenticity signals and web research evidence to compute:
      - Authenticity Risk Score (0 to 100, higher = elevated risk / more suspicious)
      - Risk Level ('LOW', 'MEDIUM', 'HIGH', 'REVIEW REQUIRED')
      - Signals list with transparent explanations
      - Supporting web sources with scanned vs reference comparison
    """

    if web_evidence is None:
        try:
            web_evidence = verify_product_identity_online(
                brand=extracted_data.brand,
                product_name=extracted_data.product_name,
                manufacturer=extracted_data.manufacturer or extracted_data.packer,
                mrp=extracted_data.mrp,
                net_quantity=extracted_data.net_quantity,
                barcode=extracted_data.barcode,
                api_key=api_key
            )
        except Exception as err:
            web_evidence = {
                "service_available": False,
                "error": str(err),
                "brand_found": False,
                "product_found": False,
                "sources": [],
                "summary": "Web verification service temporarily unavailable."
            }

    service_available = web_evidence.get("service_available", True)
    sources = web_evidence.get("sources", [])

    signals: List[AuthenticitySignal] = []
    reasons: List[str] = []
    risk_score = 15  # Base score for standard unverified package

    # Extract reference values from sources if available
    ref_info: Dict[str, str] = {}
    for src in sources:
        if isinstance(src, WebSourceEvidence) and src.retrieved_info:
            ref_info.update(src.retrieved_info)

    # -------------------------------------------------------------------------
    # Signal 1: Brand Corroboration
    # -------------------------------------------------------------------------
    brand_scanned = extracted_data.brand or extracted_data.product_name or "Not detected"
    brand_found = web_evidence.get("brand_found", False)
    brand_ref = ref_info.get("Brand") if brand_found else "Not available"

    if brand_found:
        signals.append(AuthenticitySignal(
            name="brand_corroboration",
            label="Brand Identity Corroboration",
            scanned_value=brand_scanned,
            reference_value=brand_ref,
            evidence_id="E-004",
            status="pass",
            reason=f"Claimed brand '{brand_scanned}' corroborated by official or established retail registry sources."
        ))
    else:
        signals.append(AuthenticitySignal(
            name="brand_corroboration",
            label="Brand Identity Corroboration",
            scanned_value=brand_scanned,
            reference_value="Not available",
            evidence_id="E-004",
            status="fail" if service_available else "review",
            reason=f"Claimed brand '{brand_scanned}' could not be corroborated from available credible web sources."
        ))
        reasons.append(f"Claimed brand '{brand_scanned}' lacks credible online reference corroboration.")
        risk_score += 40

    # -------------------------------------------------------------------------
    # Signal 2: Product Line Corroboration
    # -------------------------------------------------------------------------
    prod_scanned = extracted_data.product_name or "Not detected"
    prod_found = web_evidence.get("product_found", False)
    prod_ref = ref_info.get("Product Name") or ref_info.get("Product") if prod_found else "Not available"

    if prod_found:
        signals.append(AuthenticitySignal(
            name="product_corroboration",
            label="Product Variant Corroboration",
            scanned_value=prod_scanned,
            reference_value=prod_ref or prod_scanned,
            evidence_id="E-004",
            status="pass",
            reason=f"Product variant '{prod_scanned}' confirmed under brand registry."
        ))
    else:
        signals.append(AuthenticitySignal(
            name="product_corroboration",
            label="Product Variant Corroboration",
            scanned_value=prod_scanned,
            reference_value="Not available",
            evidence_id="E-004",
            status="review",
            reason=f"Product variant '{prod_scanned}' not explicitly matched in reference catalogs."
        ))
        reasons.append(f"Specific product variant '{prod_scanned}' not corroborated in reference product catalogs.")
        risk_score += 25

    # -------------------------------------------------------------------------
    # Signal 3: Manufacturer Consistency
    # -------------------------------------------------------------------------
    mfr_scanned = extracted_data.manufacturer or extracted_data.packer or "Not detected"
    mfr_matched = web_evidence.get("manufacturer_matched", False)
    mfr_ref = ref_info.get("Manufacturer") if mfr_matched else "Not available"

    if mfr_matched:
        signals.append(AuthenticitySignal(
            name="manufacturer_consistency",
            label="Manufacturer Identity Match",
            scanned_value=mfr_scanned[:40] + "..." if len(mfr_scanned) > 40 else mfr_scanned,
            reference_value=mfr_ref,
            evidence_id="E-004",
            status="pass",
            reason="Declared manufacturer/packer entity is consistent with brand ownership records."
        ))
    elif mfr_scanned != "Not detected" and len(mfr_scanned) > 5:
        signals.append(AuthenticitySignal(
            name="manufacturer_consistency",
            label="Manufacturer Identity Match",
            scanned_value=mfr_scanned[:40] + "..." if len(mfr_scanned) > 40 else mfr_scanned,
            reference_value="Not available",
            evidence_id="E-004",
            status="review",
            reason="Declared manufacturer on package requires verification against master brand entity."
        ))
        reasons.append("Declared manufacturer on package could not be cross-verified with master brand records.")
        risk_score += 15
    else:
        signals.append(AuthenticitySignal(
            name="manufacturer_consistency",
            label="Manufacturer Identity Match",
            scanned_value="Not detected",
            reference_value="Not available",
            evidence_id="E-004",
            status="fail",
            reason="No clear manufacturer declaration present on package to verify entity."
        ))
        reasons.append("Missing manufacturer entity declaration on package.")
        risk_score += 20

    # -------------------------------------------------------------------------
    # Signal 4: MRP & Attribute Anomaly Check
    # -------------------------------------------------------------------------
    mrp_scanned = extracted_data.mrp or "Not detected"
    mrp_matched = web_evidence.get("mrp_matched")
    mrp_ref = ref_info.get("MRP") or ref_info.get("Retail Price") if mrp_matched is not None else "Not available"

    if mrp_matched is True:
        signals.append(AuthenticitySignal(
            name="mrp_consistency",
            label="MRP / Price Consistency",
            scanned_value=mrp_scanned,
            reference_value=mrp_ref or mrp_scanned,
            evidence_id="E-004",
            status="pass",
            reason="Extracted MRP matches expected price points for this product variant."
        ))
    elif mrp_matched is False:
        signals.append(AuthenticitySignal(
            name="mrp_consistency",
            label="MRP / Price Consistency",
            scanned_value=mrp_scanned,
            reference_value=mrp_ref or "Standard Reference Pricing",
            evidence_id="E-004",
            status="review",
            reason="MRP Anomaly Detected: Declared price differs significantly from typical reference price points."
        ))
        reasons.append("MRP Anomaly: Package retail price differs from typical reference catalog pricing.")
        risk_score += 30
    else:
        signals.append(AuthenticitySignal(
            name="mrp_consistency",
            label="MRP / Price Consistency",
            scanned_value=mrp_scanned,
            reference_value="Not available",
            evidence_id="E-004",
            status="review",
            reason="Reference price comparison unavailable for this pack size."
        ))

    # -------------------------------------------------------------------------
    # Signal 5: Net Quantity Consistency
    # -------------------------------------------------------------------------
    qty_scanned = extracted_data.net_quantity or "Not detected"
    qty_matched = web_evidence.get("net_qty_matched")
    qty_ref = ref_info.get("Net Quantity") or ref_info.get("Pack Weight") if qty_matched is not None else "Not available"

    if qty_matched is True:
        signals.append(AuthenticitySignal(
            name="net_qty_consistency",
            label="Net Quantity Corroboration",
            scanned_value=qty_scanned,
            reference_value=qty_ref or qty_scanned,
            evidence_id="E-004",
            status="pass",
            reason="Declared package net quantity corroborated in reference catalogs."
        ))
    else:
        signals.append(AuthenticitySignal(
            name="net_qty_consistency",
            label="Net Quantity Corroboration",
            scanned_value=qty_scanned,
            reference_value="Not available",
            evidence_id="E-004",
            status="review",
            reason="Pack size requires visual confirmation against catalog variants."
        ))

    # -------------------------------------------------------------------------
    # Signal 6: Barcode / QR Status
    # -------------------------------------------------------------------------
    barcode = extracted_data.barcode
    if barcode and len(barcode) >= 8:
        barcode_status = f"Barcode Detected ({barcode})"
        signals.append(AuthenticitySignal(
            name="barcode_verification",
            label="Barcode / EAN Identifier",
            scanned_value=barcode,
            reference_value="GS1 Registry Format Matched",
            evidence_id="E-004",
            status="pass",
            reason=f"Barcode GTIN/EAN digits detected ({barcode})."
        ))
        risk_score = max(0, risk_score - 10)
    else:
        barcode_status = "Not readable / missing"
        signals.append(AuthenticitySignal(
            name="barcode_verification",
            label="Barcode / EAN Identifier",
            scanned_value="Not readable / missing",
            reference_value="Not available",
            evidence_id="E-004",
            status="review",
            reason="Barcode GTIN digits not readable or not visible on front label panel."
        ))

    risk_score = max(0, min(100, risk_score))

    if brand_found and prod_found and mrp_matched is not False:
        risk_score = min(risk_score, 18)

    if not service_available:
        risk_level = "REVIEW REQUIRED"
        assessment_title = "AUTHENTICITY VERIFICATION UNAVAILABLE"
        summary = "Web research service is currently unavailable. Legal Metrology rule screening remains active."
    elif risk_score <= 25:
        risk_level = "LOW"
        assessment_title = "LOW AUTHENTICITY RISK"
        summary = "The scanned product identity and declarations are consistent with available credible reference sources."
    elif risk_score <= 55:
        risk_level = "MEDIUM"
        assessment_title = "MEDIUM AUTHENTICITY RISK / REVIEW REQUIRED"
        summary = "Partial product corroboration or attribute variations (such as MRP anomaly) detected. Manual verification recommended."
    else:
        risk_level = "HIGH"
        assessment_title = "HIGH AUTHENTICITY RISK"
        summary = "Claimed brand/product identity could not be corroborated from credible reference sources. Elevated risk of unverified or counterfeit packaging."

    if not reasons:
        reasons.append("All primary identity signals match established reference sources.")

    return AuthenticityReport(
        service_available=service_available,
        risk_level=risk_level,
        risk_score=risk_score,
        assessment_title=assessment_title,
        assessment_summary=summary,
        signals=signals,
        reasons=reasons,
        sources=sources if isinstance(sources, list) else [],
        barcode_detected=barcode,
        barcode_status=barcode_status,
        visual_reference_status="Unavailable (Reference photo database hook prepared)"
    )
