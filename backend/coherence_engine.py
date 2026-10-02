"""
LegalMetriX Cross-Panel Coherence Engine
Guards against fraudulent or accidental multi-image pairing where a user uploads panels
from two different packaged commodities (e.g. Front of Brand A + Back of Brand B).
Evaluates brand consistency, commodity category alignment, pack size agreement, and visual packaging harmony.
"""

import os
import re
from typing import Tuple, List, Optional
import cv2
import numpy as np

from backend.models import ExtractedProductData, DualPanelCoherenceResult, BoundingRegion
from backend.nutrition_service import is_non_food_commodity


def normalize_token_set(text: Optional[str]) -> set:
    """Extracts alphanumeric lowercase word tokens from text."""
    if not text:
        return set()
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    stop_words = {"pvt", "ltd", "limited", "and", "the", "for", "with", "india", "net", "qty", "mrp", "rs", "in"}
    return {w for w in cleaned.split() if len(w) > 1 and w not in stop_words}


def compare_image_color_histograms(img_path_a: str, img_path_b: str) -> float:
    """
    Computes OpenCV HSV color histogram correlation between two package images.
    Returns correlation score (-1.0 to 1.0, higher = more similar dominant color palette).
    """
    try:
        if not os.path.exists(img_path_a) or not os.path.exists(img_path_b):
            return 0.5
        
        img_a = cv2.imread(img_path_a)
        img_b = cv2.imread(img_path_b)
        if img_a is None or img_b is None:
            return 0.5

        hsv_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2HSV)
        hsv_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2HSV)

        hist_a = cv2.calcHist([hsv_a], [0, 1], None, [30, 32], [0, 180, 0, 256])
        hist_b = cv2.calcHist([hsv_b], [0, 1], None, [30, 32], [0, 180, 0, 256])

        cv2.normalize(hist_a, hist_a, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist_b, hist_b, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        correlation = cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)
        return float(correlation)
    except Exception:
        return 0.5


def evaluate_dual_panel_coherence(
    front_data: ExtractedProductData,
    back_data: ExtractedProductData,
    front_img_filename: Optional[str] = None,
    back_img_filename: Optional[str] = None,
    front_img_path: Optional[str] = None,
    back_img_path: Optional[str] = None
) -> DualPanelCoherenceResult:
    """
    Evaluates whether two uploaded panels (Front PDP and Back Info panel) belong
    to the same physical packaged commodity or represent conflicting products.
    """
    coherence_score = 100
    discrepancies: List[str] = []
    brand_match = True
    category_match = True

    front_brand = (front_data.brand or "").strip()
    back_brand = (back_data.brand or "").strip()
    back_mfg = (back_data.manufacturer or "").strip()
    back_care = (back_data.consumer_care or "").strip()

    # 1. Brand Alignment Cross-Check
    if front_brand:
        f_tokens = normalize_token_set(front_brand)
        back_corpus = f"{back_brand} {back_mfg} {back_care} {' '.join(back_data.other_visible_text or [])}".lower()
        
        has_brand_overlap = any(tok in back_corpus for tok in f_tokens)
        
        # Check if back explicitly identifies a DIFFERENT prominent brand
        if back_brand and back_brand.lower() != front_brand.lower():
            b_tokens = normalize_token_set(back_brand)
            # If completely disjoint brand names
            if not (f_tokens & b_tokens):
                brand_match = False
                coherence_score -= 50
                discrepancies.append(
                    f"Brand Conflict: Front panel displays brand '{front_brand}', but back panel identifies brand '{back_brand}'."
                )
        elif not has_brand_overlap and len(f_tokens) > 0 and len(back_mfg) > 5:
            # Front brand not found anywhere in back manufacturer / consumer care
            brand_match = False
            coherence_score -= 35
            discrepancies.append(
                f"Entity Divergence: Claimed front brand '{front_brand}' is not corroborated anywhere in back panel manufacturer or care declarations."
            )

    # 2. Commodity Category Cross-Check (Food vs Non-Food & Variant)
    front_is_non_food = is_non_food_commodity(front_data.product_name, front_data.generic_name, front_data.brand)
    back_is_non_food = is_non_food_commodity(back_data.product_name, back_data.generic_name, back_data.brand)

    if front_is_non_food != back_is_non_food:
        category_match = False
        coherence_score -= 55
        front_type = "Cosmetic / Personal Care" if front_is_non_food else "Edible Packaged Food"
        back_type = "Cosmetic / Personal Care" if back_is_non_food else "Edible Packaged Food"
        discrepancies.append(
            f"Critical Category Mismatch: Front panel represents {front_type}, while back panel corresponds to {back_type}."
        )

    # 3. Product Variant / Title Overlap
    f_pname_tokens = normalize_token_set(front_data.product_name)
    b_pname_tokens = normalize_token_set(f"{back_data.product_name or ''} {back_data.generic_name or ''}")

    if f_pname_tokens and b_pname_tokens:
        overlap = f_pname_tokens & b_pname_tokens
        # If both panels give full titles but share zero descriptive tokens (ignoring brand)
        if not overlap and len(f_pname_tokens) >= 2 and len(b_pname_tokens) >= 2:
            coherence_score -= 20
            discrepancies.append(
                f"Variant Divergence: Front title '{front_data.product_name}' does not share descriptive keywords with back title '{back_data.product_name or back_data.generic_name}'."
            )

    # 4. Net Quantity Agreement
    if front_data.net_quantity and back_data.net_quantity:
        f_qty = re.sub(r"[^0-9a-zA-Z]", "", front_data.net_quantity.lower())
        b_qty = re.sub(r"[^0-9a-zA-Z]", "", back_data.net_quantity.lower())
        if f_qty and b_qty and f_qty != b_qty:
            coherence_score -= 20
            discrepancies.append(
                f"Pack Size Mismatch: Front panel specifies net content '{front_data.net_quantity}', but back panel declares '{back_data.net_quantity}'."
            )

    # 5. Visual Palette Similarity (OpenCV)
    if front_img_path and back_img_path:
        color_sim = compare_image_color_histograms(front_img_path, back_img_path)
        if color_sim < 0.05:  # Radically contrasting packaging palettes
            coherence_score -= 10
            discrepancies.append(
                "Packaging Material / Color Divergence: Dominant color palette difference detected between panels."
            )

    # Final Score Bounds
    coherence_score = max(0, min(100, coherence_score))

    if coherence_score < 50:
        status = "MISMATCH_REJECTED"
        title = "CROSS-PANEL MISMATCH REJECTED"
        summary = (
            f"The uploaded Front and Back images do not belong to the same product. "
            f"Found {len(discrepancies)} critical conflict(s). Inspection aborted to prevent cross-product fraud."
        )
    elif coherence_score < 75:
        status = "WARNING"
        title = "BORDERLINE CROSS-PANEL COHERENCE"
        summary = (
            "Partial alignment detected between Front PDP and Back panels. "
            "Manual officer review recommended to verify packaging continuity."
        )
    else:
        status = "PASS"
        title = "DUAL-PANEL COHERENCE VERIFIED"
        summary = "Front PDP and Back Info panels corroborated as matching components of the same packaged commodity."

    is_ok = (status != "MISMATCH_REJECTED")
    return DualPanelCoherenceResult(
        is_dual_panel=True,
        is_coherent=is_ok,
        is_matching=is_ok,
        status=status,
        coherence_score=coherence_score,
        verdict_title=title,
        verdict_summary=summary,
        brand_match=brand_match,
        category_match=category_match,
        discrepancies=discrepancies,
        front_image_filename=front_img_filename,
        back_image_filename=back_img_filename
    )


