"""
PDF Export Utility for Cynbit AI Discovery Copilot.

Generates executive-ready PDF discovery briefs using ReportLab.
"""

import io
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from src.models.schemas import DiscoveryBrief


def generate_discovery_pdf_bytes(brief: DiscoveryBrief) -> bytes:
    """Generate a high-quality PDF document of the Discovery Brief in memory."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    
    # Cynbit Corporate Brand Palette
    primary_color = colors.HexColor("#1A2021")     # Primary text
    brand_teal = colors.HexColor("#00666B")        # Primary brand teal
    secondary_teal = colors.HexColor("#4B969B")    # Secondary teal
    pale_aqua = colors.HexColor("#B4D5D8")         # Pale aqua decorative
    warm_peach = colors.HexColor("#FFD9A8")        # Warm peach accent
    accent_gray = colors.HexColor("#637477")       # Secondary text
    light_bg = colors.HexColor("#F4F8F8")          # Main canvas background
    secondary_bg = colors.HexColor("#EAF2F3")      # Secondary card background
    border_color = colors.HexColor("#DCE6E7")      # Border color

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=brand_teal,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=accent_gray,
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_teal,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=primary_color,
    )
    body_bold = ParagraphStyle(
        "BodyBoldCustom",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "BulletTextCustom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )

    story = []

    # Header
    story.append(Paragraph("CYNBIT TECHNOLOGIES", ParagraphStyle("Brand", fontName="Helvetica-Bold", fontSize=10, textColor=brand_teal, leading=12)))
    story.append(Paragraph("AI Discovery Copilot — Project Discovery Brief", title_style))
    story.append(Paragraph(f"Inquiry ID: {brief.inquiry_id} | Generated: {brief.generated_at} | Grounding: Verified cynbit.in taxonomy", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_teal, spaceBefore=0, spaceAfter=10))

    # Metadata & Score Summary Table
    tier_color = brand_teal if "Tier 1" in brief.lead_score.tier else (colors.HexColor("#A85D00") if "Tier 2" in brief.lead_score.tier else accent_gray)
    
    summary_data = [
        [
            Paragraph("<b>Client Name:</b>", body_style), Paragraph(brief.client_name, body_style),
            Paragraph("<b>Total Lead Score:</b>", body_style), Paragraph(f"<b>{brief.lead_score.total_score}/100</b>", ParagraphStyle("Score", fontName="Helvetica-Bold", fontSize=11, textColor=tier_color))
        ],
        [
            Paragraph("<b>Company:</b>", body_style), Paragraph(brief.company_name, body_style),
            Paragraph("<b>Qualification Tier:</b>", body_style), Paragraph(brief.lead_score.tier, body_bold)
        ],
        [
            Paragraph("<b>Primary Category:</b>", body_style), Paragraph(brief.classification.primary_category.value, body_style),
            Paragraph("<b>Scoring Type:</b>", body_style), Paragraph("Transparent Heuristic (Non-ML)", body_style)
        ]
    ]

    t_summary = Table(summary_data, colWidths=[90, 180, 110, 150])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), secondary_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # Executive Summary
    story.append(Paragraph("1. Executive Discovery Summary", h2_style))
    story.append(Paragraph(brief.executive_summary, body_style))
    story.append(Spacer(1, 8))

    # Explainable Score Breakdown
    story.append(Paragraph("2. Explainable Lead Qualification Rubric", h2_style))
    score_rows = [
        [
            Paragraph("<b>Evaluation Dimension</b>", body_bold),
            Paragraph("<b>Score</b>", body_bold),
            Paragraph("<b>Weight</b>", body_bold),
            Paragraph("<b>Assessment Rationale</b>", body_bold)
        ],
        [
            Paragraph("Technical Alignment", body_style),
            Paragraph(f"{brief.lead_score.technical_fit_score:.1f}/100", body_style),
            Paragraph("35%", body_style),
            Paragraph(brief.lead_score.scoring_explanation[0] if len(brief.lead_score.scoring_explanation) > 0 else "-", body_style)
        ],
        [
            Paragraph("Scope & Clarity", body_style),
            Paragraph(f"{brief.lead_score.scope_clarity_score:.1f}/100", body_style),
            Paragraph("30%", body_style),
            Paragraph(brief.lead_score.scoring_explanation[1] if len(brief.lead_score.scoring_explanation) > 1 else "-", body_style)
        ],
        [
            Paragraph("Budget Viability", body_style),
            Paragraph(f"{brief.lead_score.budget_viability_score:.1f}/100", body_style),
            Paragraph("20%", body_style),
            Paragraph(brief.lead_score.scoring_explanation[2] if len(brief.lead_score.scoring_explanation) > 2 else "-", body_style)
        ],
        [
            Paragraph("Timeline Readiness", body_style),
            Paragraph(f"{brief.lead_score.timeline_readiness_score:.1f}/100", body_style),
            Paragraph("15%", body_style),
            Paragraph(brief.lead_score.scoring_explanation[3] if len(brief.lead_score.scoring_explanation) > 3 else "-", body_style)
        ],
    ]
    t_score = Table(score_rows, colWidths=[110, 55, 45, 320])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 8))

    # Extracted Specifications
    story.append(Paragraph("3. Extracted Technical Specifications", h2_style))
    story.append(Paragraph(f"<b>Core Deliverables:</b>", body_bold))
    for req in brief.extracted_specs.core_requirements:
        story.append(Paragraph(f"• {req}", bullet_style))
    story.append(Spacer(1, 4))
    
    tech_str = ", ".join(brief.extracted_specs.suggested_tech_stack) if brief.extracted_specs.suggested_tech_stack else "Unspecified"
    budget_str = f"{brief.extracted_specs.budget.raw_budget} ({brief.extracted_specs.budget.feasibility_notes})" if brief.extracted_specs.budget.is_specified else brief.extracted_specs.budget.feasibility_notes
    timeline_str = f"{brief.extracted_specs.timeline.raw_timeline} ({brief.extracted_specs.timeline.feasibility_notes})" if brief.extracted_specs.timeline.is_specified else brief.extracted_specs.timeline.feasibility_notes

    specs_table = [
        [Paragraph("<b>Detected Tech Stack:</b>", body_style), Paragraph(tech_str, body_style)],
        [Paragraph("<b>Budget Assessment:</b>", body_style), Paragraph(budget_str, body_style)],
        [Paragraph("<b>Timeline Assessment:</b>", body_style), Paragraph(timeline_str, body_style)],
        [Paragraph("<b>Client Archetype:</b>", body_style), Paragraph(f"{brief.extracted_specs.client_type.title()} ({brief.extracted_specs.domain_industry})", body_style)],
    ]
    t_specs = Table(specs_table, colWidths=[130, 400])
    t_specs.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_specs)
    story.append(Spacer(1, 8))

    # Recommended Cynbit Architecture
    story.append(Paragraph("4. Recommended Cynbit Solution Architecture", h2_style))
    arch_lines = brief.recommended_cynbit_architecture.split("\n")
    for line in arch_lines:
        if line.strip():
            story.append(Paragraph(line, bullet_style if line.startswith("•") else body_style))
    story.append(Spacer(1, 8))

    # Clarification Questions
    story.append(Paragraph("5. Targeted Discovery Clarification Questions", h2_style))
    for q in brief.clarification_questions:
        q_text = f"<b>[{q.priority.upper()}] {q.topic}:</b> {q.question} <i>(Why: {q.justification})</i>"
        story.append(Paragraph(f"• {q_text}", bullet_style))
    story.append(Spacer(1, 8))

    # Human-in-the-Loop Action
    story.append(Paragraph("6. Solutions Team Next Steps", h2_style))
    story.append(Paragraph(f"<b>Recommended Action:</b> {brief.lead_score.recommended_human_action}", body_bold))
    for step in brief.suggested_next_steps:
        story.append(Paragraph(f"• {step}", bullet_style))

    # Build Document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def save_discovery_pdf(brief: DiscoveryBrief, output_path: str) -> None:
    """Save the Discovery Brief as a PDF to disk."""
    pdf_bytes = generate_discovery_pdf_bytes(brief)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
