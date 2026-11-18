"""
Pydantic v2 schemas defining all data contracts across the Cynbit Discovery Copilot pipeline.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.config import CynbitServiceCategory


class InquiryInput(BaseModel):
    """Raw client inquiry input payload."""
    inquiry_id: str = Field(default_factory=lambda: f"INQ-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    client_name: Optional[str] = Field(default="Prospective Client", description="Client or contact name")
    client_email: Optional[str] = Field(default="", description="Contact email address")
    company_name: Optional[str] = Field(default="", description="Client organization name")
    inquiry_text: str = Field(..., min_length=1, description="Raw unstructured text of the inquiry")
    submission_channel: str = Field(default="Web Contact Form", description="Origin of inquiry (Email, Form, RFP)")
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceClassification(BaseModel):
    """Classification of the inquiry against Cynbit's service taxonomy."""
    primary_category: CynbitServiceCategory = Field(..., description="Dominant Cynbit service vertical")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of classification")
    secondary_categories: List[CynbitServiceCategory] = Field(default_factory=list, description="Secondary services if multi-disciplinary")
    rationale: str = Field(default="", description="Explainable justification for the classification")


class BudgetInfo(BaseModel):
    """Extracted budget information."""
    raw_budget: Optional[str] = Field(default=None, description="Verbatim budget expression from inquiry")
    currency: Optional[str] = Field(default=None, description="Detected currency (e.g. USD, EUR, INR)")
    estimated_min: Optional[float] = Field(default=None, description="Lower bound of budget estimate")
    estimated_max: Optional[float] = Field(default=None, description="Upper bound of budget estimate")
    is_specified: bool = Field(default=False, description="True if a budget was explicitly provided")
    feasibility_notes: str = Field(default="Budget not specified; requires discovery discussion.", description="Assessment of budget realism")


class TimelineInfo(BaseModel):
    """Extracted timeline information."""
    raw_timeline: Optional[str] = Field(default=None, description="Verbatim timeline expression from inquiry")
    estimated_weeks: Optional[float] = Field(default=None, description="Estimated duration in weeks")
    is_specified: bool = Field(default=False, description="True if a timeline was explicitly stated")
    urgency_level: Literal["relaxed", "moderate", "urgent", "unrealistic", "unspecified"] = Field(
        default="unspecified", description="Urgency classification"
    )
    feasibility_notes: str = Field(default="Timeline not stated; requires scoping.", description="Assessment of timeline feasibility")


class ExtractedRequirements(BaseModel):
    """Structured technical specifications extracted from unstructured text."""
    core_requirements: List[str] = Field(default_factory=list, description="Explicit technical deliverables or functional goals")
    suggested_tech_stack: List[str] = Field(default_factory=list, description="Detected or recommended technologies")
    budget: BudgetInfo = Field(default_factory=BudgetInfo)
    timeline: TimelineInfo = Field(default_factory=TimelineInfo)
    client_type: Literal["enterprise", "smb", "startup", "individual", "unknown"] = Field(
        default="unknown", description="Deduced organization type"
    )
    domain_industry: Optional[str] = Field(default="Technology / General", description="Detected industry vertical")


class MissingInfoAnalysis(BaseModel):
    """Analysis of gaps, ambiguities, and missing specifications in the inquiry."""
    missing_fields: List[str] = Field(default_factory=list, description="Standard parameters omitted (e.g., budget, timeline, auth requirements)")
    ambiguities: List[str] = Field(default_factory=list, description="Vague or ambiguous phrases needing technical definition")
    technical_risks: List[str] = Field(default_factory=list, description="Potential delivery, integration, or compliance risks detected")
    has_critical_gaps: bool = Field(default=False, description="True if critical information is missing to formulate a proposal")


class ClarificationQuestion(BaseModel):
    """Targeted question to ask the prospective client during discovery."""
    id: int = Field(..., description="Question index")
    topic: str = Field(..., description="Dimension addressed (e.g. Architecture, Scale, Budget, Compliance)")
    question: str = Field(..., description="The direct question formulated for the client")
    justification: str = Field(..., description="Why Cynbit solutions architects need this detail")
    priority: Literal["high", "medium", "low"] = Field(default="medium")


class ScoreBreakdown(BaseModel):
    """
    Transparent 4-Factor Heuristic Lead Qualification Score.
    
    IMPORTANT REFINEMENT:
    This is an explainable heuristic rubric, NOT a trained predictive ML model.
    Unspecified information (budget/timeline) is treated neutrally rather than penalized.
    """
    technical_fit_score: float = Field(..., ge=0.0, le=100.0, description="Alignment with Cynbit's core pillars")
    scope_clarity_score: float = Field(..., ge=0.0, le=100.0, description="Specificity and completeness of technical scope")
    budget_viability_score: float = Field(..., ge=0.0, le=100.0, description="Budget feasibility (neutral if unspecified)")
    timeline_readiness_score: float = Field(..., ge=0.0, le=100.0, description="Feasibility of delivery schedule (neutral if unspecified)")
    total_score: float = Field(..., ge=0.0, le=100.0, description="Weighted composite score")
    
    tier: Literal[
        "Tier 1: High Priority Discovery",
        "Tier 2: Discovery & Scoping Required",
        "Tier 3: Exploratory / Advisory Review"
    ] = Field(..., description="Operational triage classification")
    
    is_heuristic: bool = Field(default=True, description="Flag explicitly confirming this is a rule-based heuristic rubric")
    scoring_explanation: List[str] = Field(default_factory=list, description="Auditable step-by-step rationale for each score component")
    recommended_human_action: str = Field(..., description="Actionable next step for Cynbit solutions team (never auto-rejects)")


class DiscoveryBrief(BaseModel):
    """Structured internal discovery document for Cynbit solutions architects."""
    inquiry_id: str
    client_name: str
    company_name: str
    generated_at: str
    executive_summary: str
    classification: ServiceClassification
    extracted_specs: ExtractedRequirements
    missing_info: MissingInfoAnalysis
    lead_score: ScoreBreakdown
    recommended_cynbit_architecture: str
    recommended_cynbit_services: List[str]
    clarification_questions: List[ClarificationQuestion]
    suggested_next_steps: List[str]


class CustomerResponseDraft(BaseModel):
    """Drafted personalized customer response for human review and sending."""
    subject_line: str
    salutation: str
    acknowledgment: str
    value_proposition: str
    clarification_points: List[str]
    call_to_action: str
    full_email_body: str


class PipelineResult(BaseModel):
    """Complete aggregated output of the Discovery Copilot pipeline."""
    inquiry: InquiryInput
    brief: DiscoveryBrief
    response_draft: CustomerResponseDraft
    engine_used: Literal["gemini", "deterministic_fallback"]
    processing_time_ms: float
    raw_model_response: Optional[str] = None
