"""Unit tests for Pydantic data schemas and contract integrity."""

import pytest
from pydantic import ValidationError
from src.config import CynbitServiceCategory
from src.models.schemas import (
    InquiryInput,
    ServiceClassification,
    BudgetInfo,
    TimelineInfo,
    ExtractedRequirements,
    MissingInfoAnalysis,
    ClarificationQuestion,
    ScoreBreakdown,
    DiscoveryBrief,
    CustomerResponseDraft,
    PipelineResult,
)


def test_inquiry_input_defaults():
    inquiry = InquiryInput(inquiry_text="Need an AI agent built for customer support.")
    assert inquiry.inquiry_id.startswith("INQ-")
    assert inquiry.client_name == "Prospective Client"
    assert inquiry.submission_channel == "Web Contact Form"
    assert inquiry.inquiry_text == "Need an AI agent built for customer support."


def test_inquiry_input_empty_text_fails():
    with pytest.raises(ValidationError):
        InquiryInput(inquiry_text="")


def test_service_classification_valid():
    cls = ServiceClassification(
        primary_category=CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        confidence=0.92,
        secondary_categories=[CynbitServiceCategory.SCALABLE_SOFTWARE],
        rationale="Strong presence of multi-agent and RAG keywords."
    )
    assert cls.primary_category == CynbitServiceCategory.AUTONOMOUS_AI_AGENTS
    assert cls.confidence == 0.92
    assert len(cls.secondary_categories) == 1


def test_score_breakdown_bounds():
    with pytest.raises(ValidationError):
        ScoreBreakdown(
            technical_fit_score=150.0,  # exceeds 100
            scope_clarity_score=80.0,
            budget_viability_score=70.0,
            timeline_readiness_score=70.0,
            total_score=85.0,
            tier="Tier 1: High Priority Discovery",
            is_heuristic=True,
            scoring_explanation=["test"],
            recommended_human_action="Review lead"
        )


def test_budget_info_defaults():
    b = BudgetInfo()
    assert b.is_specified is False
    assert b.raw_budget is None
    assert b.currency is None
