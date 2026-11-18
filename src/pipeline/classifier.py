"""
Service Classifier for Cynbit AI Discovery Copilot.

Classifies incoming customer inquiries into Cynbit's service taxonomy:
1. Autonomous AI Agents & Cognitive Automation
2. Scalable Software Development
3. Cloud Architecture & DevOps
4. Technical SEO & Growth Engineering
5. Proprietary Products & Ecosystem (TenantEase, Revio, Cynbit Studio, BitElevate)
6. Out of Scope / Non-Technical Inquiry

Supports multi-label secondary detection and explainable classification rationale.
"""

import re
from typing import Dict, List, Tuple
from src.config import CynbitServiceCategory, CYNBIT_SERVICE_REGISTRY
from src.models.schemas import ServiceClassification


# Ontology dictionary with weighted keywords for deterministic scoring
CATEGORY_ONTOLOGY: Dict[CynbitServiceCategory, Dict[str, float]] = {
    CynbitServiceCategory.AUTONOMOUS_AI_AGENTS: {
        "agent": 3.0, "autonomous": 3.5, "multi-agent": 4.0, "llm": 3.5,
        "rag": 3.5, "retrieval augmented": 4.0, "langchain": 3.0, "llamaindex": 3.0,
        "gpt": 2.5, "gemini": 2.5, "claude": 2.5, "chatbot": 2.0, "nlp": 2.5,
        "vector database": 3.0, "semantic search": 3.0, "tool-calling": 3.5,
        "function calling": 3.5, "cognitive": 2.5, "ai automation": 3.5,
        "prompt engineering": 2.5, "fine-tuning": 3.0, "embeddings": 3.0,
        "ai recommendation": 3.0, "intelligent bot": 2.5, "ai": 1.5,
    },
    CynbitServiceCategory.SCALABLE_SOFTWARE: {
        "full stack": 3.5, "full-stack": 3.5, "web app": 3.0, "saas": 3.0,
        "react": 2.5, "next.js": 3.0, "nextjs": 3.0, "vue": 2.5, "fastapi": 3.0,
        "django": 2.5, "node": 2.0, "nodejs": 2.5, "backend": 2.0, "frontend": 2.0,
        "mobile app": 3.0, "flutter": 3.0, "react native": 3.0, "rest api": 2.5,
        "graphql": 2.5, "postgres": 2.5, "postgresql": 2.5, "mongodb": 2.5,
        "database": 1.5, "microservices": 3.0, "websockets": 3.0, "real-time": 2.5,
        "multiplayer": 2.5, "figma": 2.0, "mvp": 2.0, "storefront": 2.5, "app built": 2.5
    },
    CynbitServiceCategory.CLOUD_DEVOPS: {
        "cloud": 2.0, "aws": 3.0, "gcp": 3.0, "azure": 3.0, "devops": 3.5,
        "kubernetes": 4.0, "k8s": 4.0, "eks": 3.5, "gke": 3.5, "docker": 3.0,
        "containerization": 3.5, "terraform": 3.5, "ci/cd": 3.5, "github actions": 3.0,
        "migration": 3.0, "migrated": 3.0, "on-premise": 2.5, "infrastructure": 2.5,
        "scaling": 2.0, "serverless": 2.5, "observability": 3.0, "prometheus": 3.0,
        "grafana": 3.0, "telemetry": 2.5, "zero-downtime": 3.0, "cdn": 2.5
    },
    CynbitServiceCategory.TECHNICAL_SEO_GROWTH: {
        "seo": 3.5, "technical seo": 4.0, "search engine": 3.0, "core web vitals": 4.0,
        "lighthouse": 3.0, "structured data": 3.5, "schema.org": 3.5, "crawlability": 3.5,
        "indexing": 3.0, "programmatic seo": 4.0, "page speed": 3.0, "organic search": 3.0,
        "growth engineering": 3.0, "search rankings": 3.0
    },
    CynbitServiceCategory.PROPRIETARY_SUITE: {
        "tenantease": 5.0, "tenant": 3.0, "property management": 3.5, "lease": 2.5,
        "revio": 5.0, "reputation intelligence": 4.0, "review management": 4.0,
        "cynbit studio": 5.0, "bitelevate": 5.0, "upskilling": 3.0, "internship": 2.5,
        "training program": 2.5
    },
    CynbitServiceCategory.OUT_OF_SCOPE: {
        "hardware": 4.0, "pcb": 4.5, "soldering": 4.5, "warehouse manufacturing": 4.5,
        "silicon": 3.5, "plastic enclosure": 4.0, "fabricate": 3.5, "factory": 3.0,
        "plumbing": 5.0, "hydraulic": 4.5, "pipe installation": 4.5, "construction": 4.0,
        "crypto pump": 5.0, "drop table": 4.0, "homework": 4.0, "alert('xss')": 5.0
    }
}


