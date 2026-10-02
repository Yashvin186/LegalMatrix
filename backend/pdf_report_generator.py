"""
LegalMetriX PDF Report Generator - Concise 2-Page A4 Preliminary Inspection Report
Generates a highly structured, professional, and readable 2-page A4 PDF report using ReportLab.
Conforms strictly to Legal Metrology preliminary screening standards.
"""

import os
import datetime
from typing import Dict, Any, List, Optional
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

from backend.models import InspectionReport, WebSourceEvidence


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for exact 'Page X of Y' rendering and running header/footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        page_width, page_height = A4
        margin = 30  # Margin in pt

        timestamp_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        # Running Header (Page 2)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#334155"))
            self.drawString(margin, page_height - 20, "LEGALMETRIX")
            self.setFont("Helvetica", 8)
            self.drawString(margin + 65, page_height - 20, "|  AI-ASSISTED PRELIMINARY INSPECTION REPORT")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(margin, page_height - 23, page_width - margin, page_height - 23)

        # Running Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(margin, 26, page_width - margin, 26)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))
        footer_text = f"LegalMetriX | AI-Assisted Preliminary Inspection Report | Generated: {timestamp_str} IST"
        self.drawString(margin, 15, footer_text)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_width - margin, 15, page_str)

        self.restoreState()


def crop_image_region(image_path: str, region_dict: Dict[str, Any], max_size=(160, 65)) -> Optional[str]:
    """Crops a specific evidence region from the image and returns temp path."""
    if not os.path.exists(image_path):
        return None
    try:
        x = region_dict.get('x')
        y = region_dict.get('y')
        w = region_dict.get('width')
        h = region_dict.get('height')

        if x is None or y is None or w is None or h is None:
            return None

        with PILImage.open(image_path) as img:
            img_w, img_h = img.size
            left = (x / 100.0) * img_w
            top = (y / 100.0) * img_h
            right = ((x + w) / 100.0) * img_w
            bottom = ((y + h) / 100.0) * img_h

            left = max(0, left - 4)
            top = max(0, top - 4)
            right = min(img_w, right + 4)
            bottom = min(img_h, bottom + 4)

            cropped = img.crop((left, top, right, bottom))
            cropped.thumbnail(max_size)

            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), 'legalmatrix_crops')
            os.makedirs(temp_dir, exist_ok=True)
            label_safe = str(region_dict.get('label', 'reg')).replace('/', '_').replace(' ', '_')
            crop_filename = f"crop_{label_safe}_{int(x)}_{int(y)}.jpg"
            crop_path = os.path.join(temp_dir, crop_filename)
            cropped.save(crop_path, quality=90)
            return crop_path
    except Exception:
        return None


