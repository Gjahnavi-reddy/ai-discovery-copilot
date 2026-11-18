"""
Information Extraction Engine for Cynbit AI Discovery Copilot.

Extracts structured technical specifications from unstructured client text:
- Core deliverables and functional requirements
- Tech stack elements
- Budget figures, ranges, and feasibility
- Timelines, durations, and urgency/unrealistic flags
- Client archetype and industry domain
"""

import re
from typing import List, Optional, Tuple
from src.models.schemas import (
    ExtractedRequirements,
    BudgetInfo,
    TimelineInfo,
    CynbitServiceCategory,
)


TECH_CATALOG = [
    # Frameworks & Languages
    "python", "typescript", "javascript", "react", "next.js", "nextjs", "vue",
    "fastapi", "django", "node.js", "node", "go", "golang", "flutter", "react native",
    # AI & Agents
    "rag", "langchain", "llamaindex", "gemini", "gpt-4", "gpt", "claude", "ollama",
    "vector database", "pinecone", "chroma", "qdrant", "weaviate", "embeddings",
    "function calling", "tool-calling", "multi-agent", "semantic search", "huggingface",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "eks", "gke", "terraform",
    "github actions", "ci/cd", "redis", "postgresql", "postgres", "mongodb", "mysql",
    "websockets", "microservices", "serverless", "lambda", "s3", "cloudflare", "cdn",
    # Tools & Integrations
    "zendesk", "figma", "stripe", "shopify", "salesforce", "confluence", "jira",
    "soc2", "oauth", "rest api", "graphql"
]

INDUSTRY_PATTERNS = {
    "FinTech & Banking": [r"fintech", r"banking", r"payments", r"loan", r"covenants", r"trading"],
    "Legal & Compliance": [r"legal", r"contract", r"law", r"indemnification", r"soc2", r"regulatory"],
    "Real Estate & Property Management": [r"property", r"tenant", r"tenantease", r"lease", r"commercial real estate"],
    "E-Commerce & Retail": [r"ecommerce", r"e-commerce", r"retail", r"storefront", r"shopify", r"cart"],
    "Logistics & Supply Chain": [r"logistics", r"supply chain", r"telemetry", r"tracking", r"warehouse"],
    "Enterprise Collaboration / SaaS": [r"collaborative", r"workspace", r"remote team", r"document", r"multiplayer"],
}


def extract_budget(text: str) -> BudgetInfo:
    """Extract budget expressions, range bounds, currency, and feasibility notes."""
    text_lower = text.lower()
    
    # Check for explicit range like "$35,000 to $45,000" or "$35,000 - $45,000"
    range_match = re.search(
        r'(\$|usd|inr|₹|eur|€)?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:k)?\s*(?:to|-|–)\s*(\$|usd|inr|₹|eur|€)?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:k)?\b',
        text,
        re.IGNORECASE
    )
    
    # Single figure match like "$25,000", "$40k", "budget of 15,000"
    single_match = re.search(
        r'(?:budget|allocated|of)\s*(?:is|of|about|around)?\s*(\$|usd|inr|₹|eur|€)?\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?\b',
        text,
        re.IGNORECASE
    )
    if not single_match:
        single_match = re.search(r'(\$|₹|€|£)\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?\b', text, re.IGNORECASE)

    raw_budget: Optional[str] = None
    currency: Optional[str] = "USD"
    min_val: Optional[float] = None
    max_val: Optional[float] = None

    if range_match:
        raw_budget = range_match.group(0).strip()
        curr_symbol = range_match.group(1) or range_match.group(3) or "$"
        currency = "INR" if curr_symbol in ["₹", "inr"] else ("EUR" if curr_symbol in ["€", "eur"] else "USD")
        
        v1_str = range_match.group(2).replace(",", "")
        v2_str = range_match.group(4).replace(",", "")
        v1 = float(v1_str) * (1000 if "k" in range_match.group(0).lower() and float(v1_str) < 1000 else 1)
        v2 = float(v2_str) * (1000 if "k" in range_match.group(0).lower() and float(v2_str) < 1000 else 1)
        min_val, max_val = min(v1, v2), max(v1, v2)
    elif single_match:
        raw_budget = single_match.group(0).strip()
        curr_symbol = single_match.group(1) or "$"
        currency = "INR" if curr_symbol in ["₹", "inr"] else ("EUR" if curr_symbol in ["€", "eur"] else "USD")
        
        val_str = single_match.group(2).replace(",", "")
        val = float(val_str)
        if single_match.group(3) or (val < 1000 and "k" in raw_budget.lower()):
            val *= 1000
        min_val, max_val = val, val

    if raw_budget and min_val is not None:
        if min_val >= 25000:
            notes = f"Stated budget ({raw_budget}) is well-aligned with standard enterprise/agency technical delivery."
        elif min_val >= 10000:
            notes = f"Stated budget ({raw_budget}) is suitable for modular MVP or targeted feature scope."
        else:
            notes = f"Stated budget ({raw_budget}) is below standard agency project threshold; may require phased rollout."
        return BudgetInfo(
            raw_budget=raw_budget,
            currency=currency,
            estimated_min=min_val,
            estimated_max=max_val,
            is_specified=True,
            feasibility_notes=notes
        )

    # Check if inquiry explicitly mentions that budget is not yet set or discovery-based
    if any(p in text_lower for p in ["not have a fixed budget", "relying on cynbit", "no fixed budget", "estimate"]):
        return BudgetInfo(
            raw_budget=None,
            currency="USD",
            is_specified=False,
            feasibility_notes="Client explicitly requested Cynbit to provide architectural sizing and tier options."
        )

    return BudgetInfo(
        raw_budget=None,
        currency="USD",
        is_specified=False,
        feasibility_notes="Budget not specified in inquiry text. Requires discovery discussion."
    )


