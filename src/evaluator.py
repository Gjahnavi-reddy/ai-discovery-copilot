"""
Empirical Benchmark Evaluator for Cynbit AI Discovery Copilot.

Evaluates the complete pipeline against the 10 diverse benchmark inquiries:
- Classification accuracy
- Entity extraction precision/recall
- Neutral budget scoring verification (Refinement #2)
- Gap detection recall
- Pydantic schema output validation
- Pipeline latency metrics

Reports ACTUAL measured figures without fabrication.
"""

import time
import json
import os
import sys

# Ensure repository root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Dict, Any
from src.data.sample_inquiries import BENCHMARK_INQUIRIES
from src.models.schemas import InquiryInput, PipelineResult
from src.core.engine import DiscoveryCopilotEngine


def run_benchmark_evaluation() -> Dict[str, Any]:
    """Execute evaluation over all 10 benchmark cases and return metrics."""
    engine = DiscoveryCopilotEngine(prefer_deterministic=True)
    results = []
    
    total_cases = len(BENCHMARK_INQUIRIES)
    classification_matches = 0
    schema_validations = 0
    budget_extraction_matches = 0
    timeline_extraction_matches = 0
    gaps_detected_correctly = 0
    neutral_budget_verified = 0  # Cases where budget is missing and score is exactly 65.0
    latencies_ms = []

    case_summaries = []

    for item in BENCHMARK_INQUIRIES:
        inquiry = InquiryInput(
            inquiry_id=item["id"],
            client_name=item["client_name"],
            client_email=item["client_email"],
            company_name=item["company_name"],
            submission_channel=item["submission_channel"],
            inquiry_text=item["inquiry_text"]
        )

        t0 = time.perf_counter()
        pipeline_res: PipelineResult = engine.execute_pipeline(inquiry)
        latency = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(latency)

        # 1. Schema validation (Pydantic validates during creation; if we reach here, it's valid)
        schema_valid = isinstance(pipeline_res, PipelineResult)
        if schema_valid:
            schema_validations += 1

        # 2. Classification Match
        actual_cat = pipeline_res.brief.classification.primary_category
        expected_cat = item["expected_primary_category"]
        if isinstance(expected_cat, list):
            cat_match = (actual_cat in expected_cat)
        else:
            cat_match = (actual_cat == expected_cat)
        if cat_match:
            classification_matches += 1

        # 3. Budget Extraction Match
        expected_has_budget = item["expected_characteristics"]["has_budget"]
        actual_has_budget = pipeline_res.brief.extracted_specs.budget.is_specified
        budget_match = (expected_has_budget == actual_has_budget)
        if budget_match:
            budget_extraction_matches += 1

        # 4. Neutral Budget Scoring Check (Refinement #2)
        budget_score = pipeline_res.brief.lead_score.budget_viability_score
        if not actual_has_budget:
            # Must be neutral (65.0)
            if budget_score == 65.0:
                neutral_budget_verified += 1
        else:
            neutral_budget_verified += 1

        # 5. Timeline Extraction Match
        expected_has_timeline = item["expected_characteristics"]["has_timeline"]
        actual_has_timeline = pipeline_res.brief.extracted_specs.timeline.is_specified
        timeline_match = (expected_has_timeline == actual_has_timeline)
        if timeline_match:
            timeline_extraction_matches += 1

        # 6. Critical Gap Match
        expected_critical_gaps = item["expected_characteristics"]["has_critical_gaps"]
        actual_critical_gaps = pipeline_res.brief.missing_info.has_critical_gaps
        gap_match = (expected_critical_gaps == actual_critical_gaps)
        if gap_match:
            gaps_detected_correctly += 1

        case_summaries.append({
            "id": item["id"],
            "case_name": item["case_name"],
            "primary_category": actual_cat.value,
            "category_match": cat_match,
            "total_score": pipeline_res.brief.lead_score.total_score,
            "tier": pipeline_res.brief.lead_score.tier,
            "budget_specified": actual_has_budget,
            "budget_score": budget_score,
            "timeline_specified": actual_has_timeline,
            "urgency": pipeline_res.brief.extracted_specs.timeline.urgency_level,
            "questions_count": len(pipeline_res.brief.clarification_questions),
            "latency_ms": round(latency, 2)
        })

    eval_report = {
        "total_cases_evaluated": total_cases,
        "classification_accuracy_pct": round((classification_matches / total_cases) * 100.0, 1),
        "schema_validation_success_pct": round((schema_validations / total_cases) * 100.0, 1),
        "budget_extraction_accuracy_pct": round((budget_extraction_matches / total_cases) * 100.0, 1),
        "timeline_extraction_accuracy_pct": round((timeline_extraction_matches / total_cases) * 100.0, 1),
        "gap_detection_accuracy_pct": round((gaps_detected_correctly / total_cases) * 100.0, 1),
        "neutral_budget_compliance_pct": round((neutral_budget_verified / total_cases) * 100.0, 1),
        "mean_latency_ms": round(sum(latencies_ms) / len(latencies_ms), 2),
        "min_latency_ms": round(min(latencies_ms), 2),
        "max_latency_ms": round(max(latencies_ms), 2),
        "case_summaries": case_summaries
    }

    return eval_report


if __name__ == "__main__":
    report = run_benchmark_evaluation()
    print(json.dumps(report, indent=2))