def merge_dual_panel_declarations(
    front_data: ExtractedProductData,
    back_data: ExtractedProductData
) -> ExtractedProductData:
    """
    Intelligently merges front PDP declarations (Brand, Product Name, Net Qty)
    with back panel statutory declarations (MRP, Mfg, Dates, Consumer Care, Ingredients, Nutrition).
    """
    # Front PDP is primary for brand, product name, and net quantity
    # Back panel is primary for statutory metrology details
    merged_regions = []
    for r in front_data.regions:
        merged_regions.append(BoundingRegion(
            label=f"[Front PDP] {r.label}",
            text=r.text,
            x=r.x,
            y=r.y,
            width=r.width,
            height=r.height,
            approx_pixel_height=r.approx_pixel_height
        ))
    for r in back_data.regions:
        merged_regions.append(BoundingRegion(
            label=f"[Back Panel] {r.label}",
            text=r.text,
            x=r.x,
            y=r.y,
            width=r.width,
            height=r.height,
            approx_pixel_height=r.approx_pixel_height
        ))

    all_warnings = list(dict.fromkeys((front_data.warnings or []) + (back_data.warnings or [])))
    all_certs = list(dict.fromkeys((front_data.certification_marks or []) + (back_data.certification_marks or [])))
    all_visible = list(dict.fromkeys((front_data.other_visible_text or []) + (back_data.other_visible_text or [])))

    return ExtractedProductData(
        product_name=front_data.product_name or back_data.product_name,
        brand=front_data.brand or back_data.brand,
        generic_name=front_data.generic_name or back_data.generic_name,
        net_quantity=front_data.net_quantity or back_data.net_quantity,
        mrp=back_data.mrp or front_data.mrp,
        unit_sale_price=back_data.unit_sale_price or front_data.unit_sale_price,
        manufacturer=back_data.manufacturer or front_data.manufacturer,
        packer=back_data.packer or front_data.packer,
        importer=back_data.importer or front_data.importer,
        country_of_origin=back_data.country_of_origin or front_data.country_of_origin,
        manufacturing_date=back_data.manufacturing_date or front_data.manufacturing_date,
        packing_date=back_data.packing_date or front_data.packing_date,
        import_date=back_data.import_date or front_data.import_date,
        best_before=back_data.best_before or front_data.best_before,
        expiry_date=back_data.expiry_date or front_data.expiry_date,
        consumer_care=back_data.consumer_care or front_data.consumer_care,
        batch_number=back_data.batch_number or front_data.batch_number,
        barcode=back_data.barcode or front_data.barcode,
        ingredients=back_data.ingredients or front_data.ingredients,
        warnings=all_warnings,
        certification_marks=all_certs,
        other_visible_text=all_visible,
        regions=merged_regions,
        nutrition=back_data.nutrition or front_data.nutrition,
        raw_response=(
            f"=== FRONT PDP EXTRACTION ===\n{front_data.raw_response or ''}\n\n"
            f"=== BACK INFO PANEL EXTRACTION ===\n{back_data.raw_response or ''}"
        )
    )
