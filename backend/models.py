"""
LegalMetriX Data Models
Structured data contracts for Extraction, Compliance Results, Authenticity Signals, and Inspection Reports.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BoundingRegion(BaseModel):
    label: str = Field(..., description="Label of the detected region e.g. MRP, Net Quantity")
    text: str = Field(default="", description="Text found in this region")
    x: Optional[float] = Field(default=None, description="X coordinate or percentage")
    y: Optional[float] = Field(default=None, description="Y coordinate or percentage")
    width: Optional[float] = Field(default=None, description="Width coordinate or percentage")
    height: Optional[float] = Field(default=None, description="Height coordinate or percentage")
    approx_pixel_height: Optional[int] = Field(default=None, description="Estimated pixel height of text")


class NutrientItem(BaseModel):
    name: str = Field(..., description="Nutrient name e.g. Energy, Protein, Carbohydrates, Added Sugars, Saturated Fat, Sodium")
    value: str = Field(..., description="Nutrient value with unit e.g. 480 kcal, 7.5 g, 320 mg")
    per_unit: str = Field(default="per 100g", description="Unit basis e.g. per 100g, per 100ml, per serving (30g)")
    daily_value_percent: Optional[str] = Field(default=None, description="Percentage of Recommended Daily Allowance (RDA) e.g. 15%")
    indicator_level: str = Field(default="NORMAL", description="'LOW', 'MODERATE', 'HIGH', or 'NORMAL' (FSSAI guideline classification)")


class NutritionInfo(BaseModel):
    is_food_product: bool = Field(default=True, description="False if cosmetic/cleaning/hardware commodity where nutrition does not apply")
    serving_size: Optional[str] = Field(default="100 g", description="Declared serving size e.g. 30 g, 100 g")
    servings_per_container: Optional[str] = Field(default=None, description="Number of servings per pack")
    items: List[NutrientItem] = Field(default_factory=list)
    has_nutrition_table: bool = Field(default=True)
    summary_verdict: Optional[str] = Field(default=None, description="e.g. Balanced Macronutrients, High Added Sugar Warning")
    highlights: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="Nutritional values extracted from package declaration. Final dietary assessments require verified laboratory batch analysis."
    )


class ExtractedProductData(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    packer: Optional[str] = None
    importer: Optional[str] = None
    country_of_origin: Optional[str] = None
    generic_name: Optional[str] = None
    net_quantity: Optional[str] = None
    mrp: Optional[str] = None
    manufacturing_date: Optional[str] = None
    packing_date: Optional[str] = None
    import_date: Optional[str] = None
    best_before: Optional[str] = None
    expiry_date: Optional[str] = None
    consumer_care: Optional[str] = None
    unit_sale_price: Optional[str] = None
    batch_number: Optional[str] = None
    barcode: Optional[str] = None
    ingredients: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    certification_marks: List[str] = Field(default_factory=list)
    other_visible_text: List[str] = Field(default_factory=list)
    regions: List[BoundingRegion] = Field(default_factory=list)
    nutrition: Optional["NutritionInfo"] = None
    raw_response: Optional[str] = None


class ComplianceCheckResult(BaseModel):
    finding_id: Optional[str] = Field(default=None, description="Unique finding ID e.g. LM-001")
    field_name: str
    status: str = Field(..., description="'pass', 'fail', 'review', 'missing', 'non_standard', or 'potentially_misleading'")
    classification: str = Field(default="standard", description="'compliant', 'missing_declaration', 'non_standard_format', 'potentially_misleading', 'uncertain_extraction', 'role_ambiguity'")
    ocr_status: str = Field(default="detected", description="'detected', 'uncertain', or 'not_detected'")
    raw_ocr: Optional[str] = Field(default=None, description="Raw unnormalized OCR text if different")
    detected_value: Optional[str] = None
    expected: str
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    rule_reference: str
    reason: str
    evidence: Optional[str] = None
    evidence_id: Optional[str] = Field(default=None, description="Associated evidence ID e.g. E-002")
    severity: str = "high"

    mandatory: bool = True


class ReadabilityAnalysisResult(BaseModel):
    status: str = Field(..., description="'pass', 'review', or 'fail'")
    image_resolution: str
    sharpness_score: float
    contrast_assessment: str
    glare_detected: bool = False
    ocr_confidence_score: float = 0.88
    estimated_text_height_px: Optional[int] = None
    region_text_heights: Dict[str, str] = Field(default_factory=dict)
    physical_scale_calibrated: bool = False
    physical_font_size_note: str = "Physical font-size verification: NOT CALIBRATED (requires physical scale/ruler reference; displaying pixel text height)."
    summary: str


class PlacementAnalysisResult(BaseModel):
    status: str = Field(default="pass", description="'pass', 'review'")
    pdp_detected: bool = True
    regions_detected_count: int = 0
    summary: str = "Placement detected on visible display panel."
    details: List[str] = Field(default_factory=list)


class SafetyIndicatorResult(BaseModel):
    status: str = "Safety indicators detected"
    expiry_or_best_before: Optional[str] = None
    warnings_found: List[str] = Field(default_factory=list)
    certifications_found: List[str] = Field(default_factory=list)
    ingredients_present: bool = False
    disclaimer: str = "Safety indicators extracted from label declarations. A photograph cannot verify laboratory or chemical safety."


class WebSourceEvidence(BaseModel):
    title: str = Field(..., description="Title of the web source or reference site")
    publisher_domain: Optional[str] = Field(default=None, description="Publisher / domain e.g. tooyumm.com")
    url: Optional[str] = Field(default=None, description="URL of the web source if available")
    source_type: str = Field(default="OTHER", description="'OFFICIAL', 'RETAILER', 'NEWS', or 'OTHER'")
    snippet: str = Field(default="", description="Relevant snippet or matched summary")
    matched_attributes: List[str] = Field(default_factory=list, description="Attributes confirmed e.g. brand, product, mrp, net_qty")
    retrieved_info: Dict[str, str] = Field(default_factory=dict, description="Retrieved attribute key-values")


class AuthenticitySignal(BaseModel):
    name: str = Field(..., description="Signal key e.g. brand_corroboration, product_corroboration")
    label: str = Field(..., description="Display label e.g. Brand Corroboration")
    scanned_value: Optional[str] = Field(default=None, description="Extracted value from package")
    reference_value: Optional[str] = Field(default=None, description="Reference value from official/web catalog")
    evidence_id: Optional[str] = Field(default=None, description="Associated evidence ID e.g. E-004")
    status: str = Field(..., description="'pass', 'fail', or 'review'")
    reason: str = Field(..., description="Explanation for signal status")


class AuthenticityReport(BaseModel):
    service_available: bool = Field(default=True, description="False if web verification service failed/unavailable")
    risk_level: str = Field(..., description="'LOW', 'MEDIUM', 'HIGH', or 'REVIEW REQUIRED'")
    risk_score: int = Field(..., ge=0, le=100, description="Authenticity Risk Score (0-100), higher = more suspicious")
    assessment_title: str = Field(..., description="Assessment header e.g. LOW AUTHENTICITY RISK")
    assessment_summary: str = Field(..., description="Summary narrative explaining risk rating")
    signals: List[AuthenticitySignal] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    sources: List[WebSourceEvidence] = Field(default_factory=list)
    barcode_detected: Optional[str] = Field(default=None)
    barcode_status: str = Field(default="Not detected")
    visual_reference_status: str = Field(default="Unavailable")
    disclaimer: str = Field(
        default="LegalMetriX evaluates web corroboration signals and packaging consistency. It does NOT provide laboratory certification or 100% legal counterfeit determination."
    )


class AlternateProduct(BaseModel):
    name: str = Field(..., description="Alternative product title e.g. Parle Hide & Seek Chocolate Chip Cookies")
    brand: str = Field(..., description="Brand of alternative e.g. Parle, ITC Sunfeast, Britannia")
    category: Optional[str] = Field(default=None, description="Category e.g. Biscuits / Cookies, Snacks, Shampoos")
    net_quantity: Optional[str] = Field(default=None, description="Pack size e.g. 120 g, 200 g")
    estimated_mrp: Optional[str] = Field(default=None, description="Reference retail price e.g. ₹30.00")
    unit_price: Optional[str] = Field(default=None, description="Unit rate e.g. ₹0.25 / g")
    similarity_type: str = Field(default="Direct Market Competitor", description="'Direct Market Competitor', 'Healthier Alternative', 'Economy / Value Pack', 'Brand Line Variant'")
    highlights: List[str] = Field(default_factory=list, description="Key features e.g. ['Zero Palm Oil', 'Lower Sugar', 'FSSAI Verified']")
    source_retailer: Optional[str] = Field(default="Blinkit / Zepto / BigBasket", description="Marketplace availability")
    source_url: Optional[str] = Field(default=None, description="Link or search URL")
    compliance_confidence: str = Field(default="High (Established Market Standard)", description="Standard packaging compliance status")


class DualPanelCoherenceResult(BaseModel):
    is_dual_panel: bool = Field(default=False, description="True if front and back panels were provided")
    is_coherent: bool = Field(default=True, description="True if panels belong to the same commodity")
    is_matching: bool = Field(default=True, description="Alias for is_coherent")
    status: str = Field(default="PASS", description="'PASS', 'WARNING', 'MISMATCH_REJECTED'")
    coherence_score: int = Field(default=100, ge=0, le=100, description="Coherence score (0-100)")
    verdict_title: str = Field(default="CROSS-PANEL COHERENCE VERIFIED")
    verdict_summary: str = Field(default="Front PDP and Back Info panels correspond to the same physical product.")
    brand_match: bool = Field(default=True)
    category_match: bool = Field(default=True)
    discrepancies: List[str] = Field(default_factory=list)
    front_image_filename: Optional[str] = None
    back_image_filename: Optional[str] = None


class InspectionReport(BaseModel):
    inspection_id: str
    timestamp: str
    image_filename: str
    automated_screening_score: int
    overall_status: str  # "PRELIMINARY PASS", "REVIEW REQUIRED", "FAIL / DEFICIENCIES DETECTED"
    passed_checks: int
    total_applicable_checks: int
    review_checks: int
    failed_checks: int
    compliance_checks: List[ComplianceCheckResult]
    extracted_data: ExtractedProductData
    readability: ReadabilityAnalysisResult
    placement: PlacementAnalysisResult
    safety: SafetyIndicatorResult
    authenticity: AuthenticityReport
    nutrition: Optional[NutritionInfo] = None
    alternate_products: List[AlternateProduct] = Field(default_factory=list)
    coherence: Optional[DualPanelCoherenceResult] = None
    regulatory_disclaimer: str = (
        "This report is an AI-assisted preliminary screening generated from the supplied image and available reference information. "
        "It is not an official Government of India document, legal certificate, final determination of compliance, product safety certificate, "
        "or definitive proof of authenticity/counterfeiting. Final assessment and enforcement decisions must be made by the competent authority."
    )