def is_malformed_input(text: str) -> bool:
    """Detect if input is spam, gibberish, code injection, or lacks meaningful prose."""
    cleaned = text.strip()
    if len(cleaned) < 15:
        return True
    
    # Check for SQL injection or script injection artifacts
    if re.search(r"(drop\s+table|<script>|select\s+\*\s+from|union\s+select)", cleaned, re.IGNORECASE):
        return True
    
    # Check character repetition or non-alphabetic ratio
    alpha_chars = sum(c.isalpha() for c in cleaned)
    total_chars = len(cleaned)
    if alpha_chars / total_chars < 0.45:
        return True
    
    # Check for gibberish keyboard mashing like "asdfghjkl"
    if re.search(r"(asdfgh|qwerty|zxcvbn|1234567890)", cleaned, re.IGNORECASE):
        words = cleaned.split()
        if len(words) < 15:
            return True

    return False


def classify_inquiry(inquiry_text: str) -> ServiceClassification:
    """
    Classify unstructured inquiry text into Cynbit service categories.
    
    Returns:
        ServiceClassification containing primary_category, confidence, 
        secondary_categories, and an explainable rationale.
    """
    if is_malformed_input(inquiry_text):
        return ServiceClassification(
            primary_category=CynbitServiceCategory.OUT_OF_SCOPE,
            confidence=0.95,
            secondary_categories=[],
            rationale=(
                "Input flagged as malformed, gibberish, or containing adversarial syntax. "
                "Classified as Out of Scope to protect downstream systems."
            )
        )

    text_lower = inquiry_text.lower()
    category_scores: Dict[CynbitServiceCategory, float] = {}

    for cat, keywords in CATEGORY_ONTOLOGY.items():
        score = 0.0
        for kw, weight in keywords.items():
            pattern = r'\b' + re.escape(kw) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                score += weight * min(matches, 3)  # cap frequency to prevent keyword stuffing
        category_scores[cat] = score

    # Check for clear out-of-scope priority
    out_of_scope_score = category_scores.get(CynbitServiceCategory.OUT_OF_SCOPE, 0.0)
    if out_of_scope_score >= 6.0:
        return ServiceClassification(
            primary_category=CynbitServiceCategory.OUT_OF_SCOPE,
            confidence=0.90,
            secondary_categories=[],
            rationale=(
                "Inquiry contains high-affinity out-of-scope domain keywords "
                "(e.g., physical hardware fabrication, plumbing, or non-software manufacturing)."
            )
        )

    # Sort categories by score
    sorted_scores = sorted(
        [(cat, sc) for cat, sc in category_scores.items() if cat != CynbitServiceCategory.OUT_OF_SCOPE],
        key=lambda x: x[1],
        reverse=True
    )

    top_cat, top_score = sorted_scores[0]

    # If all category scores are very low, check if generic software app
    if top_score < 2.0:
        if "app" in text_lower or "software" in text_lower or "build" in text_lower or "cost" in text_lower:
            return ServiceClassification(
                primary_category=CynbitServiceCategory.SCALABLE_SOFTWARE,
                confidence=0.55,
                secondary_categories=[],
                rationale=(
                    "Inquiry is brief or incomplete but mentions software/app development. "
                    "Assigned Scalable Software Development pending technical clarification."
                )
            )
        else:
            return ServiceClassification(
                primary_category=CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
                confidence=0.40,
                secondary_categories=[CynbitServiceCategory.SCALABLE_SOFTWARE],
                rationale=(
                    "Inquiry lacks specific technical indicators. Assigned default AI/Automation discovery "
                    "with secondary software scoping."
                )
            )

    # Compute normalized confidence
    second_cat, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0.0)
    confidence = min(0.98, max(0.60, top_score / (top_score + second_score + 1e-5)))

    # Identify valid secondary categories (>= 35% of top score and score >= 3.0)
    secondary: List[CynbitServiceCategory] = []
    for cat, sc in sorted_scores[1:]:
        if sc >= 3.0 and sc >= (top_score * 0.35):
            secondary.append(cat)

    rationale_parts = [
        f"Primary match with '{top_cat.value}' based on strong technical domain keyword presence (score: {top_score:.1f})."
    ]
    if secondary:
        secondary_names = [f"'{c.value}'" for c in secondary]
        rationale_parts.append(
            f"Multi-disciplinary scope detected with secondary alignments: {', '.join(secondary_names)}."
        )

    return ServiceClassification(
        primary_category=top_cat,
        confidence=round(confidence, 2),
        secondary_categories=secondary,
        rationale=" ".join(rationale_parts)
    )
