"""
Synthetic Benchmark Dataset for Cynbit AI Discovery Copilot.

Includes 10 diverse cases covering the exact requirements from Refinement #6:
1. High-quality AI automation inquiry
2. Full-stack application inquiry
3. Cloud migration inquiry
4. Incomplete inquiry
5. Budget unspecified
6. Unrealistic timeline
7. Multiple-service inquiry
8. Ambiguous inquiry
9. Out-of-scope inquiry
10. Malformed input
"""

from typing import List, Dict, Any, Optional
from src.config import CynbitServiceCategory


BENCHMARK_INQUIRIES: List[Dict[str, Any]] = [
    {
        "id": "CASE-01-AI-AUTOMATION",
        "case_name": "High-Quality AI Automation Inquiry",
        "client_name": "Marcus Vance",
        "client_email": "m.vance@fintechedge.io",
        "company_name": "FinTech Edge Labs",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "Hi Cynbit Team, we are seeking an engineering partner to design and build an autonomous "
            "multi-agent customer operations workflow for our fintech platform. "
            "Specifically, we need an intelligent agent layer that ingests tier-2 support tickets from Zendesk, "
            "executes semantic search over our internal Confluence & Postgres knowledge base using RAG, "
            "verifies account state via our internal REST APIs with function-calling, and drafts or executes "
            "automated resolution workflows with a human-in-the-loop review interface. "
            "We anticipate handling approximately 50,000 monthly interactions. "
            "We have allocated a dedicated budget of $35,000 to $45,000 for this phase and want to complete "
            "the implementation across a 12-week schedule with bi-weekly sprint demos. "
            "Looking forward to scheduling a technical discovery session."
        ),
        "expected_primary_category": CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        "expected_tier": "Tier 1: High Priority Discovery",
        "expected_characteristics": {
            "has_budget": True,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": False,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-02-FULLSTACK",
        "case_name": "Full-Stack Application Inquiry",
        "client_name": "Elena Rostova",
        "client_email": "elena@collabpulse.app",
        "company_name": "CollabPulse Inc.",
        "submission_channel": "Direct Email",
        "inquiry_text": (
            "Hello, we are launching a collaborative document workspace for remote engineering teams. "
            "We need full-stack product development to build the core MVP. "
            "The stack should be Next.js with TypeScript on the frontend, FastAPI (Python) on the backend, "
            "PostgreSQL for relational metadata, and Redis with WebSockets for real-time multiplayer cursor "
            "and editing synchronization. "
            "We already have Figma designs completed for 12 key screens. "
            "Our budget is $25,000 and we are aiming for a beta release in 10 weeks. "
            "Does Cynbit have capacity to take on full frontend and backend engineering?"
        ),
        "expected_primary_category": CynbitServiceCategory.SCALABLE_SOFTWARE,
        "expected_tier": "Tier 1: High Priority Discovery",
        "expected_characteristics": {
            "has_budget": True,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": False,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-03-CLOUD-MIGRATION",
        "case_name": "Cloud Migration Inquiry",
        "client_name": "David Chen",
        "client_email": "dchen@logisticsflow.net",
        "company_name": "LogisticsFlow Systems",
        "submission_channel": "RFP Portal",
        "inquiry_text": (
            "Dear Cynbit Architecture Group, our legacy on-premise supply chain tracking system (running on "
            "bare-metal CentOS VMs) needs to be modernized and migrated to AWS. "
            "We require containerization with Docker, deployment on Amazon EKS (Kubernetes), infrastructure as "
            "code using Terraform, and setup of GitHub Actions CI/CD pipelines with zero-downtime rolling updates. "
            "System handles 2M daily telemetry events. We have an approved enterprise infrastructure budget "
            "of $40,000 and need the migration executed over the next 8 weeks."
        ),
        "expected_primary_category": CynbitServiceCategory.CLOUD_DEVOPS,
        "expected_tier": "Tier 1: High Priority Discovery",
        "expected_characteristics": {
            "has_budget": True,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": False,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-04-INCOMPLETE",
        "case_name": "Incomplete Inquiry",
        "client_name": "Alex K.",
        "client_email": "alexk992@gmail.com",
        "company_name": "Unspecified",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "Need an app built. Please let me know how much it will cost and how fast you can do it."
        ),
        "expected_primary_category": CynbitServiceCategory.SCALABLE_SOFTWARE,
        "expected_tier": "Tier 2: Discovery & Scoping Required",
        "expected_characteristics": {
            "has_budget": False,
            "has_timeline": False,
            "is_out_of_scope": False,
            "has_critical_gaps": True,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-05-BUDGET-UNSPECIFIED",
        "case_name": "Budget Unspecified Inquiry",
        "client_name": "Sarah Jenkins",
        "client_email": "sjenkins@apexproperties.co",
        "company_name": "Apex Commercial Properties",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "Hello, we manage 45 commercial properties and are exploring a customized property and tenant "
            "management portal. We saw your TenantEase platform and want to understand if we can license it or "
            "have Cynbit develop a white-labeled custom module for automated lease renewals, tenant communication, "
            "and maintenance ticket tracking with Stripe payment gateway integration. "
            "We have an active engineering steering committee and want to roll this out within 14 weeks. "
            "We do not have a fixed budget line yet and are relying on Cynbit to provide an architectural estimate "
            "and tier recommendations based on the discovery scope."
        ),
        "expected_primary_category": CynbitServiceCategory.PROPRIETARY_SUITE,
        "expected_tier": "Tier 1: High Priority Discovery",  # Or Tier 2, but NOT penalized for missing budget!
        "expected_characteristics": {
            "has_budget": False,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": False,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-06-UNREALISTIC-TIMELINE",
        "case_name": "Unrealistic Timeline Inquiry",
        "client_name": "Jason Todd",
        "client_email": "jtodd@rushlaw.com",
        "company_name": "Rush Law Group",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "We need an enterprise autonomous AI legal contract analyzer that parses 500-page loan covenants, "
            "flags non-standard indemnification clauses, integrates with Microsoft Word, and passes SOC2 Type II "
            "security compliance. We have $15,000 budget and we need the full production solution fully deployed "
            "and verified by this coming Monday (3 days from now) for a major closing."
        ),
        "expected_primary_category": CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        "expected_tier": "Tier 2: Discovery & Scoping Required",  # Timeline unrealistic, needs scoping discussion
        "expected_characteristics": {
            "has_budget": True,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": True,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-07-MULTI-SERVICE",
        "case_name": "Multiple-Service Inquiry",
        "client_name": "Priya Sharma",
        "client_email": "priya@luxecommerce.in",
        "company_name": "LuxeCommerce Retail",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "We are overhauling our omnichannel retail presence. We need: "
            "1) An autonomous AI recommendation and customer re-engagement agent. "
            "2) A complete full-stack storefront rebuild on Next.js with headless Shopify backend. "
            "3) Cloud infrastructure deployment on AWS with multi-region CDN and auto-scaling. "
            "4) A technical SEO and Core Web Vitals overhaul to improve organic search rankings. "
            "Our budget is $60,000 across all four workstreams with an estimated rollout of 16 weeks. "
            "Can Cynbit handle all four engineering disciplines under one unified discovery brief?"
        ),
        "expected_primary_category": [
            CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
            CynbitServiceCategory.TECHNICAL_SEO_GROWTH,
            CynbitServiceCategory.SCALABLE_SOFTWARE,
            CynbitServiceCategory.CLOUD_DEVOPS,
        ],
        "expected_tier": "Tier 1: High Priority Discovery",
        "expected_characteristics": {
            "has_budget": True,
            "has_timeline": True,
            "is_out_of_scope": False,
            "has_critical_gaps": False,
            "is_malformed": False,
            "is_multi_service": True,
        }
    },
    {
        "id": "CASE-08-AMBIGUOUS",
        "case_name": "Ambiguous Inquiry",
        "client_name": "Jordan Bell",
        "client_email": "jbell@futuretrendz.org",
        "company_name": "FutureTrendz",
        "submission_channel": "Direct Email",
        "inquiry_text": (
            "We want to do something big with AI and maybe blockchain or quantum to disrupt the marketing industry. "
            "Our investors told us we should have an agentic workflow or intelligent bot that automates growth. "
            "We have lots of ideas but no technical specs. We have some seed funding available. What do you guys build?"
        ),
        "expected_primary_category": CynbitServiceCategory.AUTONOMOUS_AI_AGENTS,
        "expected_tier": "Tier 2: Discovery & Scoping Required",
        "expected_characteristics": {
            "has_budget": False,
            "has_timeline": False,
            "is_out_of_scope": False,
            "has_critical_gaps": True,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-09-OUT-OF-SCOPE",
        "case_name": "Out-of-Scope Inquiry",
        "client_name": "Robert Miller",
        "client_email": "rmiller@millermfg.com",
        "company_name": "Miller Hardware Works",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "We are seeking an industrial manufacturing partner to design custom silicon PCB circuit boards, "
            "solder micro-controllers, and fabricate 10,000 physical plastic enclosure units in a factory warehouse. "
            "We also need physical plumbing and hydraulic pipe installation for our warehouse facility."
        ),
        "expected_primary_category": CynbitServiceCategory.OUT_OF_SCOPE,
        "expected_tier": "Tier 3: Exploratory / Advisory Review",
        "expected_characteristics": {
            "has_budget": False,
            "has_timeline": False,
            "is_out_of_scope": True,
            "has_critical_gaps": True,
            "is_malformed": False,
        }
    },
    {
        "id": "CASE-10-MALFORMED",
        "case_name": "Malformed / Adversarial Input",
        "client_name": "Unknown",
        "client_email": "test@test",
        "company_name": "N/A",
        "submission_channel": "Web Contact Form",
        "inquiry_text": (
            "asdfghjkl;;;;; 1234567890 DROP TABLE leads; SELECT * FROM users; "
            "<script>alert('xss')</script> $$$$$$$$$$ !!!!!!!! test test test"
        ),
        "expected_primary_category": CynbitServiceCategory.OUT_OF_SCOPE,
        "expected_tier": "Tier 3: Exploratory / Advisory Review",
        "expected_characteristics": {
            "has_budget": False,
            "has_timeline": False,
            "is_out_of_scope": True,
            "has_critical_gaps": True,
            "is_malformed": True,
        }
    }
]


def get_benchmark_by_id(benchmark_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a benchmark case by ID."""
    for item in BENCHMARK_INQUIRIES:
        if item["id"] == benchmark_id:
            return item
    return None
