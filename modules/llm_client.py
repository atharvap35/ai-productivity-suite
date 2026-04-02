"""LLM client (EC2 demo mode): descriptive structured outputs"""

from typing import Dict, Any


def is_llm_configured() -> bool:
    return True


# -------------------------
# OPERATIONS
# -------------------------

def _mock_operations(user_input: str) -> Dict[str, Any]:
    return {
        "decision": "Escalate integration/system issue",

        "reasoning": "Detected failure indicators and operational disruption requiring immediate attention",

        "impact": {
            "systems_affected": "Core integration services",
            "user_impact": "Multiple users potentially impacted",
            "severity": "High"
        },

        "recommended_actions": [
            {
                "action": "Immediate Escalation",
                "details": "Assign issue to engineering team with highest priority"
            },
            {
                "action": "Incident Creation",
                "details": "Log detailed incident with timestamps and error context"
            },
            {
                "action": "Stakeholder Communication",
                "details": "Notify internal teams and affected stakeholders"
            }
        ],

        "next_steps_priority": [
            "Escalate issue",
            "Create incident log",
            "Notify stakeholders"
        ],

        "summary": f"Operational issue detected: {user_input}",

        "confidence": "High"
    }


# -------------------------
# SALES
# -------------------------

def _mock_sales(user_input: str) -> Dict[str, Any]:
    return {
        "decision": "Move deal forward to negotiation",

        "reasoning": "Customer shows intent but has objections that need resolution",

        "impact": {
            "deal_value": "Potentially significant",
            "conversion_probability": "Medium",
            "risk": "Delay due to objections"
        },

        "recommended_actions": [
            {
                "action": "Handle Objections",
                "details": "Address pricing or feature concerns with tailored messaging"
            },
            {
                "action": "Follow-Up",
                "details": "Schedule next interaction within a defined timeline"
            },
            {
                "action": "CRM Update",
                "details": "Log notes and update deal stage in CRM"
            }
        ],

        "next_steps_priority": [
            "Resolve concerns",
            "Schedule follow-up",
            "Update CRM"
        ],

        "summary": f"Sales progression insight: {user_input}",

        "confidence": "Medium"
    }


# -------------------------
# MARKETING
# -------------------------

def _mock_marketing(user_input: str) -> Dict[str, Any]:
    return {
        "decision": "Launch structured multi-channel campaign",

        "reasoning": "Campaign goal requires reach, experimentation, and targeted messaging",

        "impact": {
            "reach": "High",
            "engagement": "Moderate to high",
            "cost": "Moderate"
        },

        "recommended_actions": [
            {
                "action": "Define Messaging",
                "details": "Focus on core product value propositions"
            },
            {
                "action": "Channel Execution",
                "details": "Use Email, LinkedIn, and Paid Ads"
            },
            {
                "action": "Experimentation",
                "details": "Run A/B tests on creatives and messaging"
            }
        ],

        "next_steps_priority": [
            "Finalize messaging",
            "Launch campaign",
            "Measure performance"
        ],

        "summary": f"Marketing strategy created: {user_input}",

        "confidence": "Medium"
    }


# -------------------------
# FINANCE
# -------------------------

def _mock_finance(user_input: str) -> Dict[str, Any]:
    return {
        "decision": "Treat as high-risk payroll/financial disruption",

        "reasoning": "Salary/payment delays directly impact employees and organizational trust",

        "impact": {
            "employees_affected": "Multiple employees",
            "business_risk": "Reputation damage and HR escalation",
            "urgency": "High"
        },

        "recommended_actions": [
            {
                "action": "Official Communication",
                "details": "Send clear and transparent communication to all affected employees"
            },
            {
                "action": "Bank Coordination",
                "details": "Engage with bank to confirm issue and expected resolution timeline"
            },
            {
                "action": "Contingency Planning",
                "details": "Prepare manual transfers or temporary advances if delays persist"
            },
            {
                "action": "Documentation",
                "details": "Log all communication and errors for compliance and reimbursement cases"
            }
        ],

        "next_steps_priority": [
            "Notify employees",
            "Confirm issue with bank",
            "Track resolution timeline"
        ],

        "summary": f"Critical financial issue detected: {user_input}",

        "confidence": "High"
    }


# -------------------------
# MAIN FUNCTION
# -------------------------

def complete_json(system_prompt: str, user_input: str, *args, **kwargs) -> Dict[str, Any]:
    prompt = system_prompt.lower()

    if "operations" in prompt:
        data = _mock_operations(user_input)

    elif "sales" in prompt:
        data = _mock_sales(user_input)

    elif "marketing" in prompt or "gtm" in prompt:
        data = _mock_marketing(user_input)

    elif "finance" in prompt:
        data = _mock_finance(user_input)

    else:
        data = {
            "decision": "Generic analysis",
            "summary": user_input
        }

    return {"ok": True, "data": data}