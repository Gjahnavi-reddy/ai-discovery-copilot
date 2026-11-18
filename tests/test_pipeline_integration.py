"""Integration tests for the complete Discovery Copilot Engine pipeline."""

from src.models.schemas import InquiryInput, PipelineResult
from src.core.engine import DiscoveryCopilotEngine
from src.data.sample_inquiries import BENCHMARK_INQUIRIES


def test_engine_initializes_in_deterministic_mode():
    engine = DiscoveryCopilotEngine(prefer_deterministic=True)
    assert engine.prefer_deterministic is True


def test_end_to_end_pipeline_on_all_benchmarks():
    engine = DiscoveryCopilotEngine(prefer_deterministic=True)

    for item in BENCHMARK_INQUIRIES:
        inquiry = InquiryInput(
            inquiry_id=item["id"],
            client_name=item["client_name"],
            client_email=item["client_email"],
            company_name=item["company_name"],
            submission_channel=item["submission_channel"],
            inquiry_text=item["inquiry_text"]
        )

        result: PipelineResult = engine.execute_pipeline(inquiry)

        # Assert contract validity
        assert isinstance(result, PipelineResult)
        assert result.engine_used == "deterministic_fallback"
        assert result.processing_time_ms > 0
        assert len(result.brief.executive_summary) > 20
        assert result.brief.lead_score.total_score >= 0.0
        assert result.brief.lead_score.total_score <= 100.0
        assert len(result.response_draft.full_email_body) > 50
        assert result.brief.lead_score.is_heuristic is True
        assert len(result.brief.lead_score.recommended_human_action) > 10


def test_customer_response_draft_contains_client_name_and_questions():
    engine = DiscoveryCopilotEngine(prefer_deterministic=True)
    inquiry = InquiryInput(
        client_name="Marcus Vance",
        company_name="FinTech Edge Labs",
        inquiry_text="Need an autonomous agent built with RAG and Zendesk integration. Budget is $40k."
    )
    result = engine.execute_pipeline(inquiry)
    draft = result.response_draft
    assert "Marcus" in draft.salutation
    assert "FinTech Edge Labs" in draft.acknowledgment or "Marcus" in draft.salutation
    assert len(draft.call_to_action) > 10
