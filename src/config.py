"""
Configuration and Domain Registry for Cynbit AI Discovery Copilot.

Grounding note (Verified from cynbit.in):
- Cynbit Technologies is based in Jaipur, Rajasthan.
- Core pillars: Autonomous AI Agents & Cognitive Automation, Full-Stack / Scalable Software Engineering,
  Cloud Architecture & DevOps, Technical SEO & Digital Growth.
- Proprietary Products / Initiatives: TenantEase (property management), Revio (AI reputation intelligence),
  Cynbit Studio, and BitElevate (learning ecosystem).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class CynbitServiceCategory(str, Enum):
    """Officially verified service categories offered by Cynbit Technologies."""
    AUTONOMOUS_AI_AGENTS = "Autonomous AI Agents & Cognitive Automation"
    SCALABLE_SOFTWARE = "Scalable Software Development"
    CLOUD_DEVOPS = "Cloud Architecture & DevOps"
    TECHNICAL_SEO_GROWTH = "Technical SEO & Growth Engineering"
    PROPRIETARY_SUITE = "Proprietary Products & Ecosystem"
    OUT_OF_SCOPE = "Out of Scope / Non-Technical Inquiry"


@dataclass(frozen=True)
class ServiceDefinition:
    category: CynbitServiceCategory
    description: str
    typical_deliverables: List[str]
    representative_keywords: List[str]
    typical_duration_weeks: str
    typical_budget_range_usd: str


CYNBIT_SERVICE_REGISTRY: Dict[CynbitServiceCategory, ServiceDefinition] = {
    CynbitServiceCategory.AUTONOMOUS_AI_AGENTS: ServiceDefinition(
        category=CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        description=(
            "Custom autonomous AI agents, multi-agent orchestration, LLM integrations, "
            "tool-calling pipelines, RAG systems, and cognitive business process automation."
        ),
        typical_deliverables=[
            "Custom Autonomous Agent Workflow",
            "RAG (Retrieval-Augmented Generation) Pipeline",
            "Tool-Calling / API Execution Engine",
            "LLM Fine-Tuning & Evaluation Harness",
            "Human-in-the-Loop Supervision Dashboard",
        ],
        representative_keywords=[
            "ai", "agent", "llm", "rag", "langchain", "llamaindex", "gpt", "gemini",
            "claude", "autonomous", "chatbot", "nlp", "semantic search", "vector database",
            "automation", "cognitive", "prompt engineering", "multi-agent", "tool-use"
        ],
        typical_duration_weeks="6 to 16 weeks",
        typical_budget_range_usd="$15,000 - $60,000+"
    ),
    CynbitServiceCategory.SCALABLE_SOFTWARE: ServiceDefinition(
        category=CynbitServiceCategory.SCALABLE_SOFTWARE,
        description=(
            "Modern full-stack digital architectures, high-concurrency web and mobile applications, "
            "real-time collaborative engines, microservices, and custom SaaS platforms."
        ),
        typical_deliverables=[
            "Full-Stack Web Application (React/Next.js/Vue + Node/Python/Go)",
            "Scalable REST & GraphQL APIs",
            "Relational / NoSQL Database Schema & Optimization",
            "Real-time WebSocket / Collaboration Engine",
            "Microservice Architecture & Event Bus",
        ],
        representative_keywords=[
            "full stack", "web app", "react", "next.js", "vue", "fastapi", "django", "node",
            "backend", "frontend", "saas", "database", "postgres", "mongodb", "api", "mobile",
            "flutter", "react native", "concurrency", "dashboard", "microservices"
        ],
        typical_duration_weeks="8 to 20 weeks",
        typical_budget_range_usd="$20,000 - $80,000+"
    ),
    CynbitServiceCategory.CLOUD_DEVOPS: ServiceDefinition(
        category=CynbitServiceCategory.CLOUD_DEVOPS,
        description=(
            "Scalable cloud infrastructure setup, container orchestration, CI/CD pipelines, "
            "cloud migration (AWS/GCP/Azure), and site reliability engineering."
        ),
        typical_deliverables=[
            "Kubernetes / Container Orchestration Architecture",
            "Infrastructure as Code (Terraform / CloudFormation)",
            "Automated CI/CD Deployment Pipelines",
            "Cloud Security, Monitoring & Observability Setup",
            "Cloud Cost Optimization & Migration Audit",
        ],
        representative_keywords=[
            "cloud", "aws", "gcp", "azure", "devops", "kubernetes", "k8s", "docker",
            "terraform", "ci/cd", "migration", "infrastructure", "scaling", "serverless",
            "lambda", "monitoring", "prometheus", "grafana", "sre", "reliability"
        ],
        typical_duration_weeks="4 to 12 weeks",
        typical_budget_range_usd="$12,000 - $50,000"
    ),
    CynbitServiceCategory.TECHNICAL_SEO_GROWTH: ServiceDefinition(
        category=CynbitServiceCategory.TECHNICAL_SEO_GROWTH,
        description=(
            "Mathematical and algorithmic technical search optimization, programmatic SEO, "
            "web vitals acceleration, structured data architectures, and search engineering."
        ),
        typical_deliverables=[
            "Comprehensive Technical SEO Audit",
            "Core Web Vitals & Page Speed Optimization",
            "Programmatic SEO Content Architecture",
            "Schema.org Structured Data Implementation",
            "Search Engine Crawlability & Indexing Remediation",
        ],
        representative_keywords=[
            "seo", "technical seo", "search engine", "core web vitals", "lighthouse",
            "structured data", "schema", "crawlability", "programmatic seo", "indexing",
            "page speed", "growth", "organic traffic"
        ],
        typical_duration_weeks="3 to 8 weeks",
        typical_budget_range_usd="$5,000 - $25,000"
    ),
    CynbitServiceCategory.PROPRIETARY_SUITE: ServiceDefinition(
        category=CynbitServiceCategory.PROPRIETARY_SUITE,
        description=(
            "Inquiries relating to Cynbit's proprietary products (TenantEase, Revio, Cynbit Studio) "
            "or the BitElevate engineering educational ecosystem."
        ),
        typical_deliverables=[
            "TenantEase Enterprise Integration or Custom Deployment",
            "Revio Multi-Site Review Management Implementation",
            "Cynbit Studio Showcase Consultation",
            "BitElevate Technical Training / Corporate Upskilling Program",
        ],
        representative_keywords=[
            "tenantease", "tenant", "property management", "revio", "review management",
            "cynbit studio", "bitelevate", "internship", "course", "training", "upskilling"
        ],
        typical_duration_weeks="Custom / SaaS Onboarding",
        typical_budget_range_usd="Product License / Subscription Tier"
    ),
    CynbitServiceCategory.OUT_OF_SCOPE: ServiceDefinition(
        category=CynbitServiceCategory.OUT_OF_SCOPE,
        description=(
            "Inquiries that do not align with Cynbit's software, AI, cloud, or digital growth domains "
            "(e.g., physical hardware fabrication, non-technical BPO, spam)."
        ),
        typical_deliverables=[],
        representative_keywords=[
            "hardware", "pcb", "soldering", "warehouse", "physical manufacturing",
            "crypto pump", "plumbing", "construction", "spam", "homework"
        ],
        typical_duration_weeks="N/A",
        typical_budget_range_usd="N/A"
    ),
}


@dataclass
class ScoringWeights:
    """
    Transparent Heuristic Lead Scoring Weights.
    Note: As documented in the methodology, this is an explainable heuristic,
    not a trained predictive ML model.
    """
    TECHNICAL_FIT: float = 0.35
    SCOPE_CLARITY: float = 0.30
    BUDGET_VIABILITY: float = 0.20
    TIMELINE_READINESS: float = 0.15

    # Neutral score assigned when information is unknown/unstated
    # (Refinement: missing budget/timeline does not penalize the lead).
    NEUTRAL_UNSPECIFIED_SCORE: float = 65.0


@dataclass
class LLMConfig:
    """LLM configuration for Google Gemini integration."""
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.2
    MAX_OUTPUT_TOKENS: int = 2048
    REQUEST_TIMEOUT_SECONDS: float = 30.0


# Grounding documentation separating Verified Facts, Assumptions, and Recommendations
GROUNDING_FACTS_ASSUMPTIONS_RECOMMENDATIONS = {
    "verified_facts": [
        "Cynbit Technologies is an engineering and AI solutions company based in Jaipur, Rajasthan (cynbit.in).",
        "Publicly verified core services: Autonomous AI Agents & Cognitive Automation, Scalable Software Development, Cloud Architecture, Technical SEO & Digital Growth.",
        "Publicly verified proprietary platforms: TenantEase (property management), Revio (AI reputation intelligence), Cynbit Studio, BitElevate (learning ecosystem)."
    ],
    "working_assumptions": [
        "Inbound sales inquiries arrive with varying technical depth and frequently omit budget or realistic delivery constraints.",
        "Manual qualification by senior engineers creates context-switching overhead and discovery delay.",
        "All ROI projections (e.g. 75% discovery time reduction, 3x conversion) are hypothetical targets requiring empirical validation."
    ],
    "architectural_recommendations": [
        "Employ a hybrid pipeline combining deterministic NLP parsing with LLM reasoning to ensure 100% offline uptime and zero-cost fallback.",
        "Use a transparent, explainable 4-factor heuristic rubric rather than a black-box model until sufficient historical CRM ground truth is gathered.",
        "Keep a human-in-the-loop (Solutions Architect / Lead) at all times before sending client correspondence or archiving leads."
    ]
}