def extract_timeline(text: str) -> TimelineInfo:
    """Extract timeline duration, deadline constraints, and detect unrealistic schedules."""
    text_lower = text.lower()

    # Search for patterns like "12-week", "10 weeks", "8 weeks", "14 weeks", "6 months"
    week_match = re.search(r'(\d+)\s*(?:-|–|\s)?\s*(?:week|weeks|wk|wks)\b', text, re.IGNORECASE)
    month_match = re.search(r'(\d+)\s*(?:-|–|\s)?\s*(?:month|months|mo|mos)\b', text, re.IGNORECASE)
    day_match = re.search(r'(\d+)\s*(?:-|–|\s)?\s*(?:day|days)\b', text, re.IGNORECASE)
    rush_deadline_match = re.search(r'\b(monday|tomorrow|this weekend|48 hours|24 hours|3 days)\b', text_lower)

    raw_timeline: Optional[str] = None
    estimated_weeks: Optional[float] = None
    urgency_level = "unspecified"
    feasibility_notes = "Timeline not stated; requires discovery scoping."

    if rush_deadline_match:
        raw_timeline = rush_deadline_match.group(0)
        # Check if scope is complex (e.g. enterprise, autonomous agent, SOC2)
        if any(w in text_lower for w in ["autonomous", "soc2", "enterprise", "covenants", "platform", "system"]):
            estimated_weeks = 0.5
            urgency_level = "unrealistic"
            feasibility_notes = (
                f"High Delivery Risk: Stated delivery timeline ('{raw_timeline}') is technically unfeasible "
                "for enterprise AI/compliance architecture. Recommend establishing an emergency phased milestone."
            )
            return TimelineInfo(
                raw_timeline=raw_timeline,
                estimated_weeks=estimated_weeks,
                is_specified=True,
                urgency_level=urgency_level,
                feasibility_notes=feasibility_notes
            )

    if week_match:
        raw_timeline = week_match.group(0)
        estimated_weeks = float(week_match.group(1))
    elif month_match:
        raw_timeline = month_match.group(0)
        estimated_weeks = float(month_match.group(1)) * 4.33
    elif day_match:
        raw_timeline = day_match.group(0)
        estimated_weeks = float(day_match.group(1)) / 7.0

    if estimated_weeks is not None:
        if estimated_weeks < 2:
            urgency_level = "unrealistic"
            feasibility_notes = f"Timeline ({raw_timeline}) is extremely aggressive. Requires scope trimming to MVP."
        elif estimated_weeks <= 6:
            urgency_level = "urgent"
            feasibility_notes = f"Timeline ({raw_timeline}) is fast-paced but viable with focused sprint cadences."
        elif estimated_weeks <= 16:
            urgency_level = "moderate"
            feasibility_notes = f"Timeline ({raw_timeline}) is standard and realistic for end-to-end engineering."
        else:
            urgency_level = "relaxed"
            feasibility_notes = f"Timeline ({raw_timeline}) allows for thorough architectural phases and testing."

        return TimelineInfo(
            raw_timeline=raw_timeline,
            estimated_weeks=round(estimated_weeks, 1),
            is_specified=True,
            urgency_level=urgency_level,
            feasibility_notes=feasibility_notes
        )

    return TimelineInfo(
        raw_timeline=None,
        estimated_weeks=None,
        is_specified=False,
        urgency_level="unspecified",
        feasibility_notes="Timeline not explicitly provided. Schedule will be established during discovery."
    )


