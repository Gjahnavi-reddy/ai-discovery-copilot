"""
Personalized Customer Response Drafter for Cynbit AI Discovery Copilot.

Drafts a polished, context-aware initial response email to the prospective client,
embodying Cynbit's technical depth, acknowledging specific project requirements,
and posing key clarification questions politely before a discovery call.
"""

from typing import List
from src.config import CynbitServiceCategory
from src.models.schemas import (
    InquiryInput,
    ServiceClassification,
    ExtractedRequirements,
    ClarificationQuestion,
    CustomerResponseDraft,
)


def draft_customer_response(
    inquiry: InquiryInput,
    classification: ServiceClassification,
    specs: ExtractedRequirements,
    questions: List[ClarificationQuestion]
) -> CustomerResponseDraft:
    """Generate a context-aware, highly personalized response draft."""
    client_first = inquiry.client_name.split()[0] if inquiry.client_name else "there"
    company_phrase = f" at {inquiry.company_name}" if inquiry.company_name and inquiry.company_name != "Unspecified" else ""
    cat = classification.primary_category

    # Subject Line tailored to inquiry
    if cat == CynbitServiceCategory.OUT_OF_SCOPE:
        subject = f"Thank you for contacting Cynbit Technologies — Project Inquiry Review"
    else:
        subject = f"Cynbit Technologies — Discovery & Architecture for your {cat.value} Project"

    salutation = f"Hi {client_first},"

    # Acknowledgment tailored to requirements
    if specs.core_requirements:
        top_req = specs.core_requirements[0]
        ack = (
            f"Thank you for reaching out to Cynbit Technologies. We reviewed your inquiry regarding "
            f"your initiative{company_phrase}, specifically your focus on {top_req.lower().rstrip('.')}."
        )
    else:
        ack = (
            f"Thank you for reaching out to Cynbit Technologies. We appreciate your interest in our "
            f"engineering and digital solutions services."
        )

    # Value proposition grounded in Cynbit's verified strengths
    if cat == CynbitServiceCategory.AUTONOMOUS_AI_AGENTS:
        val_prop = (
            "At Cynbit, our AI engineering practice specializes in production-grade autonomous agent systems, "
            "RAG pipelines, and cognitive workflows designed for enterprise reliability. "
            "We focus on creating robust tool-calling architectures and intuitive human-in-the-loop interfaces."
        )
    elif cat == CynbitServiceCategory.SCALABLE_SOFTWARE:
        val_prop = (
            "Cynbit's engineering team builds high-concurrency, modern web platforms and SaaS architectures. "
            "We emphasize resilient API backends, responsive design systems, and real-time collaboration engines."
        )
    elif cat == CynbitServiceCategory.CLOUD_DEVOPS:
        val_prop = (
            "Our cloud architecture group helps organizations transition to modern, containerized cloud environments "
            "with Kubernetes, Terraform Infrastructure as Code, and automated zero-downtime CI/CD pipelines."
        )
    elif cat == CynbitServiceCategory.TECHNICAL_SEO_GROWTH:
        val_prop = (
            "Cynbit approaches SEO from a rigorous engineering standpoint—optimizing Core Web Vitals, site crawlability, "
            "and programmatic structured data architectures to drive sustainable organic reach."
        )
    elif cat == CynbitServiceCategory.PROPRIETARY_SUITE:
        val_prop = (
            "We are delighted by your interest in Cynbit's proprietary solutions suite. Our platforms are designed "
            "to accelerate operational workflows with turnkey flexibility and modular custom extensions."
        )
    else:
        val_prop = (
            "Cynbit primarily focuses on custom AI automation, full-stack software development, cloud infrastructure, "
            "and digital growth systems."
        )

    # Select top 2-3 clarification questions
    selected_questions: List[str] = []
    for q in questions[:3]:
        selected_questions.append(f"• {q.question}")

    # Call to action
    cta = (
        "To help us prepare a tailored technical discovery agenda and initial architecture recommendations, "
        "could we schedule a brief 25-minute introductory call with our solutions engineering team this week?"
    )

    # Assemble full email body
    email_lines = [
        salutation,
        "",
        ack,
        "",
        val_prop,
        "",
        "To ensure our initial discussion is as valuable and targeted as possible, our architects had a couple of preliminary questions:",
        ""
    ]
    email_lines.extend(selected_questions if selected_questions else ["• Could you share any additional documentation or technical specs you currently have?"])
    email_lines.extend([
        "",
        cta,
        "",
        "Please let us know your preferred availability, or feel free to share any supplementary architecture documents.",
        "",
        "Warm regards,",
        "",
        "Solutions Architecture Team",
        "Cynbit Technologies",
        "https://cynbit.in"
    ])

    full_email = "\n".join(email_lines)

    return CustomerResponseDraft(
        subject_line=subject,
        salutation=salutation,
        acknowledgment=ack,
        value_proposition=val_prop,
        clarification_points=selected_questions,
        call_to_action=cta,
        full_email_body=full_email
    )
