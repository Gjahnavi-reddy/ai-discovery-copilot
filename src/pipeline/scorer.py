"""
Explainable Lead Qualification Scoring Engine for Cynbit AI Discovery Copilot.

CRITICAL DESIGN REFINEMENTS:
1. This is a transparent, auditable heuristic rubric, NOT a trained predictive ML model.
2. Missing/unstated information (budget, timeline) is treated neutrally (65.0) rather
   than penalized as negative.
3. No automated rejection or disqualification. All tiers route to human review with
   specific operational recommendations.
"""

from typing import List, Tuple
from src.config import CynbitServiceCategory, ScoringWeights
from src.models.schemas import (
    ExtractedRequirements,
    ServiceClassification,
    MissingInfoAnalysis,
    ScoreBreakdown,
)


def compute_lead_score(
    classification: ServiceClassification,
    specs: ExtractedRequirements,
    gaps: MissingInfoAnalysis,
    weights: ScoringWeights = ScoringWeights()
) -> ScoreBreakdown:
    """
    Compute transparent 4-factor heuristic lead qualification score.
    Returns ScoreBreakdown with itemized sub-scores, mathematical derivation,
    and recommended human actions.
    """
    explanations: List[str] = []

    # -------------------------------------------------------------
    # 1. Technical Fit Score (Weight: 35%)
    # -------------------------------------------------------------
    cat = classification.primary_category
    if cat == CynbitServiceCategory.OUT_OF_SCOPE:
        tech_fit = 20.0
        explanations.append(
            f"Technical Fit ({tech_fit:.1f}/100): Out of Scope. Inquiry keywords do not match Cynbit's "
            "software, AI, cloud, or SEO engineering services."
        )
    elif cat in [
        CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        CynbitServiceCategory.SCALABLE_SOFTWARE,
        CynbitServiceCategory.CLOUD_DEVOPS,
        CynbitServiceCategory.PROPRIETARY_SUITE
    ]:
        tech_fit = 90.0
        # Multi-disciplinary synergy bonus
        if len(classification.secondary_categories) > 0:
            tech_fit = min(100.0, tech_fit + 5.0)
            explanations.append(
                f"Technical Fit ({tech_fit:.1f}/100): High Alignment. Project directly leverages Cynbit's core "
                f"strengths in {cat.value} with multi-disciplinary extensions."
            )
        else:
            explanations.append(
                f"Technical Fit ({tech_fit:.1f}/100): Strong Alignment with Cynbit's primary {cat.value} practice."
            )
    elif cat == CynbitServiceCategory.TECHNICAL_SEO_GROWTH:
        tech_fit = 80.0
        explanations.append(
            f"Technical Fit ({tech_fit:.1f}/100): Good Alignment with Cynbit's Technical SEO & Growth Engineering practice."
        )
    else:
        tech_fit = 50.0
        explanations.append(f"Technical Fit ({tech_fit:.1f}/100): Moderate alignment; domain boundaries require clarification.")

    # -------------------------------------------------------------
    # 2. Scope Clarity Score (Weight: 30%)
    # -------------------------------------------------------------
    num_deliverables = len(specs.core_requirements)
    num_tech = len(specs.suggested_tech_stack)
    num_ambiguities = len(gaps.ambiguities)

    if cat == CynbitServiceCategory.OUT_OF_SCOPE:
        scope_clarity = 25.0
        explanations.append(
            f"Scope Clarity ({scope_clarity:.1f}/100): Requirements describe out-of-scope non-software deliverables."
        )
    else:
        if num_deliverables >= 3 and num_tech >= 3:
            raw_scope = 95.0
        elif num_deliverables >= 2 or num_tech >= 2:
            raw_scope = 80.0
        elif num_deliverables >= 1:
            raw_scope = 60.0
        else:
            raw_scope = 30.0

        # Penalize for severe ambiguities
        scope_clarity = max(15.0, raw_scope - (num_ambiguities * 12.0))
        explanations.append(
            f"Scope Clarity ({scope_clarity:.1f}/100): Detected {num_deliverables} core deliverable(s) "
            f"and {num_tech} specific technical requirement(s). "
            f"{f'Deducted {num_ambiguities * 12.0} pts for {num_ambiguities} detected ambiguities.' if num_ambiguities > 0 else 'Clear technical objectives.'}"
        )

    # -------------------------------------------------------------
    # 3. Budget Viability Score (Weight: 20%)
    # REFINEMENT #2: Unknown budget is NEUTRAL, not penalized!
    # -------------------------------------------------------------
    if not specs.budget.is_specified:
        budget_score = weights.NEUTRAL_UNSPECIFIED_SCORE  # 65.0
        explanations.append(
            f"Budget Viability ({budget_score:.1f}/100): Neutral (Unspecified). Missing budget is treated as "
            "unknown rather than negative; financial scope will be established during discovery."
        )
    else:
        min_b = specs.budget.estimated_min or 0.0
        if min_b >= 30000.0:
            budget_score = 95.0
            explanations.append(
                f"Budget Viability ({budget_score:.1f}/100): Commercial Viability. Stated budget ({specs.budget.raw_budget}) "
                "comfortably meets Cynbit's typical project scale."
            )
        elif min_b >= 15000.0:
            budget_score = 85.0
            explanations.append(
                f"Budget Viability ({budget_score:.1f}/100): Viable for targeted MVP or modular release ({specs.budget.raw_budget})."
            )
        elif min_b >= 5000.0:
            budget_score = 65.0
            explanations.append(
                f"Budget Viability ({budget_score:.1f}/100): Moderate. Budget is constrained ({specs.budget.raw_budget}); "
                "recommending phased milestones."
            )
        else:
            budget_score = 40.0
            explanations.append(
                f"Budget Viability ({budget_score:.1f}/100): Stated budget ({specs.budget.raw_budget}) is below "
                "standard bespoke engineering thresholds; will require scope adjustment."
            )

    # -------------------------------------------------------------
    # 4. Timeline Readiness Score (Weight: 15%)
    # REFINEMENT #2: Unknown timeline is NEUTRAL, not penalized!
    # -------------------------------------------------------------
    if not specs.timeline.is_specified:
        timeline_score = weights.NEUTRAL_UNSPECIFIED_SCORE  # 65.0
        explanations.append(
            f"Timeline Readiness ({timeline_score:.1f}/100): Neutral (Unspecified). No fixed deadline stated; "
            "timeline will be defined during technical scoping."
        )
    elif specs.timeline.urgency_level == "unrealistic":
        timeline_score = 35.0
        explanations.append(
            f"Timeline Readiness ({timeline_score:.1f}/100): Critical Scheduling Risk. Stated timeline "
            f"('{specs.timeline.raw_timeline}') is technically unfeasible for the requested scope."
        )
    elif specs.timeline.urgency_level in ["moderate", "relaxed"]:
        timeline_score = 90.0
        explanations.append(
            f"Timeline Readiness ({timeline_score:.1f}/100): Realistic Schedule. Stated delivery timeframe "
            f"('{specs.timeline.raw_timeline}') allows standard sprint and QA cycles."
        )
    elif specs.timeline.urgency_level == "urgent":
        timeline_score = 75.0
        explanations.append(
            f"Timeline Readiness ({timeline_score:.1f}/100): Accelerated Schedule. Requires fast-tracked sprints."
        )
    else:
        timeline_score = 65.0
        explanations.append(f"Timeline Readiness ({timeline_score:.1f}/100): Standard schedule evaluation.")

    # -------------------------------------------------------------
    # Composite Weighted Total & Safety Constraints
    # -------------------------------------------------------------
    total = (
        (tech_fit * weights.TECHNICAL_FIT) +
        (scope_clarity * weights.SCOPE_CLARITY) +
        (budget_score * weights.BUDGET_VIABILITY) +
        (timeline_score * weights.TIMELINE_READINESS)
    )

    # If critical delivery risk detected (e.g. unrealistic timeline), cap at Tier 2 boundary
    if specs.timeline.urgency_level == "unrealistic" and total >= 75.0:
        total = 72.0
        explanations.append(
            "Overall score capped at 72.0 (Tier 2: Discovery & Scoping Required) due to critical "
            "delivery schedule unfeasibility requiring architectural de-risking."
        )

    total_score = round(max(0.0, min(100.0, total)), 1)

    # -------------------------------------------------------------
    # Tier Assignment & Human Action (REFINEMENT #3: NEVER Auto-Reject!)
    # -------------------------------------------------------------
    if total_score >= 75.0:
        tier = "Tier 1: High Priority Discovery"
        action = (
            "Schedule priority Technical Discovery & Solution Architecture session with a Senior Solutions Architect. "
            "Prepare tailored architecture proposal using the generated Discovery Brief."
        )
    elif total_score >= 50.0:
        tier = "Tier 2: Discovery & Scoping Required"
        action = (
            "Initiate discovery follow-up. Send the drafted clarification questions to address unspecified "
            "scope/budget/timeline variables before committing engineering resources."
        )
    else:
        tier = "Tier 3: Exploratory / Advisory Review"
        action = (
            "Route for manual review by Account Executive / Solutions Lead. Evaluate whether inquiry can be "
            "realigned with Cynbit educational initiatives (BitElevate), self-service resources, or politely redirected."
        )

    return ScoreBreakdown(
        technical_fit_score=round(tech_fit, 1),
        scope_clarity_score=round(scope_clarity, 1),
        budget_viability_score=round(budget_score, 1),
        timeline_readiness_score=round(timeline_score, 1),
        total_score=total_score,
        tier=tier,
        is_heuristic=True,
        scoring_explanation=explanations,
        recommended_human_action=action
    )