def extract_requirements(inquiry_text: str) -> ExtractedRequirements:
    """Extract all technical specs, tech stack, budget, timeline, and client type."""
    text_lower = inquiry_text.lower()

    # 1. Detect Technologies
    detected_tech: List[str] = []
    for tech in TECH_CATALOG:
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, text_lower):
            # Normalize display capitalization
            display_name = tech.title()
            if tech in ["aws", "gcp", "rag", "k8s", "eks", "gke", "ci/cd", "rest api", "graphql", "soc2", "mvp", "cdn"]:
                display_name = tech.upper()
            elif tech == "next.js" or tech == "nextjs":
                display_name = "Next.js"
            elif tech == "fastapi":
                display_name = "FastAPI"
            elif tech == "postgresql" or tech == "postgres":
                display_name = "PostgreSQL"
            if display_name not in detected_tech:
                detected_tech.append(display_name)

    # 2. Extract Core Deliverables
    # Split text into sentences and identify sentences with actionable deliverables
    sentences = re.split(r'[.!?\n]+', inquiry_text)
    deliverables: List[str] = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 15:
            continue
        s_lower = s_clean.lower()
        if any(verb in s_lower for verb in [
            "need", "build", "design", "develop", "looking for", "seeking", "require",
            "modernized", "migrated", "roll out", "rebuild", "overhaul", "automate"
        ]):
            # Clean leading polite prefixes
            cleaned_s = re.sub(
                r'^(hi|hello|dear cynbit|specifically|we also|we need|we require|we are seeking|we are launching|need)\s*(to|an|a|our)?\s*',
                '',
                s_clean,
                flags=re.IGNORECASE
            )
            cleaned_s = cleaned_s[:1].upper() + cleaned_s[1:]
            deliverables.append(cleaned_s)

    if not deliverables and len(inquiry_text.strip()) > 15:
        deliverables.append(inquiry_text.strip())

    # 3. Detect Budget & Timeline
    budget_info = extract_budget(inquiry_text)
    timeline_info = extract_timeline(inquiry_text)

    # 4. Detect Client Type
    client_type = "unknown"
    if any(w in text_lower for w in ["enterprise", "legacy", "compliance", "soc2", "telemetry events", "covenants"]):
        client_type = "enterprise"
    elif any(w in text_lower for w in ["launching", "mvp", "seed funding", "startup", "figma designs"]):
        client_type = "startup"
    elif any(w in text_lower for w in ["retail", "properties", "storefront", "commercial"]):
        client_type = "smb"
    elif len(inquiry_text.split()) < 20:
        client_type = "individual"

    # 5. Detect Industry
    detected_industry = "General Technology / SaaS"
    for ind, patterns in INDUSTRY_PATTERNS.items():
        if any(re.search(p, text_lower) for p in patterns):
            detected_industry = ind
            break

    return ExtractedRequirements(
        core_requirements=deliverables[:5],
        suggested_tech_stack=detected_tech,
        budget=budget_info,
        timeline=timeline_info,
        client_type=client_type,
        domain_industry=detected_industry
    )
