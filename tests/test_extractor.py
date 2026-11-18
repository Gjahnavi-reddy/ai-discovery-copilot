"""Unit tests for the information extraction engine."""

from src.pipeline.extractor import extract_budget, extract_timeline, extract_requirements


def test_extract_budget_range():
    text = "We have an approved budget of $35,000 to $45,000 for this development phase."
    b = extract_budget(text)
    assert b.is_specified is True
    assert b.estimated_min == 35000.0
    assert b.estimated_max == 45000.0
    assert b.currency == "USD"


def test_extract_budget_single():
    text = "We have a budget of $25k for the MVP."
    b = extract_budget(text)
    assert b.is_specified is True
    assert b.estimated_min == 25000.0


def test_extract_budget_unspecified():
    text = "We do not have a fixed budget line yet and are looking for advice."
    b = extract_budget(text)
    assert b.is_specified is False
    assert b.raw_budget is None


def test_extract_timeline_weeks():
    text = "We want to launch this within a 12-week schedule."
    t = extract_timeline(text)
    assert t.is_specified is True
    assert t.estimated_weeks == 12.0
    assert t.urgency_level == "moderate"


def test_extract_timeline_unrealistic():
    text = "Need this enterprise autonomous agent with SOC2 deployed by this coming Monday (3 days)."
    t = extract_timeline(text)
    assert t.is_specified is True
    assert t.urgency_level == "unrealistic"


def test_extract_requirements_tech_stack():
    text = (
        "We are building a React and Next.js frontend with FastAPI, PostgreSQL, Redis, "
        "and deploying on AWS EKS using Docker and Terraform."
    )
    reqs = extract_requirements(text)
    assert "Next.js" in reqs.suggested_tech_stack
    assert "FastAPI" in reqs.suggested_tech_stack
    assert "PostgreSQL" in reqs.suggested_tech_stack
    assert "AWS" in reqs.suggested_tech_stack
    assert "Docker" in reqs.suggested_tech_stack
    assert "Terraform" in reqs.suggested_tech_stack
