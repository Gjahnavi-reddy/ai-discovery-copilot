"""Pipeline package for Cynbit AI Discovery Copilot."""
from .classifier import classify_inquiry
from .extractor import extract_requirements
from .gap_detector import analyze_gaps_and_generate_questions
from .scorer import compute_lead_score
from .brief_generator import generate_discovery_brief
from .response_drafter import draft_customer_response

__all__ = [
    "classify_inquiry",
    "extract_requirements",
    "analyze_gaps_and_generate_questions",
    "compute_lead_score",
    "generate_discovery_brief",
    "draft_customer_response",
]
