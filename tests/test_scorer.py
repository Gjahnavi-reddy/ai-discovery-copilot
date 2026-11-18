"""Unit tests for the explainable lead qualification scoring engine."""

from src.config import CynbitServiceCategory, ScoringWeights
from src.models.schemas import (
    ServiceClassification,
    ExtractedRequirements,
    BudgetInfo,
    TimelineInfo,
    MissingInfoAnalysis,
)
from src.pipeline.scorer import compute_lead_score


def test_missing_budget_is_neutral_not_penalized():
    """REFINEMENT #2: Unspecified budget receives 65.0 neutral score."""
    cls = ServiceClassification(
        primary_category=CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        confidence=0.90,
        secondary_categories=[],
        rationale="Strong AI keywords."
    )
    specs = ExtractedRequirements(
        core_requirements=["Build autonomous RAG agent", "Integrate Zendesk API"],
        suggested_tech_stack=["Python", "FastAPI", "PostgreSQL", "RAG"],
        budget=BudgetInfo(is_specified=False),  # Unspecified budget
        timeline=TimelineInfo(is_specified=True, estimated_weeks=10.0, urgency_level="moderate"),
        client_type="enterprise"
    )
    gaps = MissingInfoAnalysis(missing_fields=["Target Budget"])

    score = compute_lead_score(cls, specs, gaps)
    assert score.budget_viability_score == 65.0
    assert "Neutral (Unspecified)" in score.scoring_explanation[2]
    # Total score should still qualify as high or solid tier 2/tier 1 because scope and tech fit are high!
    assert score.total_score >= 70.0


def test_missing_timeline_is_neutral_not_penalized():
    """REFINEMENT #2: Unspecified timeline receives 65.0 neutral score."""
    cls = ServiceClassification(
        primary_category=CynbitServiceCategory.SCALABLE_SOFTWARE,
        confidence=0.88,
        secondary_categories=[],
        rationale="Software engineering."
    )
    specs = ExtractedRequirements(
        core_requirements=["Build web app"],
        suggested_tech_stack=["React", "FastAPI"],
        budget=BudgetInfo(is_specified=True, estimated_min=30000.0, raw_budget="$30k"),
        timeline=TimelineInfo(is_specified=False),  # Unspecified timeline
        client_type="startup"
    )
    gaps = MissingInfoAnalysis(missing_fields=["Target Timeline"])

    score = compute_lead_score(cls, specs, gaps)
    assert score.timeline_readiness_score == 65.0


def test_unrealistic_timeline_caps_score():
    cls = ServiceClassification(
        primary_category=CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        confidence=0.95,
        secondary_categories=[],
        rationale="AI inquiry."
    )
    specs = ExtractedRequirements(
        core_requirements=["SOC2 agent", "contract analysis"],
        suggested_tech_stack=["Python", "RAG"],
        budget=BudgetInfo(is_specified=True, estimated_min=40000.0, raw_budget="$40,000"),
        timeline=TimelineInfo(is_specified=True, estimated_weeks=0.5, urgency_level="unrealistic", raw_timeline="3 days"),
        client_type="enterprise"
    )
    gaps = MissingInfoAnalysis(technical_risks=["Timeline unfeasible"])

    score = compute_lead_score(cls, specs, gaps)
    # Total score must be capped at 72.0 (Tier 2) due to safety constraint
    assert score.total_score <= 72.0
    assert score.tier == "Tier 2: Discovery & Scoping Required"


def test_out_of_scope_tier3_recommends_human_action():
    """REFINEMENT #3: All tiers recommend human review; no auto-rejections."""
    cls = ServiceClassification(
        primary_category=CynbitServiceCategory.OUT_OF_SCOPE,
        confidence=0.95,
        secondary_categories=[],
        rationale="Hardware fabrication."
    )
    specs = ExtractedRequirements(
        core_requirements=["PCB fabrication"],
        suggested_tech_stack=[],
        budget=BudgetInfo(is_specified=False),
        timeline=TimelineInfo(is_specified=False),
        client_type="smb"
    )
    gaps = MissingInfoAnalysis(technical_risks=["Out of scope domain"])

    score = compute_lead_score(cls, specs, gaps)
    assert score.tier == "Tier 3: Exploratory / Advisory Review"
    assert "manual review" in score.recommended_human_action.lower()
    assert score.is_heuristic is True
