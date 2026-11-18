"""Unit tests for the Cynbit service classifier."""

from src.config import CynbitServiceCategory
from src.pipeline.classifier import classify_inquiry, is_malformed_input


def test_classify_ai_agent():
    text = "We want to build an autonomous multi-agent workflow using RAG and LangChain with tool-calling."
    cls = classify_inquiry(text)
    assert cls.primary_category == CynbitServiceCategory.AUTONOMOUS_AI_AGENTS
    assert cls.confidence >= 0.70


def test_classify_scalable_software():
    text = "Looking for a full-stack engineering team to build a Next.js frontend with FastAPI backend and PostgreSQL."
    cls = classify_inquiry(text)
    assert cls.primary_category == CynbitServiceCategory.SCALABLE_SOFTWARE
    assert cls.confidence >= 0.70


def test_classify_cloud_migration():
    text = "We need to migrate our infrastructure to AWS EKS using Kubernetes, Terraform, and Docker with CI/CD."
    cls = classify_inquiry(text)
    assert cls.primary_category == CynbitServiceCategory.CLOUD_DEVOPS
    assert cls.confidence >= 0.70


def test_classify_tenantease_product():
    text = "We are interested in licensing or extending TenantEase for our residential property portfolio."
    cls = classify_inquiry(text)
    assert cls.primary_category == CynbitServiceCategory.PROPRIETARY_SUITE
    assert cls.confidence >= 0.70


def test_classify_out_of_scope_hardware():
    text = "We need PCB circuit boards manufactured with physical soldering, hydraulic plumbing, and plastic molds."
    cls = classify_inquiry(text)
    assert cls.primary_category == CynbitServiceCategory.OUT_OF_SCOPE


def test_is_malformed_input_gibberish():
    gibberish = "asdfghjkl;;;;; 1234567890 DROP TABLE leads; <script>alert(1)</script>"
    assert is_malformed_input(gibberish) is True
    cls = classify_inquiry(gibberish)
    assert cls.primary_category == CynbitServiceCategory.OUT_OF_SCOPE
