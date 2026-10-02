"""
LegalMetriX Sample & Demo Data
Provides pre-calibrated sample packages for Phase 1 (Legal Metrology), Phase 2 (Authenticity Risk),
and Phase 3 (Nutritional Profiling & Market Alternative Products).
"""

from typing import Dict, Any
from backend.models import (
    ExtractedProductData,
    BoundingRegion,
    AuthenticityReport,
    AuthenticitySignal,
    WebSourceEvidence,
    NutritionInfo,
    NutrientItem,
    AlternateProduct,
    DualPanelCoherenceResult
)

SAMPLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "biscuit_compliant": {
        "name": "Britannia Treat Butter Cookies (Genuine - Low Risk)",
        "filename": "sample_cookies.jpg",
        "description": "Genuine packaged food commodity. 100% Legal Metrology Pass + LOW Authenticity Risk.",
        "extracted_data": ExtractedProductData(
            product_name="Britannia Treat Butter Cookies",
            brand="Britannia",
            generic_name="Biscuits / Bakery Product",
            manufacturer="Britannia Industries Ltd., 5/1A Hungerford Street, Kolkata - 700017, West Bengal, India. Mfg at: Plot 12, Ind Area, Bidadi, Bangalore - 562109",
            packer=None,
            importer=None,
            country_of_origin="India",
            net_quantity="120 g",
            mrp="MRP ₹ 30.00 (Incl. of all taxes)",
            manufacturing_date="04/2026",
            best_before="6 Months from Manufacture",
            expiry_date="10/2026",
            consumer_care="Toll Free: 1800-425-4444 | Email: feedback@britannia.co.in | Address: Britannia Consumer Care, Bangalore - 562109",
            unit_sale_price="₹ 0.25 / g",
            batch_number="BAT-2026-X81",
            barcode="8901063012345",
            ingredients="Refined Wheat Flour (Maida), Sugar, Butter (14%), Edible Vegetable Oil (Palm), Milk Solids, Invert Sugar Syrup, Raising Agents (500(ii), 503(ii)), Iodised Salt, Emulsifier (322).",
            warnings=["Contains Wheat (Gluten), Milk and Soya.", "May contain traces of Nuts."],
            certification_marks=["FSSAI Lic. No. 10015043001129", "100% Vegetarian (Green Dot Logo)"],
            other_visible_text=["Rich in Butter Taste", "Crunchy & Golden Baked", "Store in a cool, dry and hygienic place."],
            regions=[
                BoundingRegion(label="Product Name", text="Britannia Treat Butter Cookies", x=5.0, y=3.0, width=88.0, height=9.0, approx_pixel_height=42),
                BoundingRegion(label="Ingredients", text="Ingredients: Refined Wheat Flour, Butter (14%), Sugar, Milk Solids, Salt", x=6.0, y=26.0, width=42.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="Warnings", text="Allergen Warning: Contains Wheat (Gluten), Milk. May contain Nuts.", x=6.0, y=33.0, width=40.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="Certification & Batch", text="FSSAI Lic. No. 10015043001129 | Batch No: BAT-2026-X81", x=6.0, y=40.0, width=34.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="Net Quantity", text="Net Quantity: 120 g", x=6.0, y=69.0, width=15.0, height=4.0, approx_pixel_height=26),
                BoundingRegion(label="MRP", text="MRP: Rs. 30.00 (Incl. of all taxes)", x=56.0, y=69.0, width=22.0, height=4.0, approx_pixel_height=28),
                BoundingRegion(label="Unit Sale Price", text="Unit Sale Price (USP): Rs 0.25 / g", x=6.0, y=75.0, width=20.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="Mfg Date", text="Mfg Date: 04/2026", x=56.0, y=75.0, width=15.0, height=4.0, approx_pixel_height=22),
                BoundingRegion(label="Manufacturer", text="Mfg & Packed by: Britannia Industries Ltd., Plot 12, Ind Area, Bangalore - 562109", x=6.0, y=81.0, width=45.0, height=4.0, approx_pixel_height=18),
                BoundingRegion(label="Consumer Care", text="Consumer Care: Toll-Free 1800-425-4444 | Email: feedback@britannia.co.in", x=6.0, y=86.0, width=44.0, height=4.0, approx_pixel_height=18)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="LOW",
            risk_score=10,
            assessment_title="LOW AUTHENTICITY RISK",
            assessment_summary="The scanned product identity (Britannia Treat Butter Cookies) is corroborated by official brand and retail registry records.",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="Britannia", reference_value="Britannia", evidence_id="E-004", status="pass", reason="Claimed brand 'Britannia' corroborated by official brand website."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="Treat Butter Cookies", reference_value="Treat Butter Cookies 120g", evidence_id="E-004", status="pass", reason="Product variant 'Treat Butter Cookies' confirmed in official catalog."),
                AuthenticitySignal(name="manufacturer_consistency", label="Manufacturer Identity Match", scanned_value="Britannia Industries Ltd", reference_value="Britannia Industries Ltd", evidence_id="E-004", status="pass", reason="Declared manufacturer 'Britannia Industries Ltd' matches brand entity."),
                AuthenticitySignal(name="mrp_consistency", label="MRP / Price Consistency", scanned_value="MRP ₹ 30.00", reference_value="₹ 30.00", evidence_id="E-004", status="pass", reason="Extracted MRP (₹30.00) matches standard reference pricing."),
                AuthenticitySignal(name="barcode_verification", label="Barcode / EAN Identifier", scanned_value="8901063012345", reference_value="GS1 Matched", evidence_id="E-004", status="pass", reason="Barcode GTIN digits detected (8901063012345).")
            ],
            reasons=["All primary identity signals match established reference sources."],
            sources=[
                WebSourceEvidence(title="Official Britannia Consumer Products Catalog", publisher_domain="britannia.co.in", url="https://britannia.co.in/products", source_type="OFFICIAL", snippet="Official product listing for Britannia Treat Butter Cookies 120g.", matched_attributes=["brand", "product", "manufacturer"], retrieved_info={"Brand": "Britannia", "Product": "Treat Butter Cookies", "Net Qty": "120 g"}),
                WebSourceEvidence(title="Major Indian E-Commerce Grocery Registry", publisher_domain="bigbasket.com", url="https://www.bigbasket.com/pd/britannia-treat-cookies", source_type="RETAILER", snippet="Britannia Treat Butter Cookies 120g - MRP ₹30.", matched_attributes=["brand", "product", "mrp", "net_quantity"], retrieved_info={"Brand": "Britannia", "Product": "Treat Butter Cookies", "MRP": "₹30.00"})
            ],
            barcode_detected="8901063012345",
            barcode_status="Barcode Detected (8901063012345)"
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=True,
            has_nutrition_table=True,
            serving_size="30 g (approx. 4 cookies)",
            servings_per_container="4 servings",
            summary_verdict="Bakery Commodity - High Added Sugar & Saturated Fat",
            highlights=[
                "Contains 14% Real Butter",
                "Zero Trans Fat (0.0g)",
                "High Added Sugars (22.0g / 100g - Caution)",
                "Allergen: Contains Wheat Gluten and Milk Solids"
            ],
            items=[
                NutrientItem(name="Energy", value="492 kcal", per_unit="per 100g", daily_value_percent="24.6%", indicator_level="HIGH"),
                NutrientItem(name="Protein", value="6.8 g", per_unit="per 100g", daily_value_percent="12.5%", indicator_level="NORMAL"),
                NutrientItem(name="Carbohydrates", value="68.0 g", per_unit="per 100g", daily_value_percent="23.0%", indicator_level="NORMAL"),
                NutrientItem(name="Total Sugars", value="24.5 g", per_unit="per 100g", daily_value_percent="49.0%", indicator_level="HIGH"),
                NutrientItem(name="Added Sugars", value="22.0 g", per_unit="per 100g", daily_value_percent="44.0%", indicator_level="HIGH"),
                NutrientItem(name="Total Fat", value="21.0 g", per_unit="per 100g", daily_value_percent="31.3%", indicator_level="MODERATE"),
                NutrientItem(name="Saturated Fat", value="9.8 g", per_unit="per 100g", daily_value_percent="44.5%", indicator_level="HIGH"),
                NutrientItem(name="Trans Fat", value="0.0 g", per_unit="per 100g", daily_value_percent="0%", indicator_level="LOW"),
                NutrientItem(name="Dietary Fiber", value="2.4 g", per_unit="per 100g", daily_value_percent="8.0%", indicator_level="NORMAL"),
                NutrientItem(name="Sodium", value="310 mg", per_unit="per 100g", daily_value_percent="15.5%", indicator_level="MODERATE")
            ]
        ),
        "preset_alternates": [
            AlternateProduct(
                name="Parle 20-20 Butter Cookies",
                brand="Parle",
                category="Biscuits / Cookies",
                net_quantity="120 g",
                estimated_mrp="₹ 30.00",
                unit_price="₹ 0.25 / g",
                similarity_type="Economy / Value Pack",
                highlights=["Cost-Effective Unit Rate", "Traditional Crispy Butter Taste", "FSSAI Certified"],
                source_retailer="Blinkit / Zepto",
                source_url="https://www.blinkit.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Sunfeast Mom's Magic Butter & Cashew",
                brand="ITC Sunfeast",
                category="Biscuits / Cookies",
                net_quantity="120 g",
                estimated_mrp="₹ 35.00",
                unit_price="₹ 0.29 / g",
                similarity_type="Direct Market Competitor",
                highlights=["Enriched with Real Butter & Cashews", "Widely Available on Quick Commerce", "Full Legal Metrology Declarations"],
                source_retailer="Zepto / Instamart",
                source_url="https://www.zeptonow.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Britannia NutriChoice Digestive High Fibre",
                brand="Britannia",
                category="Health / High Fibre Biscuits",
                net_quantity="100 g",
                estimated_mrp="₹ 30.00",
                unit_price="₹ 0.30 / g",
                similarity_type="Healthier Alternative",
                highlights=["Zero Trans Fat", "High Dietary Fibre (5.5g)", "No Refined Wheat Flour Claim"],
                source_retailer="BigBasket / Blinkit",
                source_url="https://www.bigbasket.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Unibic Butter Cookies Pack",
                brand="Unibic",
                category="Premium Bakery Cookies",
                net_quantity="150 g",
                estimated_mrp="₹ 45.00",
                unit_price="₹ 0.30 / g",
                similarity_type="Brand Line Variant",
                highlights=["Traditional Wire-Cut Cookie", "Rich 15% Butter Recipe", "FSSAI Grade A"],
                source_retailer="Amazon.in / Zepto",
                source_url="https://www.amazon.in",
                compliance_confidence="High (Registered Standard Brand)"
            )
        ]
    },
    "synthetic_fake": {
        "name": "Too Yumms All In One (Fake Brand - High Risk)",
        "filename": "sample_fake_tooyumms.jpg",
        "description": "Synthetic/fake test case: Nonexistent brand 'Too Yumms' imitating 'Too Yumm!'. HIGH Authenticity Risk.",
        "extracted_data": ExtractedProductData(
            product_name="All In One Spicy Mixture",
            brand="Too Yumms",
            generic_name="Namkeen / Snack Food",
            manufacturer="Unverified Local Packers, MIDC, Pune",
            packer=None,
            importer=None,
            country_of_origin="India",
            net_quantity="200 g",
            mrp="MRP ₹ 65.00 (Incl. of all taxes)",
            manufacturing_date="05/2026",
            best_before="4 Months",
            consumer_care="Call Helpline: 9999900000",
            unit_sale_price=None,
            batch_number="FAKE-001",
            barcode="8909999999999",
            ingredients="Gram flour, Edible vegetable oil, Peanuts, Spices.",
            warnings=["Contains Peanuts."],
            certification_marks=["Fake FSSAI Lic. 99999999999999"],
            other_visible_text=["Extra Spicy Super Crunch"],
            regions=[
                BoundingRegion(label="Product Name", text="Too Yumms All In One Spicy Mixture", x=5.0, y=3.0, width=88.0, height=9.0, approx_pixel_height=40),
                BoundingRegion(label="Manufacturer", text="Unverified Local Packers, MIDC, Pune", x=6.0, y=26.0, width=35.0, height=5.0, approx_pixel_height=20),
                BoundingRegion(label="Net Quantity", text="Net Qty: 200 g", x=6.0, y=72.0, width=15.0, height=4.0, approx_pixel_height=26),
                BoundingRegion(label="MRP", text="MRP ₹ 65.00", x=56.0, y=72.0, width=22.0, height=4.0, approx_pixel_height=28)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="HIGH",
            risk_score=88,
            assessment_title="HIGH AUTHENTICITY RISK",
            assessment_summary="Claimed brand 'Too Yumms' could not be corroborated from available credible web sources. High risk of unverified or imitation brand packaging.",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="Too Yumms", reference_value="Not available", evidence_id="E-004", status="fail", reason="Claimed brand 'Too Yumms' could not be corroborated from credible official or retail sources."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="All In One Spicy Mixture", reference_value="Not available", evidence_id="E-004", status="fail", reason="No matching product line found for brand 'Too Yumms'."),
                AuthenticitySignal(name="manufacturer_consistency", label="Manufacturer Identity Match", scanned_value="Unverified Local Packers", reference_value="Not available", evidence_id="E-004", status="review", reason="Declared manufacturer 'Unverified Local Packers' is unverified."),
                AuthenticitySignal(name="mrp_consistency", label="MRP / Price Consistency", scanned_value="MRP ₹ 65.00", reference_value="Not available", evidence_id="E-004", status="review", reason="No reference price catalog exists for unverified brand."),
                AuthenticitySignal(name="barcode_verification", label="Barcode / EAN Identifier", scanned_value="8909999999999", reference_value="Not available", evidence_id="E-004", status="review", reason="Barcode GTIN digits (8909999999999) not found in official GS1 registry.")
            ],
            reasons=[
                "Claimed brand 'Too Yumms' could not be corroborated from available credible web sources.",
                "Matching product identity and manufacturer records could not be established.",
                "Manual physical and legal verification recommended before distribution."
            ],
            sources=[],
            barcode_detected="8909999999999",
            barcode_status="Unverified Barcode (8909999999999)"
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=True,
            has_nutrition_table=True,
            serving_size="30 g",
            servings_per_container="6-7 servings",
            summary_verdict="High Risk Savory Snack - Unverified Nutritional Declarations",
            highlights=[
                "High Sodium Warning (>850mg / 100g)",
                "High Saturated Fat (12.5g)",
                "Unverified FSSAI Nutritional Audit on Fake Pack"
            ],
            items=[
                NutrientItem(name="Energy", value="535 kcal", per_unit="per 100g", daily_value_percent="26.7%", indicator_level="HIGH"),
                NutrientItem(name="Protein", value="11.2 g", per_unit="per 100g", daily_value_percent="20.7%", indicator_level="NORMAL"),
                NutrientItem(name="Carbohydrates", value="46.0 g", per_unit="per 100g", daily_value_percent="15.3%", indicator_level="NORMAL"),
                NutrientItem(name="Total Sugars", value="3.5 g", per_unit="per 100g", daily_value_percent="7.0%", indicator_level="LOW"),
                NutrientItem(name="Total Fat", value="34.0 g", per_unit="per 100g", daily_value_percent="50.7%", indicator_level="HIGH"),
                NutrientItem(name="Saturated Fat", value="12.5 g", per_unit="per 100g", daily_value_percent="56.8%", indicator_level="HIGH"),
                NutrientItem(name="Trans Fat", value="0.2 g", per_unit="per 100g", daily_value_percent="1.0%", indicator_level="NORMAL"),
                NutrientItem(name="Sodium", value="880 mg", per_unit="per 100g", daily_value_percent="44.0%", indicator_level="HIGH")
            ]
        ),
        "preset_alternates": [
            AlternateProduct(
                name="Too Yumm! All In One Multigrain Snack",
                brand="Too Yumm! (Guiltfree)",
                category="Extruded Namkeen / Snack",
                net_quantity="200 g",
                estimated_mrp="₹ 65.00",
                unit_price="₹ 0.325 / g",
                similarity_type="Genuine Brand Benchmark",
                highlights=["100% Genuine Certified Brand", "Baked Not Fried (40% Less Fat)", "Zero Trans Fat", "Correct Retail MRP ₹65"],
                source_retailer="Blinkit / Zepto / BigBasket",
                source_url="https://www.blinkit.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Haldiram's All In One Mixture",
                brand="Haldiram's",
                category="Traditional Savory Namkeen",
                net_quantity="200 g",
                estimated_mrp="₹ 60.00",
                unit_price="₹ 0.30 / g",
                similarity_type="Direct Market Competitor",
                highlights=["Standard Category Leader", "Zero Added Preservatives", "Standard Legal Metrology Packaging"],
                source_retailer="Zepto / Blinkit / Amazon",
                source_url="https://www.zeptonow.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Bikaji All-In-One Kuch-Kuch Mixture",
                brand="Bikaji",
                category="Traditional Savory Namkeen",
                net_quantity="200 g",
                estimated_mrp="₹ 55.00",
                unit_price="₹ 0.275 / g",
                similarity_type="Economy / Value Pack",
                highlights=["Authentic Bikaneri Spices", "FSSAI Verified Manufacturing", "Cost-effective Unit Pricing"],
                source_retailer="BigBasket / JioMart",
                source_url="https://www.bigbasket.com",
                compliance_confidence="High (Registered Standard Brand)"
            )
        ]
    },
    "mrp_anomaly": {
        "name": "Too Yumm! All In One (MRP Anomaly - Elevated Risk)",
        "filename": "sample_mrp_anomaly.jpg",
        "description": "Genuine brand 'Too Yumm!' with an abnormal price tag (₹999 vs standard ₹65). Elevated MRP Anomaly Risk.",
        "extracted_data": ExtractedProductData(
            product_name="All In One Multigrain Snack",
            brand="Too Yumm!",
            generic_name="Extruded Snack Food",
            manufacturer="Guiltfree Industries Limited, 1st Floor, 31 Netaji Subhas Road, Kolkata - 700001",
            packer=None,
            importer=None,
            country_of_origin="India",
            net_quantity="200 g",
            mrp="MRP ₹ 999.00 (Incl. of all taxes)",
            manufacturing_date="05/2026",
            best_before="6 Months from Manufacture",
            consumer_care="Toll Free: 1800-309-3000 | feedback@tooyumm.com",
            unit_sale_price="₹ 5.00 / g",
            batch_number="TY-2026-M04",
            barcode="8906065123456",
            ingredients="Multigrain Flour (Rice, Corn, Wheat, Oats), Seasoning, Edible Oil.",
            warnings=["Contains Wheat."],
            certification_marks=["FSSAI Lic. No. 10017031002158", "Green Veg Dot"],
            other_visible_text=["Baked Not Fried", "40% Less Fat"],
            regions=[
                BoundingRegion(label="Product Name", text="TOO YUMM! ALL IN ONE MULTIGRAIN SNACK", x=5.0, y=3.0, width=88.0, height=9.0, approx_pixel_height=42),
                BoundingRegion(label="Other Visible Text", text="Baked Not Fried | 40% Less Fat", x=6.0, y=19.0, width=30.0, height=5.0, approx_pixel_height=20),
                BoundingRegion(label="Manufacturer", text="Guiltfree Industries Limited, Kolkata - 700001", x=6.0, y=26.0, width=32.0, height=5.0, approx_pixel_height=20),
                BoundingRegion(label="Certification & Batch", text="FSSAI Lic No. 10017031002158 | Batch: TY-2026-M04", x=6.0, y=33.0, width=35.0, height=5.0, approx_pixel_height=20),
                BoundingRegion(label="Net Quantity", text="Net Qty: 200 g", x=6.0, y=72.0, width=15.0, height=4.0, approx_pixel_height=24),
                BoundingRegion(label="Unit Sale Price", text="USP: ₹ 5.00 / g", x=6.0, y=79.0, width=12.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="Consumer Care", text="Consumer Care: 1800-309-3000 | feedback@tooyumm.com", x=6.0, y=86.0, width=36.0, height=4.0, approx_pixel_height=20),
                BoundingRegion(label="MRP Anomaly", text="MRP ₹ 999.00 (Incl. of all taxes)", x=56.0, y=72.0, width=22.0, height=4.0, approx_pixel_height=28),
                BoundingRegion(label="Mfg Date", text="Mfg Date: 05/2026", x=56.0, y=79.0, width=15.0, height=4.0, approx_pixel_height=22)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="MEDIUM",
            risk_score=48,
            assessment_title="MEDIUM AUTHENTICITY RISK / MRP ANOMALY",
            assessment_summary="Extracted brand 'Too Yumm!' is corroborated, but declared MRP (₹999.00) differs significantly from typical reference price points (₹65.00).",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="Too Yumm!", reference_value="Too Yumm!", evidence_id="E-004", status="pass", reason="Claimed brand 'Too Yumm!' corroborated by official website."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="All In One", reference_value="All In One 200g", evidence_id="E-004", status="pass", reason="Product 'All In One' confirmed in Too Yumm! product line."),
                AuthenticitySignal(name="manufacturer_consistency", label="Manufacturer Identity Match", scanned_value="Guiltfree Industries Limited", reference_value="Guiltfree Industries Limited", evidence_id="E-004", status="pass", reason="Manufacturer 'Guiltfree Industries Limited' matches official brand owner."),
                AuthenticitySignal(name="mrp_consistency", label="MRP / Price Consistency", scanned_value="MRP ₹ 999.00", reference_value="Standard Ref: ₹ 65.00", evidence_id="E-004", status="review", reason="MRP Anomaly: Declared price ₹999.00 is ~15x higher than standard reference retail price ₹65.00."),
                AuthenticitySignal(name="barcode_verification", label="Barcode / EAN Identifier", scanned_value="8906065123456", reference_value="GS1 Matched", evidence_id="E-004", status="pass", reason="Barcode GTIN digits detected (8906065123456).")
            ],
            reasons=[
                "MRP Anomaly: Package retail price (₹999.00) differs significantly from standard reference pricing (₹65.00).",
                "Requires manual verification to determine if pack size or special institutional edition applies."
            ],
            sources=[
                WebSourceEvidence(title="Official Too Yumm! Brand Page", publisher_domain="tooyumm.com", url="https://tooyumm.com", source_type="OFFICIAL", snippet="Too Yumm! All In One 200g - MRP ₹65.", matched_attributes=["brand", "product", "manufacturer"], retrieved_info={"Brand": "Too Yumm!", "Product": "All In One 200g", "MRP": "₹65.00"}),
                WebSourceEvidence(title="Blinkit Quick Commerce Listing", publisher_domain="blinkit.com", url="https://blinkit.com/prn/too-yumm-all-in-one/prid/3452", source_type="RETAILER", snippet="Too Yumm! All In One 200g Pack - ₹65.", matched_attributes=["brand", "product", "mrp"], retrieved_info={"Brand": "Too Yumm!", "Retail Price": "₹65.00"})
            ],
            barcode_detected="8906065123456",
            barcode_status="Barcode Detected (8906065123456)"
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=True,
            has_nutrition_table=True,
            serving_size="30 g",
            servings_per_container="6-7 servings",
            summary_verdict="Extruded Multigrain Snack - Baked Not Fried",
            highlights=[
                "Baked Not Fried Formulation (40% Less Fat)",
                "Zero Trans Fat (0.0g)",
                "Multigrain Blend (Rice, Corn, Wheat, Oats)",
                "Protects consumer from ₹999 MRP price gouge"
            ],
            items=[
                NutrientItem(name="Energy", value="460 kcal", per_unit="per 100g", daily_value_percent="23.0%", indicator_level="NORMAL"),
                NutrientItem(name="Protein", value="8.5 g", per_unit="per 100g", daily_value_percent="15.7%", indicator_level="NORMAL"),
                NutrientItem(name="Carbohydrates", value="65.0 g", per_unit="per 100g", daily_value_percent="21.6%", indicator_level="NORMAL"),
                NutrientItem(name="Total Sugars", value="4.5 g", per_unit="per 100g", daily_value_percent="9.0%", indicator_level="LOW"),
                NutrientItem(name="Total Fat", value="18.2 g", per_unit="per 100g", daily_value_percent="27.1%", indicator_level="MODERATE"),
                NutrientItem(name="Saturated Fat", value="3.5 g", per_unit="per 100g", daily_value_percent="15.9%", indicator_level="MODERATE"),
                NutrientItem(name="Trans Fat", value="0.0 g", per_unit="per 100g", daily_value_percent="0%", indicator_level="LOW"),
                NutrientItem(name="Dietary Fiber", value="4.8 g", per_unit="per 100g", daily_value_percent="16.0%", indicator_level="NORMAL"),
                NutrientItem(name="Sodium", value="540 mg", per_unit="per 100g", daily_value_percent="27.0%", indicator_level="MODERATE")
            ]
        ),
        "preset_alternates": [
            AlternateProduct(
                name="Too Yumm! All In One (Standard Retail Pack)",
                brand="Too Yumm!",
                category="Extruded Namkeen / Snack",
                net_quantity="200 g",
                estimated_mrp="₹ 65.00",
                unit_price="₹ 0.325 / g",
                similarity_type="Standard Retail Equivalent",
                highlights=["Standard Retail MRP: ₹65 (Protects against ₹999 price gouge)", "Baked Formulation", "Quick Commerce Verified"],
                source_retailer="Blinkit / Zepto",
                source_url="https://www.blinkit.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Kurkure Solid Masti Masala Twisteez",
                brand="PepsiCo Kurkure",
                category="Extruded Savory Snack",
                net_quantity="90 g",
                estimated_mrp="₹ 20.00",
                unit_price="₹ 0.22 / g",
                similarity_type="Economy Value Pack",
                highlights=["Cost-Effective Unit Rate", "Traditional Masala Taste", "FSSAI Registered"],
                source_retailer="Zepto / Blinkit",
                source_url="https://www.zeptonow.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Haldiram's Bhujia Sev",
                brand="Haldiram's",
                category="Traditional Namkeen",
                net_quantity="200 g",
                estimated_mrp="₹ 58.00",
                unit_price="₹ 0.29 / g",
                similarity_type="Traditional Alternative",
                highlights=["Standard Retail Price", "Crispy Moth Bean Flour", "Wide Retail Availability"],
                source_retailer="BigBasket / Amazon",
                source_url="https://www.bigbasket.com",
                compliance_confidence="High (Registered Standard Brand)"
            )
        ]
    },
    "noodles_partial_review": {
        "name": "TastyBite Masala Noodles (Review Required)",
        "filename": "sample_noodles.jpg",
        "description": "Commodity package with partial consumer care helpline and ambiguous date stamp requiring manual inspection.",
        "extracted_data": ExtractedProductData(
            product_name="Spicy Masala Instant Noodles",
            brand="TastyBite",
            generic_name="Instant Noodles with Seasoning",
            manufacturer="TastyBite Foods Ltd, Industrial Area, Solan, HP, India",
            packer=None,
            importer=None,
            country_of_origin="India",
            net_quantity="70 g",
            mrp="₹ 15.00",
            manufacturing_date="2026",
            best_before="Best Before 9 Months",
            consumer_care="For complaints contact Consumer Care Executive",
            batch_number="LOT-99A",
            barcode="8901234567890",
            ingredients="Wheat flour, Palm oil, Salt, Spices & Condiments (Chilli, Cumin, Turmeric), Flavor enhancers.",
            warnings=["Contains Wheat. Manufactured on equipment that processes peanut and soy."],
            certification_marks=["FSSAI Lic. No. 10012011000345", "Green Veg Dot"],
            other_visible_text=["Ready in 2 Minutes", "Extra Spicy Tandoori Flavor"],
            regions=[
                BoundingRegion(label="Product Name", text="Spicy Masala Instant Noodles", x=5.0, y=3.0, width=88.0, height=9.0, approx_pixel_height=38),
                BoundingRegion(label="Manufacturer", text="TastyBite Foods Ltd, Solan, HP", x=6.0, y=26.0, width=35.0, height=5.0, approx_pixel_height=20),
                BoundingRegion(label="Net Quantity", text="Net Wt: 70 g", x=6.0, y=69.0, width=15.0, height=4.0, approx_pixel_height=24),
                BoundingRegion(label="MRP", text="₹ 15.00", x=56.0, y=69.0, width=20.0, height=4.0, approx_pixel_height=26)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="LOW",
            risk_score=20,
            assessment_title="LOW AUTHENTICITY RISK",
            assessment_summary="Brand and product identity corroborated by online retail listings.",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="TastyBite", reference_value="TastyBite", evidence_id="E-004", status="pass", reason="Brand 'TastyBite' corroborated."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="Instant Noodles", reference_value="Instant Noodles 70g", evidence_id="E-004", status="pass", reason="Instant noodles variant confirmed.")
            ],
            sources=[
                WebSourceEvidence(title="TastyBite Products", publisher_domain="tastybite.com", url="https://tastybite.com", source_type="OFFICIAL", snippet="TastyBite Noodles 70g Pack", matched_attributes=["brand", "product"], retrieved_info={"Brand": "TastyBite", "Product": "Instant Noodles 70g"})
            ]
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=True,
            has_nutrition_table=True,
            serving_size="70 g (1 pack)",
            servings_per_container="1 serving",
            summary_verdict="Instant Noodle Pack - High Sodium Alert",
            highlights=[
                "High Sodium Content (920mg / 100g - Caution)",
                "Instant Prep in 2 Minutes",
                "Fortified with Iron & B-Vitamins",
                "Allergen: Contains Wheat Gluten"
            ],
            items=[
                NutrientItem(name="Energy", value="385 kcal", per_unit="per 100g", daily_value_percent="19.2%", indicator_level="NORMAL"),
                NutrientItem(name="Protein", value="8.0 g", per_unit="per 100g", daily_value_percent="14.8%", indicator_level="NORMAL"),
                NutrientItem(name="Carbohydrates", value="55.0 g", per_unit="per 100g", daily_value_percent="18.3%", indicator_level="NORMAL"),
                NutrientItem(name="Total Sugars", value="2.8 g", per_unit="per 100g", daily_value_percent="5.6%", indicator_level="LOW"),
                NutrientItem(name="Total Fat", value="15.0 g", per_unit="per 100g", daily_value_percent="22.4%", indicator_level="MODERATE"),
                NutrientItem(name="Saturated Fat", value="6.5 g", per_unit="per 100g", daily_value_percent="29.5%", indicator_level="HIGH"),
                NutrientItem(name="Trans Fat", value="0.05 g", per_unit="per 100g", daily_value_percent="0%", indicator_level="LOW"),
                NutrientItem(name="Dietary Fiber", value="3.1 g", per_unit="per 100g", daily_value_percent="10.3%", indicator_level="NORMAL"),
                NutrientItem(name="Sodium", value="920 mg", per_unit="per 100g", daily_value_percent="46.0%", indicator_level="HIGH")
            ]
        ),
        "preset_alternates": [
            AlternateProduct(
                name="Maggi 2-Minute Masala Instant Noodles",
                brand="Nestlé",
                category="Instant Noodles",
                net_quantity="70 g",
                estimated_mrp="₹ 14.00",
                unit_price="₹ 0.20 / g",
                similarity_type="Direct Market Leader",
                highlights=["National Benchmark Brand", "Fortified with Iron & Vitamin A", "100% Legal Metrology Compliant"],
                source_retailer="Blinkit / Zepto / BigBasket",
                source_url="https://www.blinkit.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Sunfeast YiPPee! Magic Masala Noodles",
                brand="ITC",
                category="Instant Noodles",
                net_quantity="65 g",
                estimated_mrp="₹ 12.00",
                unit_price="₹ 0.18 / g",
                similarity_type="Direct Market Competitor",
                highlights=["Non-Sticky Round Noodle Block", "Real Vegetable Extracts", "Value Unit Rate"],
                source_retailer="Zepto / Blinkit",
                source_url="https://www.zeptonow.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Ching's Secret Schezwan Instant Noodles",
                brand="Capital Foods",
                category="Spicy Instant Noodles",
                net_quantity="60 g",
                estimated_mrp="₹ 15.00",
                unit_price="₹ 0.25 / g",
                similarity_type="Spicier Alternative",
                highlights=["Desi Chinese Spicy Flavor", "Vegetarian Green Dot Certified", "Quick 3-Min Preparation"],
                source_retailer="BigBasket",
                source_url="https://www.bigbasket.com",
                compliance_confidence="High (Registered Standard Brand)"
            )
        ]
    },
    "shampoo_non_compliant": {
        "name": "Herbal Shine Shampoo (Non-Compliant - High Risk)",
        "filename": "sample_shampoo.jpg",
        "description": "Defective packaging sample missing mandatory net quantity declaration and manufacturing date under Rule 6.",
        "extracted_data": ExtractedProductData(
            product_name="Herbal Shine Silky Shampoo",
            brand="NatureCare",
            generic_name=None,
            manufacturer="NatureCare Cosmetics, Mumbai",
            net_quantity=None,
            mrp="MRP Rs. 145.00",
            manufacturing_date=None,
            consumer_care="Call 9876543210",
            batch_number="B-12",
            ingredients="Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Herbal Extracts, Fragrance.",
            warnings=["Avoid contact with eyes."],
            other_visible_text=["Deep Nourishment with Amla & Bhringraj", "For Dull & Damaged Hair"],
            regions=[
                BoundingRegion(label="Product Name", text="Herbal Shine Silky Shampoo", x=5.0, y=3.0, width=88.0, height=9.0, approx_pixel_height=36),
                BoundingRegion(label="MRP", text="MRP Rs. 145.00", x=56.0, y=69.0, width=20.0, height=4.0, approx_pixel_height=28)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="HIGH",
            risk_score=75,
            assessment_title="HIGH AUTHENTICITY RISK",
            assessment_summary="Brand 'NatureCare' has unverified online references. Missing mandatory Net Quantity and Manufacturing Date declarations.",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="NatureCare", reference_value="Not available", evidence_id="E-004", status="fail", reason="Unverified brand identity."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="Herbal Shine Silky Shampoo", reference_value="Not available", evidence_id="E-004", status="review", reason="No catalog match found.")
            ],
            reasons=["Unverified brand identity and missing mandatory Legal Metrology packaging declarations."]
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=False,
            has_nutrition_table=False,
            serving_size="N/A",
            servings_per_container=None,
            summary_verdict="Non-Food Commodity - Cosmetic & Personal Care",
            highlights=[
                "Category: Cosmetic Personal Care (Exempt from FSSAI Nutritional Labeling)",
                "Regulated under Drugs & Cosmetics Act and Legal Metrology Rule 6(1)",
                "Mandatory Net Volume, MRP, and Batch Stamping Required"
            ],
            items=[],
            disclaimer="This is a non-food cosmetic commodity. FSSAI nutritional declarations are exempt, but mandatory Legal Metrology declarations apply."
        ),
        "preset_alternates": [
            AlternateProduct(
                name="Dove Daily Shine Shampoo with Nutritive Serum",
                brand="Dove (Hindustan Unilever)",
                category="Hair Care / Shampoo",
                net_quantity="180 ml",
                estimated_mrp="₹ 165.00",
                unit_price="₹ 0.92 / ml",
                similarity_type="Direct Market Leader",
                highlights=["100% Legal Metrology Compliant PDP", "Complete Manufacturer & Net Volume Disclosures", "Micro-Moisture Serum"],
                source_retailer="Blinkit / Zepto / Nykaa",
                source_url="https://www.blinkit.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Clinic Plus Strong & Long Health Shampoo",
                brand="Clinic Plus (HUL)",
                category="Hair Care / Shampoo",
                net_quantity="175 ml",
                estimated_mrp="₹ 115.00",
                unit_price="₹ 0.65 / ml",
                similarity_type="Economy / Value Pack",
                highlights=["Budget-Friendly Unit Rate", "Milk Protein Formula", "Clear Batch & Expiry Stamping"],
                source_retailer="Zepto / BigBasket",
                source_url="https://www.zeptonow.com",
                compliance_confidence="High (Registered Standard Brand)"
            ),
            AlternateProduct(
                name="Himalaya Anti-Hair Fall Bhringraj Shampoo",
                brand="Himalaya Wellness",
                category="Herbal Hair Care",
                net_quantity="180 ml",
                estimated_mrp="₹ 150.00",
                unit_price="₹ 0.83 / ml",
                similarity_type="Herbal Alternative",
                highlights=["Enriched with Bhringraj & Butea Frondosa", "Paraben-Free Formulation", "FSSAI/Ayush Regulatory Clearance"],
                source_retailer="Amazon.in / Nykaa",
                source_url="https://www.amazon.in",
                compliance_confidence="High (Registered Standard Brand)"
            )
        ]
    },
    "dual_panel_valid": {
        "name": "Butter Cookies (Dual-Panel Front PDP + Back Info)",
        "filename": "sample_cookies.jpg",
        "description": "Guided Dual-Panel Scan: Front PDP (Product & Net Qty) + Back Panel (MRP, Mfg, Dates). Coherence: PASSED (100%).",
        "extracted_data": ExtractedProductData(
            product_name="Britannia Treat Butter Cookies",
            brand="Britannia",
            generic_name="Biscuits / Bakery Product",
            manufacturer="Britannia Industries Ltd., 5/1A Hungerford Street, Kolkata - 700017, West Bengal, India. Mfg at: Plot 12, Ind Area, Bidadi, Bangalore - 562109",
            packer=None,
            importer=None,
            country_of_origin="India",
            net_quantity="120 g",
            mrp="MRP ₹ 30.00 (Incl. of all taxes)",
            manufacturing_date="04/2026",
            best_before="6 Months from Manufacture",
            expiry_date="10/2026",
            consumer_care="Toll Free: 1800-425-4444 | Email: feedback@britannia.co.in | Address: Britannia Consumer Care, Bangalore - 562109",
            unit_sale_price="₹ 0.25 / g",
            batch_number="BAT-2026-X81",
            barcode="8901063012345",
            ingredients="Refined Wheat Flour (Maida), Sugar, Butter (14%), Edible Vegetable Oil (Palm), Milk Solids, Invert Sugar Syrup, Raising Agents (500(ii), 503(ii)), Iodised Salt, Emulsifier (322).",
            warnings=["Contains Wheat (Gluten), Milk and Soya.", "May contain traces of Nuts."],
            certification_marks=["FSSAI Lic. No. 10015043001129", "100% Vegetarian (Green Dot Logo)"],
            other_visible_text=["[Front PDP] Rich in Butter Taste", "[Back Panel] Store in a cool dry place"],
            regions=[
                BoundingRegion(label="[Front PDP] Brand & Product", text="Britannia Treat Butter Cookies", x=5.0, y=5.0, width=85.0, height=12.0, approx_pixel_height=42),
                BoundingRegion(label="[Front PDP] Net Quantity", text="Net Qty: 120 g", x=6.0, y=70.0, width=20.0, height=5.0, approx_pixel_height=26),
                BoundingRegion(label="[Back Panel] MRP & USP", text="MRP ₹ 30.00 (USP ₹ 0.25/g)", x=50.0, y=70.0, width=35.0, height=5.0, approx_pixel_height=28),
                BoundingRegion(label="[Back Panel] Manufacturer", text="Britannia Industries Ltd, Kolkata", x=6.0, y=80.0, width=45.0, height=5.0, approx_pixel_height=20)
            ]
        ),
        "preset_authenticity": AuthenticityReport(
            service_available=True,
            risk_level="LOW",
            risk_score=10,
            assessment_title="LOW AUTHENTICITY RISK",
            assessment_summary="Dual-panel packaging cross-verified with official brand catalog and retail records.",
            signals=[
                AuthenticitySignal(name="brand_corroboration", label="Brand Identity Corroboration", scanned_value="Britannia", reference_value="Britannia", evidence_id="E-004", status="pass", reason="Front and Back panels corroborated."),
                AuthenticitySignal(name="product_corroboration", label="Product Variant Corroboration", scanned_value="Treat Butter Cookies", reference_value="Treat Butter Cookies 120g", evidence_id="E-004", status="pass", reason="Corroborated across both panels.")
            ],
            sources=[
                WebSourceEvidence(title="Official Britannia Consumer Products Catalog", publisher_domain="britannia.co.in", url="https://britannia.co.in/products", source_type="OFFICIAL", snippet="Official product listing for Britannia Treat Butter Cookies 120g.", matched_attributes=["brand", "product", "manufacturer"], retrieved_info={"Brand": "Britannia", "Product": "Treat Butter Cookies"})
            ]
        ),
        "preset_nutrition": NutritionInfo(
            is_food_product=True,
            has_nutrition_table=True,
            serving_size="30 g",
            items=[
                NutrientItem(name="Energy", value="492 kcal", per_unit="per 100g", indicator_level="HIGH"),
                NutrientItem(name="Total Sugars", value="24.5 g", per_unit="per 100g", indicator_level="HIGH"),
                NutrientItem(name="Saturated Fat", value="9.8 g", per_unit="per 100g", indicator_level="HIGH"),
                NutrientItem(name="Sodium", value="310 mg", per_unit="per 100g", indicator_level="MODERATE")
            ]
        ),
        "preset_coherence": DualPanelCoherenceResult(
            is_dual_panel=True,
            status="PASS",
            coherence_score=100,
            verdict_title="DUAL-PANEL COHERENCE VERIFIED (100%)",
            verdict_summary="Front PDP and Back Info panels corroborated as matching components of Britannia Treat Butter Cookies (120 g).",
            brand_match=True,
            category_match=True,
            discrepancies=[],
            front_image_filename="sample_cookies.jpg",
            back_image_filename="sample_cookies.jpg"
        )
    },
    "dual_panel_mismatch": {
        "name": "Cross-Product Mismatch Attack (Biscuit Front + Shampoo Back)",
        "filename": "sample_cookies.jpg",
        "description": "Simulated fraud test: Front of Britannia Cookies + Back of NatureCare Shampoo. Rejected by Coherence Gatekeeper!",
        "extracted_data": ExtractedProductData(
            product_name="Britannia Treat Butter Cookies",
            brand="Britannia",
            generic_name="Biscuits / Bakery Product"
        ),
        "preset_coherence": DualPanelCoherenceResult(
            is_dual_panel=True,
            is_coherent=False,
            is_matching=False,
            status="MISMATCH_REJECTED",
            coherence_score=0,
            verdict_title="CROSS-PANEL PRODUCT MISMATCH REJECTED (0%)",
            verdict_summary="Conflicting product panels detected! Front panel is Britannia Cookies (Food), but Back panel belongs to NatureCare Shampoo (Cosmetic). Inspection blocked to prevent cross-product fraud.",
            brand_match=False,
            category_match=False,
            discrepancies=[
                "Brand Conflict: Front panel displays brand 'Britannia', but back panel identifies brand 'NatureCare'.",
                "Critical Category Mismatch: Front panel represents Edible Packaged Food, while back panel corresponds to Cosmetic / Personal Care.",
                "Variant Divergence: Front title 'Britannia Treat Butter Cookies' has zero keyword overlap with back panel 'Herbal Shine Shampoo'."
            ],
            front_image_filename="sample_cookies.jpg",
            back_image_filename="sample_shampoo.jpg"
        )
    }
}
