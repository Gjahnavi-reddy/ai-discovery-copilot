"""
Ambiguity and Missing Information Analyzer for Cynbit AI Discovery Copilot.

Analyzes inquiry gaps across:
- Architecture & integration specs
- Scale, traffic, and concurrency expectations
- Security, compliance, and data governance
- Budget and timeline clarity

Generates prioritized clarification questions for the technical discovery session.
"""

from typing import Tuple, List
from src.models.schemas import (
    ExtractedRequirements,
    ServiceClassification,
    MissingInfoAnalysis,
    ClarificationQuestion,
    CynbitServiceCategory,
)


def analyze_gaps_and_generate_questions(
    inquiry_text: str,
    classification: ServiceClassification,
    specs: ExtractedRequirements
) -> Tuple[MissingInfoAnalysis, List[ClarificationQuestion]]:
    """
    Examine extracted specifications against required engineering parameters.
    Returns:
        (MissingInfoAnalysis, List[ClarificationQuestion])
    """
    text_lower = inquiry_text.lower()
    missing_fields: List[str] = []
    ambiguities: List[str] = []
    risks: List[str] = []
    questions: List[ClarificationQuestion] = []
    q_id = 1

    # 1. Budget Gap Analysis
    if not specs.budget.is_specified:
        missing_fields.append("Explicit Target Budget Range")
        questions.append(
            ClarificationQuestion(
                id=q_id,
                topic="Budget Range & Resource Allocation",
                question=(
                    "What target investment bracket or budgetary ceiling has your team allocated "
                    "for the initial MVP versus production rollout phases?"
                ),
                justification="Enables Cynbit solutions architects to right-size the architecture (e.g., serverless vs. dedicated EKS clusters).",
                priority="high"
            )
        )
        q_id += 1

    # 2. Timeline & Schedule Gap Analysis
    if not specs.timeline.is_specified:
        missing_fields.append("Explicit Target Delivery Milestone")
        questions.append(
            ClarificationQuestion(
                id=q_id,
                topic="Target Launch Milestones",
                question=(
                    "Do you have a fixed target delivery date, funding milestone, or stakeholder demo deadline driving this schedule?"
                ),
                justification="Determines team staffing, sprint cadence, and critical path scheduling.",
                priority="medium"
            )
        )
        q_id += 1
    elif specs.timeline.urgency_level == "unrealistic":
        risks.append(
            f"Severe delivery timeline constraint: '{specs.timeline.raw_timeline}' is technically unfeasible for the stated complexity."
        )
        questions.append(
            ClarificationQuestion(
                id=q_id,
                topic="Timeline De-risking & Phasing",
                question=(
                    f"Given that your target timeframe ('{specs.timeline.raw_timeline}') is compressed, could we define a streamlined "
                    "Phase 1 Proof of Concept to satisfy immediate closing needs, followed by production hardening?"
                ),
                justification="Prevents failure to deliver by structuring an aggressive MVP phase while safeguarding security and quality.",
                priority="high"
            )
        )
        q_id += 1

    # 3. Domain-Specific Technical Gaps
    if classification.primary_category == CynbitServiceCategory.AUTONOMOUS_AI_AGENTS:
        # Check data sources and RAG knowledge base
        if not any(w in text_lower for w in ["database", "postgres", "confluence", "docs", "vector", "pdf", "zendesk"]):
            missing_fields.append("Knowledge Base & Training Data Sources")
            questions.append(
                ClarificationQuestion(
                    id=q_id,
                    topic="Data Sources & Ingestion Schemas",
                    question=(
                        "What underlying data stores or document repositories (e.g., Notion, PostgreSQL, PDFs) "
                        "will the autonomous agent need to index and query via RAG?"
                    ),
                    justification="Required to evaluate vector database architecture, chunking strategies, and retrieval latency.",
                    priority="high"
                )
            )
            q_id += 1

        # Check LLM model preference or hosting constraints
        if not any(w in text_lower for w in ["gemini", "gpt", "claude", "local llm", "ollama", "azure openai"]):
            missing_fields.append("Preferred LLM Provider / Privacy Constraints")
            questions.append(
                ClarificationQuestion(
                    id=q_id,
                    topic="Model Governance & Privacy",
                    question=(
                        "Do you have specific enterprise LLM preferences (e.g., Gemini 2.5, OpenAI, Claude) "
                        "or on-premise data residency requirements for the agentic execution?"
                    ),
                    justification="Determines compliance boundaries and API cost projections.",
                    priority="medium"
                )
            )
            q_id += 1

    elif classification.primary_category == CynbitServiceCategory.SCALABLE_SOFTWARE:
        # Check scale & concurrency
        if not any(w in text_lower for w in ["users", "concurrency", "requests", "dau", "mau", "events"]):
            missing_fields.append("Expected Concurrency & Active User Scale")
            questions.append(
                ClarificationQuestion(
                    id=q_id,
                    topic="User Scale & Concurrency",
                    question=(
                        "What is your anticipated day-one and 12-month concurrent user volume and daily transaction scale?"
                    ),
                    justification="Required to architect database connection pooling, caching tiers (Redis), and horizontal pod auto-scalers.",
                    priority="high"
                )
            )
            q_id += 1

    elif classification.primary_category == CynbitServiceCategory.CLOUD_DEVOPS:
        # Check cloud provider credentials & compliance
        if not any(w in text_lower for w in ["compliance", "hipaa", "soc2", "pci", "iso"]):
            missing_fields.append("Security & Compliance Frameworks (SOC2 / HIPAA / GDPR)")
            questions.append(
                ClarificationQuestion(
                    id=q_id,
                    topic="Security & Compliance Baseline",
                    question=(
                        "Are there specific compliance or governance frameworks (e.g. SOC2 Type II, HIPAA, ISO 27001) "
                        "governing this cloud architecture and CI/CD pipeline?"
                    ),
                    justification="Dictates encryption key management, audit logging, and network segregation policies.",
                    priority="high"
                )
            )
            q_id += 1

    # 4. Check for High Ambiguity phrases
    ambiguous_keywords = [
        ("something with ai", "Vague AI mandate without concrete business task definition"),
        ("blockchain or quantum", "Unspecified speculative tech stack additions without business justification"),
        ("agent or something", "Uncertainty on whether standard workflow automation or autonomous reasoning is needed"),
        ("app built", "Minimal scope definition; lacks user stories or target platform specification"),
        ("disrupt the marketing", "Abstract ambition without measurable success metrics")
    ]
    for pattern, rationale in ambiguous_keywords:
        if pattern in text_lower:
            ambiguities.append(f"'{pattern}': {rationale}")

    # 5. Out of scope risk
    if classification.primary_category == CynbitServiceCategory.OUT_OF_SCOPE:
        risks.append("Inquiry falls outside Cynbit's digital engineering and software services domain.")
        questions.append(
            ClarificationQuestion(
                id=q_id,
                topic="Domain Scope Alignment",
                question=(
                    "Cynbit specializes in AI automation, software engineering, and cloud architecture. "
                    "Could you clarify if your project involves a software, telemetry, or digital control layer?"
                ),
                justification="Identifies whether there is an underlying software or digital systems component Cynbit can support.",
                priority="high"
            )
        )
        q_id += 1

    # Critical gap determination
    has_critical = (
        len(specs.core_requirements) == 0
        or (not specs.budget.is_specified and not specs.timeline.is_specified and len(ambiguities) > 0)
        or specs.timeline.urgency_level == "unrealistic"
        or classification.primary_category == CynbitServiceCategory.OUT_OF_SCOPE
    )

    analysis = MissingInfoAnalysis(
        missing_fields=missing_fields,
        ambiguities=ambiguities,
        technical_risks=risks,
        has_critical_gaps=has_critical
    )

    return analysis, questions
