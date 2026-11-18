"""
Utility script to convert the markdown technical reports into publication-grade PDFs
using ReportLab.
"""

import os
import re
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


def md_to_pdf(markdown_path: str, output_pdf_path: str, doc_title: str) -> None:
    """Read markdown report and generate formatted PDF."""
    if not os.path.exists(markdown_path):
        print(f"Error: {markdown_path} not found.")
        return

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1A2021")    # Primary text
    brand_teal = colors.HexColor("#00666B")       # Primary brand teal
    secondary_teal = colors.HexColor("#4B969B")   # Secondary teal
    slate_gray = colors.HexColor("#637477")       # Secondary text
    light_bg = colors.HexColor("#F4F8F8")         # Main background
    border_color = colors.HexColor("#DCE6E7")     # Border color

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=brand_teal,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=brand_teal,
        spaceAfter=8,
    )
    meta_style = ParagraphStyle(
        "ReportMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=slate_gray,
        spaceAfter=10,
    )
    h1_style = ParagraphStyle(
        "ReportH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=brand_teal,
        spaceBefore=12,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=primary_color,
        spaceAfter=5,
    )
    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )
    code_style = ParagraphStyle(
        "ReportCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=4,
        spaceAfter=4,
    )

    story = []

    # Document Header
    story.append(Paragraph("CYNBIT TECHNOLOGIES — TECHNICAL ASSESSMENT REPORT", subtitle_style))
    story.append(Paragraph(doc_title, title_style))
    story.append(Paragraph("AI/ML Engineer Intern Assessment Deliverable | Grounded in Verified cynbit.in Domain", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_teal, spaceBefore=0, spaceAfter=10))

    lines = md_text.split("\n")
    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.strip()

        # Handle fenced code blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                story.append(Paragraph(code_text, code_style))
                story.append(Spacer(1, 4))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            safe_line = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(safe_line)
            continue

        # Skip main markdown H1/H2 header since we placed customized document title
        if stripped.startswith("# Cynbit AI Discovery Copilot") or stripped.startswith("## Strategic") or stripped.startswith("## Architecture, Methodology"):
            continue

        if stripped.startswith("## "):
            text = stripped[3:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, h1_style))
        elif stripped.startswith("### "):
            text = stripped[4:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, h2_style))
        elif stripped.startswith("#### "):
            text = stripped[5:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, h2_style))
        elif stripped.startswith("* ") or stripped.startswith("- "):
            clean_b = stripped[2:]
            clean_b = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_b)
            clean_b = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_b)
            clean_b = clean_b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            clean_b = clean_b.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            clean_b = clean_b.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
            story.append(Paragraph(f"• {clean_b}", bullet_style))
        elif stripped.startswith("|") and stripped.endswith("|"):
            # Skip raw markdown tables in simple flow
            continue
        elif stripped == "---":
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=6))
        elif stripped:
            clean_p = stripped
            clean_p = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_p)
            clean_p = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_p)
            clean_p = clean_p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            clean_p = clean_p.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            clean_p = clean_p.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
            # KaTeX / math cleanup for plain reportlab
            clean_p = clean_p.replace("$", "")
            story.append(Paragraph(clean_p, body_style))
        else:
            story.append(Spacer(1, 3))

    doc.build(story)
    print(f"Generated PDF: {output_pdf_path}")


if __name__ == "__main__":
    md_to_pdf(
        "reports/REPORT_1_OPPORTUNITY_IDENTIFICATION.md",
        "reports/REPORT_1_OPPORTUNITY_IDENTIFICATION.pdf",
        "Report 1: Strategic AI/ML Opportunity Identification & Technical Product Specification"
    )
    md_to_pdf(
        "reports/REPORT_2_TECHNICAL_EVALUATION.md",
        "reports/REPORT_2_TECHNICAL_EVALUATION.pdf",
        "Report 2: Architecture, Methodology & Empirical Benchmark Evaluation Report"
    )
