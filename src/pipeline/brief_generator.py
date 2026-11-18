"""
Structured Project Discovery Brief Generator for Cynbit AI Discovery Copilot.

Synthesizes all parsed and scored artifacts into a clean, professional discovery brief
grounded in Cynbit's verified service capabilities.
"""

from datetime import datetime, timezone
from typing import List
from src.config import CynbitServiceCategory, CYNBIT_SERVICE_REGISTRY
from src.models.schemas import (
    InquiryInput,
    ServiceClassification,
    ExtractedRequirements,
    MissingInfoAnalysis,
    ClarificationQuestion,
    ScoreBreakdown,
    DiscoveryBrief,
)


def build_recommended_architecture(
    classification: ServiceClassification,
    specs: ExtractedRequirements
) -> str:
    """Generate tailored technical architecture recommendations based on Cynbit's capabilities."""
    cat = classification.primary_category
    tech_stack = ", ".join(specs.suggested_tech_stack) if specs.suggested_tech_stack else "Modern Cloud-Native Stack"

    if cat == CynbitServiceCategory.AUTONOMOUS_AI_AGENTS:
        return (
            "Recommended Cynbit Cognitive Architecture:\n"
            "• Agent Orchestration: Multi-agent runtime with tool-use / function calling for API execution.\n"
            "• Retrieval Layer: Hybrid RAG architecture (Dense Vector Embeddings + BM25 Sparse Search) with metadata filtering.\n"
            "• Context & Storage: PostgreSQL (pgvector) or specialized vector index + operational Redis state cache.\n"
            "• Governance & Safety: Input/output validation guardrails, prompt evaluation harness, and human-in-the-loop review queue.\n"
            f"• Integrated Technologies: {tech_stack}."
        )
    elif cat == CynbitServiceCategory.SCALABLE_SOFTWARE:
        return (
            "Recommended Cynbit Full-Stack Architecture:\n"
            "• Frontend: Component-driven modern SPA (Next.js / React) with responsive UI, SSR/SSG caching.\n"
            "• Backend API: High-performance asynchronous microservice layer (FastAPI / Node.js) with structured OpenAPI specs.\n"
            "• Real-Time Engine: Redis Pub/Sub + WebSockets for bi-directional live synchronization.\n"
            "• Persistence: Relational data layer (PostgreSQL) with connection pooling and automated migration scripts.\n"
            f"• Integrated Technologies: {tech_stack}."
        )
    elif cat == CynbitServiceCategory.CLOUD_DEVOPS:
        return (
            "Recommended Cynbit Cloud Architecture:\n"
            "• Infrastructure as Code: Modular Terraform definitions for immutable environment provisioning.\n"
            "• Compute & Containers: Containerized Docker workloads orchestrated via Amazon EKS / Kubernetes.\n"
            "• CI/CD Pipeline: Automated multi-stage GitHub Actions with static analysis, container scanning, and zero-downtime rolling deploys.\n"
            "• Observability: Centralized telemetry via Prometheus, Grafana dashboards, and structured cloud logging.\n"
            f"• Integrated Technologies: {tech_stack}."
        )
    elif cat == CynbitServiceCategory.TECHNICAL_SEO_GROWTH:
        return (
            "Recommended Cynbit SEO & Growth Engineering:\n"
            "• Architectural Audit: Complete crawlability, canonicalization, and indexing health check.\n"
            "• Performance Engineering: Core Web Vitals remediation (LCP/CLS/INP optimization, edge asset compression).\n"
            "• Semantic Web: Automated JSON-LD structured data generation (Schema.org) across key entity templates.\n"
            "• Programmatic Content: Scalable headless content delivery pipelines with automated sitemap indexing."
        )
    elif cat == CynbitServiceCategory.PROPRIETARY_SUITE:
        return (
            "Recommended Cynbit Product Suite Alignment:\n"
            "• Platform Evaluation: Assessment against Cynbit TenantEase / Revio modular architectures.\n"
            "• Custom Integration: White-labeled extension modules, custom tenant webhooks, and third-party payment gateway adapters.\n"
            "• Deployment: Managed cloud tenancy or dedicated enterprise deployment with SLA guarantees."
        )
    else:
        return (
            "Scope Advisory:\n"
            "• Current requirements fall outside Cynbit's core digital software services.\n"
            "• Recommend an advisory consultation to explore potential software/IoT telemetry interfaces or polite referral."
        )


def generate_discovery_brief(
    inquiry: InquiryInput,
    classification: ServiceClassification,
    specs: ExtractedRequirements,
    gaps: MissingInfoAnalysis,
    questions: List[ClarificationQuestion],
    score: ScoreBreakdown
) -> DiscoveryBrief:
    """Produce the complete structured discovery brief."""
    service_def = CYNBIT_SERVICE_REGISTRY.get(classification.primary_category)
    cynbit_services = service_def.typical_deliverables if service_def else []

    # Build executive summary
    company_tag = f"from {inquiry.company_name}" if inquiry.company_name and inquiry.company_name != "N/A" else ""
    client_tag = inquiry.client_name or "Prospective Client"
    exec_summary = (
        f"Inquiry received {company_tag} regarding '{classification.primary_category.value}'. "
        f"The client is exploring {specs.domain_industry.lower()} solutions involving {len(specs.core_requirements)} primary requirement(s). "
        f"Qualification score is {score.total_score}/100 ({score.tier}). "
        f"Budget status: {specs.budget.feasibility_notes} "
        f"Timeline status: {specs.timeline.feasibility_notes}"
    )

    # Next steps for the Cynbit team
    next_steps = [
        f"Action: {score.recommended_human_action}",
        "Review and approve/modify the draft response email before contacting the client.",
        f"Address the {len(questions)} identified discovery clarification question(s) during initial contact.",
        "Log discovery brief into CRM and assign lead to relevant Cynbit Practice Lead."
    ]

    arch = build_recommended_architecture(classification, specs)

    return DiscoveryBrief(
        inquiry_id=inquiry.inquiry_id,
        client_name=client_tag,
        company_name=inquiry.company_name or "Unspecified Organization",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        executive_summary=exec_summary,
        classification=classification,
        extracted_specs=specs,
        missing_info=gaps,
        lead_score=score,
        recommended_cynbit_architecture=arch,
        recommended_cynbit_services=cynbit_services,
        clarification_questions=questions,
        suggested_next_steps=next_steps
    )
