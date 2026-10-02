"""
LegalMetriX Gemini Service
Multimodal visual extraction of packaging declarations using Gemini API.
Extracts structured JSON conforming to the statutory declaration requirements.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from PIL import Image

from backend.models import ExtractedProductData, BoundingRegion, NutritionInfo, NutrientItem

# Extraction Prompt instructing Gemini for structured Legal Metrology declaration extraction
EXTRACTION_SYSTEM_PROMPT = """
You are LegalMetriX Vision, an expert packaging label analysis assistant for Legal Metrology compliance inspection.
Analyze the provided product packaging image carefully and extract all visible text and declarations.

Extract the following structured JSON format:
{
  "product_name": "Exact product name or null if not detected",
  "brand": "Brand name or null if not detected",
  "manufacturer": "Full manufacturer name and address or null if not detected",
  "packer": "Packer name and address if different or null",
  "importer": "Importer name and address if imported or null",
  "country_of_origin": "Country of origin (e.g. 'India', 'Made in India') or null",
  "generic_name": "Common or generic name of commodity or null",
  "net_quantity": "Net quantity with unit (e.g. '100 g', '500 ml', '1 kg', '10 N') or null",
  "mrp": "Maximum Retail Price string exactly as printed (e.g. 'MRP ₹20.00 incl. of all taxes') or null",
  "manufacturing_date": "Manufacturing date (e.g. '05/2026', 'May 2026') or null",
  "packing_date": "Packing date if indicated or null",
  "import_date": "Import date if indicated or null",
  "best_before": "Best before declaration (e.g. '9 months from mfg') or null",
  "expiry_date": "Expiry / Use-by date or null",
  "consumer_care": "Consumer care contact details (phone number, email, address) or null",
  "unit_sale_price": "Unit sale price (e.g. '₹0.20 / g') or null",
  "batch_number": "Batch / Lot number (e.g. 'B.No. 402') or null",
  "barcode": "Barcode / EAN number digits if visible or null",
  "ingredients": "List of visible ingredients or null",
  "warnings": ["Array of any visible warnings, allergens, or cautions"],
  "certification_marks": ["Array of visible marks e.g. 'FSSAI Lic No. ...', 'ISI', 'Agmark', 'Green Veg Logo'"],
  "other_visible_text": ["Array of other visible text blocks/claims on label"],
  "nutrition_info": {
    "is_food_product": true,
    "serving_size": "Serving size e.g. '30 g' or '100 g' or null",
    "servings_per_container": "Servings count or null",
    "items": [
      {
        "name": "Energy / Protein / Carbohydrates / Total Sugars / Added Sugars / Total Fat / Saturated Fat / Trans Fat / Sodium / Fiber",
        "value": "Value with unit e.g. 480 kcal, 7g, 320 mg",
        "per_unit": "per 100g or per serve",
        "daily_value_percent": "e.g. 15% or null",
        "indicator_level": "LOW | MODERATE | HIGH | NORMAL"
      }
    ],
    "highlights": ["e.g. Zero Trans Fat", "High Added Sugar"]
  },
  "regions": [
    {
      "label": "MRP | Net Quantity | Manufacturer | Date | Consumer Care | Product Name",
      "text": "Exact text detected in this zone",
      "x": 10.5,
      "y": 45.2,
      "width": 25.0,
      "height": 8.0,
      "approx_pixel_height": 32
    }
  ]
}

