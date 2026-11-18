"""
Discovery Copilot Orchestrator Engine.

Integrates Google Gemini (via google-genai SDK) with an enterprise-grade,
100% deterministic local fallback pipeline.
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

from src.config import LLMConfig, CynbitServiceCategory, CYNBIT_SERVICE_REGISTRY
from src.models.schemas import (
    InquiryInput,
    PipelineResult,
    ServiceClassification,
    ExtractedRequirements,
    BudgetInfo,
    TimelineInfo,
    MissingInfoAnalysis,
    ClarificationQuestion,
    ScoreBreakdown,
    DiscoveryBrief,
    CustomerResponseDraft,
)
from src.pipeline.classifier import classify_inquiry
from src.pipeline.extractor import extract_requirements
from src.pipeline.gap_detector import analyze_gaps_and_generate_questions
from src.pipeline.scorer import compute_lead_score
from src.pipeline.brief_generator import generate_discovery_brief
from src.pipeline.response_drafter import draft_customer_response
from src.core.prompt_templates import SYSTEM_DISCOVERY_PROMPT, USER_ANALYSIS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class DiscoveryCopilotEngine:
    """
    Main orchestrator for Cynbit AI Discovery Copilot.
    Provides dual-mode execution:
    1. Real Gemini LLM API integration via `google-genai` (when API key provided)
    2. Zero-dependency deterministic rule/regex/NLP fallback (when offline or unauthenticated)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = LLMConfig.MODEL_NAME,
        prefer_deterministic: bool = False
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.prefer_deterministic = prefer_deterministic
        self._genai_client = None

        if self.api_key and not self.prefer_deterministic:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google-genai Client: {e}. Defaulting to deterministic engine.")
                self._genai_client = None

    def execute_pipeline(self, inquiry: InquiryInput) -> PipelineResult:
        """
        Execute the end-to-end qualification and discovery workflow.
        Returns validated PipelineResult with full audit trail.
        """
        start_time = time.perf_counter()

        # Check if genuine Gemini call should be attempted
        if self._genai_client is not None and not self.prefer_deterministic:
            try:
                return self._execute_gemini_pipeline(inquiry, start_time)
            except Exception as exc:
                logger.warning(f"Gemini API call failed ({exc}); falling back to deterministic engine.")
                # Graceful fallback to deterministic pipeline below

        return self._execute_deterministic_pipeline(inquiry, start_time)

    def _execute_deterministic_pipeline(self, inquiry: InquiryInput, start_time: float) -> PipelineResult:
        """Execute the 100% offline, deterministic heuristic pipeline."""
        text = inquiry.inquiry_text

        # 1. Classification
        classification = classify_inquiry(text)

        # 2. Information Extraction
        specs = extract_requirements(text)

        # 3. Gap & Ambiguity Analysis + Question Generation
        gaps, questions = analyze_gaps_and_generate_questions(text, classification, specs)

        # 4. Explainable Lead Qualification Scoring
        score = compute_lead_score(classification, specs, gaps)

        # 5. Discovery Brief Synthesis
        brief = generate_discovery_brief(
            inquiry=inquiry,
            classification=classification,
            specs=specs,
            gaps=gaps,
            questions=questions,
            score=score
        )

        # 6. Customer Response Drafting
        response_draft = draft_customer_response(
            inquiry=inquiry,
            classification=classification,
            specs=specs,
            questions=questions
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return PipelineResult(
            inquiry=inquiry,
            brief=brief,
            response_draft=response_draft,
            engine_used="deterministic_fallback",
            processing_time_ms=elapsed_ms,
            raw_model_response=None
        )

    def _execute_gemini_pipeline(self, inquiry: InquiryInput, start_time: float) -> PipelineResult:
        """Execute genuine Gemini call via google-genai SDK with structured schema."""
        user_prompt = USER_ANALYSIS_PROMPT_TEMPLATE.format(
            inquiry_id=inquiry.inquiry_id,
            client_name=inquiry.client_name,
            company_name=inquiry.company_name,
            submission_channel=inquiry.submission_channel,
            inquiry_text=inquiry.inquiry_text
        )

        # Call Gemini model
        from google.genai import types
        response = self._genai_client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=SYSTEM_DISCOVERY_PROMPT + "\n\n" + user_prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=LLMConfig.TEMPERATURE,
                max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
            )
        )

        raw_text = response.text or "{}"
        parsed = json.loads(raw_text)

        # Reconstruct Pydantic models from parsed JSON
        cls_dict = parsed.get("classification", {})
        raw_cat = cls_dict.get("primary_category", "")
        # Match enum
        matched_cat = CynbitServiceCategory.AUTONOMOUS_AI_AGENTS
        for c in CynbitServiceCategory:
            if c.value.lower() in raw_cat.lower() or raw_cat.lower() in c.value.lower():
                matched_cat = c
                break

        classification = ServiceClassification(
            primary_category=matched_cat,
            confidence=float(cls_dict.get("confidence", 0.85)),
            secondary_categories=[],
            rationale=cls_dict.get("rationale", "Classified via Gemini cognitive engine.")
        )

        specs_dict = parsed.get("extracted_specs", {})
        budget_dict = specs_dict.get("budget", {})
        timeline_dict = specs_dict.get("timeline", {})

        budget_info = BudgetInfo(
            raw_budget=budget_dict.get("raw_budget"),
            currency=budget_dict.get("currency", "USD"),
            estimated_min=budget_dict.get("estimated_min"),
            estimated_max=budget_dict.get("estimated_max"),
            is_specified=bool(budget_dict.get("is_specified", False)),
            feasibility_notes=budget_dict.get("feasibility_notes", "Extracted via LLM.")
        )

        timeline_info = TimelineInfo(
            raw_timeline=timeline_dict.get("raw_timeline"),
            estimated_weeks=timeline_dict.get("estimated_weeks"),
            is_specified=bool(timeline_dict.get("is_specified", False)),
            urgency_level=timeline_dict.get("urgency_level", "unspecified"),
            feasibility_notes=timeline_dict.get("feasibility_notes", "Extracted via LLM.")
        )

        specs = ExtractedRequirements(
            core_requirements=specs_dict.get("core_requirements", []),
            suggested_tech_stack=specs_dict.get("suggested_tech_stack", []),
            budget=budget_info,
            timeline=timeline_info,
            client_type=specs_dict.get("client_type", "unknown"),
            domain_industry=specs_dict.get("domain_industry", "Technology")
        )

        missing_dict = parsed.get("missing_info", {})
        gaps = MissingInfoAnalysis(
            missing_fields=missing_dict.get("missing_fields", []),
            ambiguities=missing_dict.get("ambiguities", []),
            technical_risks=missing_dict.get("technical_risks", []),
            has_critical_gaps=bool(missing_dict.get("has_critical_gaps", False))
        )

        questions_list: list[ClarificationQuestion] = []
        for i, q in enumerate(parsed.get("clarification_questions", []), 1):
            questions_list.append(
                ClarificationQuestion(
                    id=i,
                    topic=q.get("topic", "Architecture"),
                    question=q.get("question", ""),
                    justification=q.get("justification", ""),
                    priority=q.get("priority", "medium")
                )
            )

        # Compute explainable score using our auditable rubric
        score = compute_lead_score(classification, specs, gaps)

        # Generate Brief
        service_def = CYNBIT_SERVICE_REGISTRY.get(classification.primary_category)
        cynbit_services = service_def.typical_deliverables if service_def else []

        brief = DiscoveryBrief(
            inquiry_id=inquiry.inquiry_id,
            client_name=inquiry.client_name or "Prospective Client",
            company_name=inquiry.company_name or "Unspecified Organization",
            generated_at=time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            executive_summary=(
                f"LLM Discovery Analysis for {inquiry.company_name or inquiry.client_name}. "
                f"Category: {classification.primary_category.value}. Score: {score.total_score}/100 ({score.tier})."
            ),
            classification=classification,
            extracted_specs=specs,
            missing_info=gaps,
            lead_score=score,
            recommended_cynbit_architecture=parsed.get(
                "recommended_cynbit_architecture",
                "Architectural recommendations synthesized by Gemini."
            ),
            recommended_cynbit_services=cynbit_services,
            clarification_questions=questions_list,
            suggested_next_steps=[
                f"Action: {score.recommended_human_action}",
                "Review Gemini-generated discovery brief and customize customer draft.",
                "Schedule discovery call."
            ]
        )

        resp_dict = parsed.get("customer_response", {})
        response_draft = CustomerResponseDraft(
            subject_line=resp_dict.get("subject_line", f"Cynbit Technologies — {classification.primary_category.value}"),
            salutation=resp_dict.get("salutation", f"Hi {inquiry.client_name},"),
            acknowledgment=resp_dict.get("acknowledgment", "Thank you for contacting Cynbit Technologies."),
            value_proposition=resp_dict.get("value_proposition", "Cynbit specializes in advanced engineering."),
            clarification_points=resp_dict.get("clarification_points", []),
            call_to_action=resp_dict.get("call_to_action", "Let us connect for a brief discovery session."),
            full_email_body=resp_dict.get("full_email_body", "")
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return PipelineResult(
            inquiry=inquiry,
            brief=brief,
            response_draft=response_draft,
            engine_used="gemini",
            processing_time_ms=elapsed_ms,
            raw_model_response=raw_text
        )