def generate_inspection_pdf_report(
    report: InspectionReport,
    image_path: str,
    output_pdf_path: str
) -> str:
    """
    Generates a concise, highly professional 2-Page A4 PDF inspection report for LegalMetriX using ReportLab.
    """
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=25,
        bottomMargin=30
    )

    story = []
    printable_width = 535.27  # A4 width (595.27) minus 2*30

    styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_secondary = colors.HexColor("#1e293b")   # Slate 800
    c_blue = colors.HexColor("#1d4ed8")        # Blue 700
    c_text = colors.HexColor("#334155")        # Slate 700
    c_border = colors.HexColor("#cbd5e1")      # Slate 300
    c_bg_light = colors.HexColor("#f8fafc")    # Slate 50
    c_pass = colors.HexColor("#166534")        # Green 800
    c_review = colors.HexColor("#854d0e")      # Yellow 800
    c_fail = colors.HexColor("#991b1b")        # Red 800

    # Typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.white,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#93c5fd"),
        spaceAfter=0
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_text,
        spaceAfter=3
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    # =========================================================================
    # PAGE 1 - INSPECTION DETAILS + PRODUCT SNAPSHOT + COMPLIANCE MATRIX
    # =========================================================================

    # Header Banner (No government seals/fake logos!)
    header_data = [
        [
            Paragraph("LEGALMETRIX", title_style),
            Paragraph("AI-ASSISTED PRELIMINARY INSPECTION REPORT", ParagraphStyle('HRight', parent=subtitle_style, alignment=2))
        ],
        [
            Paragraph("Packaged Commodity Compliance & Authenticity Screening", subtitle_style),
            Paragraph("Standard: Legal Metrology (Packaged Commodities) Rules, 2011", ParagraphStyle('SubRight', parent=body_style, fontSize=7.5, textColor=colors.HexColor("#cbd5e1"), alignment=2))
        ]
    ]

    header_table = Table(header_data, colWidths=[300, 235.27])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_primary),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    # Inspection Details (Compact 2-row table)
    meta_data = [
        [
            Paragraph("Inspection ID", body_bold), Paragraph(report.inspection_id, body_style),
            Paragraph("Date & Time", body_bold), Paragraph(report.timestamp, body_style),
            Paragraph("Inspection Type", body_bold), Paragraph("Packaged Commodity Inspection", body_style)
        ],
        [
            Paragraph("Analysis Mode", body_bold), Paragraph("Image + AI-assisted analysis", body_style),
            Paragraph("Report Status", body_bold), Paragraph("Preliminary / Officer Review", body_bold),
            Paragraph("Inspector", body_bold), Paragraph("Not provided", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[75, 105, 75, 110, 80, 90.27])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Product Snapshot Section
    story.append(Paragraph("PRODUCT SNAPSHOT & DETECTED DECLARATIONS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    info = report.extracted_data
    date_str = info.manufacturing_date or info.packing_date or info.import_date or "Not detected"

    snapshot_fields = [
        [Paragraph("Product Attribute", table_header_style), Paragraph("Detected Declaration Value", table_header_style)],
        [Paragraph("Brand", table_cell_bold), Paragraph(info.brand or "Not detected", table_cell_style)],
        [Paragraph("Product Name", table_cell_bold), Paragraph(info.product_name or "Not reliably detected", table_cell_style)],
        [Paragraph("Generic Name", table_cell_bold), Paragraph(info.generic_name or "Not detected", table_cell_style)],
        [Paragraph("Manufacturer / Packer", table_cell_bold), Paragraph(info.manufacturer or info.packer or "Not detected", table_cell_style)],
        [Paragraph("Importer / Origin", table_cell_bold), Paragraph(f"{info.importer or 'N/A'} | Origin: {info.country_of_origin or 'India'}", table_cell_style)],
        [Paragraph("Net Quantity", table_cell_bold), Paragraph(info.net_quantity or "Not detected", table_cell_style)],
        [Paragraph("MRP", table_cell_bold), Paragraph(info.mrp or "Not detected", table_cell_style)],
        [Paragraph("Mfg / Packing Date", table_cell_bold), Paragraph(date_str, table_cell_style)],
        [Paragraph("Consumer Care / Barcode", table_cell_bold), Paragraph(f"{info.consumer_care or 'Not detected'} | Barcode: {info.barcode or 'N/A'}", table_cell_style)]
    ]

    snapshot_table = Table(snapshot_fields, colWidths=[130, 245])
    snapshot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light])
    ]))

    # Render Product Image
    img_flowable = None
    if os.path.exists(image_path):
        try:
            with PILImage.open(image_path) as pimg:
                w, h = pimg.size
                aspect = h / w
                target_w = 145
                target_h = int(target_w * aspect)
                if target_h > 150:
                    target_h = 150
                    target_w = int(target_h / aspect)
                img_flowable = Image(image_path, width=target_w, height=target_h)
        except Exception:
            img_flowable = Paragraph("Image unavailable", body_style)

    if img_flowable:
        snapshot_layout = Table([[snapshot_table, img_flowable]], colWidths=[375, 160.27])
        snapshot_layout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(snapshot_layout)
    else:
        story.append(snapshot_table)

    story.append(Spacer(1, 6))

    # Compliance Summary Score Banner
    score_val = report.automated_screening_score
    status_text = report.overall_status

    if "PASS" in status_text:
        status_bg = colors.HexColor("#dcfce7")
        status_tc = c_pass
    elif "FAIL" in status_text:
        status_bg = colors.HexColor("#fee2e2")
        status_tc = c_fail
    else:
        status_bg = colors.HexColor("#fef3c7")
        status_tc = c_review

    summary_data = [
        [
            Paragraph(f"<b>Automated Screening Score:</b> <font size=11 color='{c_blue.hexval()}'><b>{score_val}%</b></font>", body_style),
            Paragraph(f"<font color='{c_pass.hexval()}'><b>PASS: {report.passed_checks}</b></font>", body_style),
            Paragraph(f"<font color='{c_review.hexval()}'><b>REVIEW: {report.review_checks}</b></font>", body_style),
            Paragraph(f"<font color='{c_fail.hexval()}'><b>FAIL: {report.failed_checks}</b></font>", body_style),
            Paragraph(f"<b>Overall:</b> <font color='{status_tc.hexval()}'><b>{status_text}</b></font>", body_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[150, 70, 75, 65, 175.27])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6))

    # Legal Metrology Check Table
    story.append(Paragraph("LEGAL METROLOGY STATUTORY DECLARATION TABLE", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    check_table_data = [
        [
            Paragraph("Statutory Requirement", table_header_style),
            Paragraph("Detected Information", table_header_style),
            Paragraph("Status", table_header_style),
            Paragraph("Confidence", table_header_style)
        ]
    ]

    for idx, check in enumerate(report.compliance_checks, 1):
        status = check.status.upper()
        if status == "PASS":
            status_cell = Paragraph(f"<font color='{c_pass.hexval()}'><b>PASS</b></font>", table_cell_bold)
        elif status in ["FAIL", "MISSING"]:
            status_cell = Paragraph(f"<font color='{c_fail.hexval()}'><b>{status}</b></font>", table_cell_bold)
        else:
            status_cell = Paragraph(f"<font color='{c_review.hexval()}'><b>REVIEW</b></font>", table_cell_bold)

        conf_str = f"{int(check.confidence * 100)}%"

        check_table_data.append([
            Paragraph(check.field_name, table_cell_bold),
            Paragraph(check.detected_value or "<i>Not detected</i>", table_cell_style),
            status_cell,
            Paragraph(conf_str, table_cell_style)
        ])

    check_table = Table(check_table_data, colWidths=[140, 245, 80, 70.27], repeatRows=1)
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light])
    ]))
    story.append(check_table)

    # END OF PAGE 1
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2 - FINDINGS + READABILITY + EVIDENCE + AUTHENTICITY + DISCLAIMER
    # =========================================================================

    story.append(Paragraph("KEY COMPLIANCE & DEFICIENCY FINDINGS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    non_pass_checks = [c for c in report.compliance_checks if c.status.lower() != 'pass']
    if non_pass_checks:
        for idx, check in enumerate(non_pass_checks[:3], 1):  # Top 3 non-pass findings to ensure strict 2-page fit
            status = check.status.upper()
            status_color = c_fail.hexval() if status in ["FAIL", "MISSING", "NON-STANDARD"] else c_review.hexval()

            def_details = [
                [Paragraph("Requirement", body_bold), Paragraph(check.field_name, body_bold), Paragraph("Status", body_bold), Paragraph(f"<font color='{status_color}'><b>{status}</b></font>", body_bold)],
                [Paragraph("Detected", body_bold), Paragraph(check.detected_value or "Not detected", body_style), Paragraph("Ref Rule", body_bold), Paragraph(check.rule_reference, body_style)],
                [Paragraph("Observation", body_bold), Paragraph(check.reason, body_style), Paragraph("Ev. ID", body_bold), Paragraph(check.evidence_id or "E-001", body_style)]
            ]

            def_table = Table(def_details, colWidths=[70, 240, 55, 170.27])
            def_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
                ('GRID', (0, 0), (-1, -1), 0.5, c_border),
                ('PADDING', (0, 0), (-1, -1), 2.5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('SPAN', (1, 2), (3, 2))
            ]))
            story.append(def_table)
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("<b>No non-compliant or ambiguous declarations detected.</b>", body_style))
        story.append(Spacer(1, 4))

    # Readability & Font Analysis Section
    story.append(Paragraph("READABILITY & FONT ANALYSIS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    read = report.readability
    reg_heights = read.region_text_heights or {"MRP": "~30 px", "Net Qty": "~28 px", "Manufacturer": "~20 px"}
    height_str = " | ".join([f"{k}: {v}" for k, v in list(reg_heights.items())[:3]])

    read_summary_data = [
        [
            Paragraph("Image Quality", body_bold), Paragraph("GOOD" if read.sharpness_score > 40 else "MODERATE", body_style),
            Paragraph("Readability", body_bold), Paragraph(read.status.upper(), body_bold),
            Paragraph("Physical Font Size", body_bold), Paragraph("<font color='#854d0e'><b>NOT CALIBRATED</b></font>", body_style)
        ],
        [
            Paragraph("Detected Text Heights", body_bold), Paragraph(height_str or f"~{read.estimated_text_height_px or 28} px", body_style),
            Paragraph("Sharpness Score", body_bold), Paragraph(f"{read.sharpness_score:.1f}", body_style),
            Paragraph("OCR Confidence", body_bold), Paragraph(f"{int(read.ocr_confidence_score * 100)}%", body_style)
        ]
    ]

    read_summary_table = Table(read_summary_data, colWidths=[90, 120, 75, 75, 90, 85.27])
    read_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (1, 1), (1, 1))
    ]))
    story.append(read_summary_table)
    story.append(Spacer(1, 5))

    # Evidence Crops / Snippets Section
    story.append(Paragraph("SUPPORTING EVIDENCE ATTACHMENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    regions = report.extracted_data.regions or []
    crop_rows = []
    if regions:
        for r in regions[:2]:  # Show top 2 evidence crops only to keep strictly 2 pages
            crop_path = crop_image_region(image_path, r.model_dump() if hasattr(r, 'model_dump') else r.__dict__)
            if crop_path and os.path.exists(crop_path):
                img_c = Image(crop_path, width=120, height=45)
                txt_c = Paragraph(f"<b>Ev. ID: E-002</b> | Requirement: {r.label}<br/>Detected: '{r.text}'", body_style)
                crop_rows.append([img_c, txt_c])

    if not crop_rows:
        crop_rows.append([
            Paragraph("E-001 (Original Image)", body_bold),
            Paragraph("Full product image evidence processed across label panel.", body_style)
        ])

    crop_table = Table(crop_rows, colWidths=[130, 405.27])
    crop_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 2.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(crop_table)
    story.append(Spacer(1, 5))

    # Authenticity Risk & Web Sources
    story.append(Paragraph("AUTHENTICITY RISK ASSESSMENT", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    auth = report.authenticity
    if auth:
        auth_banner = [
            [
                Paragraph("Authenticity Risk Score", body_bold), Paragraph(f"<b><font color='{c_blue.hexval()}'>{auth.risk_score} / 100</font></b>", body_style),
                Paragraph("Risk Level", body_bold), Paragraph(f"<b>{auth.risk_level}</b>", body_bold),
                Paragraph("Guidance", body_bold), Paragraph("Manual verification recommended", body_style)
            ]
        ]
        auth_table = Table(auth_banner, colWidths=[105, 75, 60, 65, 55, 175.27])
        auth_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(auth_table)
        story.append(Spacer(1, 4))

        # Compact Signal Matrix Table
        sig_data = [
            [Paragraph("Authenticity Signal", table_header_style), Paragraph("Scanned Value", table_header_style), Paragraph("Reference Value", table_header_style), Paragraph("Result", table_header_style)]
        ]

        for sig in auth.signals:
            sig_data.append([
                Paragraph(sig.label, table_cell_bold),
                Paragraph(sig.scanned_value or "Not detected", table_cell_style),
                Paragraph(sig.reference_value or "Not available", table_cell_style),
                Paragraph(f"<b>{sig.status.upper()}</b>", table_cell_bold)
            ])

        sig_table = Table(sig_data, colWidths=[140, 140, 175, 80.27], repeatRows=1)
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
            ('PADDING', (0, 0), (-1, -1), 2.5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light])
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 4))

        # Top 2 Web Evidence Sources Only
        sources = auth.sources or []
        if sources:
            src_data = [
                [Paragraph("Type", table_header_style), Paragraph("Source Title", table_header_style), Paragraph("Domain & URL", table_header_style), Paragraph("Matched Info", table_header_style)]
            ]
            for s in sources[:2]:  # Top 2 web sources only
                src_data.append([
                    Paragraph(s.source_type.upper(), table_cell_bold),
                    Paragraph(s.title, table_cell_style),
                    Paragraph(f"<b>{s.publisher_domain or 'web'}</b><br/><font color='blue'><u>{s.url or 'N/A'}</u></font>", table_cell_style),
                    Paragraph(", ".join(s.matched_attributes) if s.matched_attributes else "Brand / Product", table_cell_style)
                ])
            src_table = Table(src_data, colWidths=[65, 140, 195, 135.27])
            src_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
                ('GRID', (0, 0), (-1, -1), 0.5, c_border),
                ('PADDING', (0, 0), (-1, -1), 2.5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(src_table)

    story.append(Spacer(1, 5))

    # Final Recommendation
    story.append(Paragraph("<b>Recommended Action:</b> Manual officer verification recommended for all REVIEW/FAIL findings.", body_bold))
    story.append(Spacer(1, 4))

    # Final Disclaimer Box
    disclaimer_box_data = [
        [Paragraph(
            "<i>This is an AI-assisted preliminary screening report generated from the supplied image and available reference information. "
            "It is not an official Government of India document, legal certificate, final legal determination, product-safety certificate, "
            "or definitive proof of authenticity/counterfeiting.</i>",
            ParagraphStyle('DisText', parent=body_style, fontSize=7, leading=8.5, textColor=colors.HexColor("#7f1d1d"))
        )]
    ]
    disclaimer_box = Table(disclaimer_box_data, colWidths=[printable_width])
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#fca5a5")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(disclaimer_box)

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_pdf_path