IMPORTANT RULES:
1. ONLY return valid JSON. Do NOT include any markdown explanations or conversational text outside the JSON.
2. For missing information, return null or empty array []. Do NOT invent or fabricate information.
3. For regions, provide approximate bounding coordinates (percentages 0-100 from top-left) where reliably identifiable. If not reliable, omit coordinates or return empty regions.
"""


def get_effective_api_key(passed_key: Optional[str] = None) -> Optional[str]:
    """Helper to retrieve API key from argument, environment, or apikey.txt."""
    if passed_key and len(passed_key.strip()) > 5:
        # If passed key has multiple lines, take first valid line
        first_line = [l.strip() for l in passed_key.splitlines() if l.strip() and len(l.strip()) > 5]
        if first_line:
            return first_line[0]

    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and len(env_key.strip()) > 5:
        first_line = [l.strip() for l in env_key.splitlines() if l.strip() and len(l.strip()) > 5]
        if first_line:
            return first_line[0]

    # Check apikey.txt in project root
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "apikey.txt")
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 5 and not clean_line.startswith("#"):
                        return clean_line
        except Exception:
            pass

    return None


def clean_json_text(text: str) -> str:
    """Strip markdown code blocks or surrounding text to isolate JSON string."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def extract_declarations_from_image(image_path: str, api_key: Optional[str] = None) -> ExtractedProductData:
    """
    Extracts structured product packaging declarations from an image using Gemini.
    """
    effective_api_key = get_effective_api_key(api_key)

    if not effective_api_key:
        raise ValueError(
            "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable, "
            "provide a key in apikey.txt, or use the sample demo presets."
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    pil_image = Image.open(image_path)
    raw_response_text = ""

    is_openrouter = effective_api_key.startswith("sk-or-")

    if is_openrouter:
        import requests
        import base64
        import io
        
        try:
            buffered = io.BytesIO()
            pil_image.convert("RGB").save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            headers = {
                "Authorization": f"Bearer {effective_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": EXTRACTION_SYSTEM_PROMPT},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ]
            }
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            raw_response_text = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenRouter API analysis failed: {str(e)}")
    else:
        candidate_models = [
            'gemini-2.5-flash',
            'gemini-3.6-flash',
            'gemini-3.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-flash-latest'
        ]

        last_exception = None

        try:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=effective_api_key)

                for model_name in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[
                                EXTRACTION_SYSTEM_PROMPT,
                                pil_image
                            ],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            )
                        )
                        raw_response_text = response.text
                        if raw_response_text and raw_response_text.strip():
                            break
                    except Exception as model_err:
                        last_exception = model_err
                        continue
                else:
                    if last_exception:
                        raise last_exception
                    raise RuntimeError("All Gemini model candidates failed to return content.")

            except Exception as genai_err:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=effective_api_key)
                
                legacy_models = ['gemini-2.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro-vision']
                for leg_model in legacy_models:
                    try:
                        model = legacy_genai.GenerativeModel(leg_model)
                        response = model.generate_content([
                            EXTRACTION_SYSTEM_PROMPT,
                            pil_image
                        ])
                        raw_response_text = response.text
                        if raw_response_text and raw_response_text.strip():
                            break
                    except Exception:
                        continue
                else:
                    raise genai_err

        except Exception as e:
            raise RuntimeError(f"Gemini API analysis failed: {str(e)}")

    cleaned_json = clean_json_text(raw_response_text)

    try:
        data_dict = json.loads(cleaned_json)
    except json.JSONDecodeError as err:
        raise ValueError(f"Malformed AI extraction response. Could not parse JSON: {str(err)}. Raw output: {cleaned_json[:200]}")

    regions_list = []
    for r in data_dict.get("regions", []):
        if isinstance(r, dict):
            regions_list.append(BoundingRegion(
                label=r.get("label", "Declaration"),
                text=r.get("text", ""),
                x=r.get("x"),
                y=r.get("y"),
                width=r.get("width"),
                height=r.get("height"),
                approx_pixel_height=r.get("approx_pixel_height")
            ))

    nutrition_obj = None
    nut_dict = data_dict.get("nutrition_info")
    if isinstance(nut_dict, dict):
        nut_items = []
        for it in nut_dict.get("items", []):
            if isinstance(it, dict) and it.get("name") and it.get("value"):
                nut_items.append(NutrientItem(
                    name=it.get("name"),
                    value=it.get("value"),
                    per_unit=it.get("per_unit") or "per 100g",
                    daily_value_percent=it.get("daily_value_percent"),
                    indicator_level=it.get("indicator_level", "NORMAL")
                ))
        if nut_items or nut_dict.get("is_food_product") is False:
            nutrition_obj = NutritionInfo(
                is_food_product=nut_dict.get("is_food_product", True),
                has_nutrition_table=bool(nut_items),
                serving_size=nut_dict.get("serving_size") or data_dict.get("net_quantity") or "100 g",
                servings_per_container=nut_dict.get("servings_per_container"),
                items=nut_items,
                highlights=nut_dict.get("highlights") or []
            )

    return ExtractedProductData(
        product_name=data_dict.get("product_name"),
        brand=data_dict.get("brand"),
        manufacturer=data_dict.get("manufacturer"),
        packer=data_dict.get("packer"),
        importer=data_dict.get("importer"),
        country_of_origin=data_dict.get("country_of_origin"),
        generic_name=data_dict.get("generic_name"),
        net_quantity=data_dict.get("net_quantity"),
        mrp=data_dict.get("mrp"),
        manufacturing_date=data_dict.get("manufacturing_date"),
        packing_date=data_dict.get("packing_date"),
        import_date=data_dict.get("import_date"),
        best_before=data_dict.get("best_before"),
        expiry_date=data_dict.get("expiry_date"),
        consumer_care=data_dict.get("consumer_care"),
        unit_sale_price=data_dict.get("unit_sale_price"),
        batch_number=data_dict.get("batch_number"),
        barcode=data_dict.get("barcode"),
        ingredients=data_dict.get("ingredients"),
        warnings=data_dict.get("warnings") or [],
        certification_marks=data_dict.get("certification_marks") or [],
        other_visible_text=data_dict.get("other_visible_text") or [],
        regions=regions_list,
        nutrition=nutrition_obj,
        raw_response=raw_response_text
    )
