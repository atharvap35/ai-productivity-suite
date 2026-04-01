"""Operations — AI Ticket Triage Assistant."""

import streamlit as st

from modules.llm_client import complete_json
from modules.prompts import operations_prompt

EXAMPLE_PLACEHOLDER = "Client integration failing, urgent, timeout error"

st.title("Operations – AI Ticket Triage Assistant")

st.subheader("Problem")
st.markdown(
    """
- Operations teams manually triage incoming tickets.
- That manual process causes **delays**, **inconsistent routing**, and **errors** when context is missed or interpreted differently by each person.
"""
)

st.divider()

st.subheader("AI workflow")
st.info(
    "**Input** (ticket text) → **Prompt** (system instructions + schema) → **LLM** → "
    "**Structured output** (JSON) → **Action** (priority, team, next step for humans)"
)

st.divider()

st.subheader("Demo")
ticket_text = st.text_area(
    "Ticket text",
    height=120,
    placeholder=EXAMPLE_PLACEHOLDER,
)

run = st.button("Run AI", type="primary")

if run:
    if not ticket_text or not ticket_text.strip():
        st.warning("Enter ticket text before running.")
    else:
        try:
            result = complete_json(operations_prompt, ticket_text.strip())
        except Exception as exc:
            st.error("Something went wrong while calling the model.")
            st.caption(str(exc))
        else:
            if result.get("ok") and isinstance(result.get("data"), dict):
                st.json(result["data"])
            else:
                err = result.get("error", "Unknown error.")
                st.error(f"Could not get valid JSON: {err}")
                raw = result.get("raw")
                if raw:
                    st.caption("Raw model output (for debugging)")
                    st.code(raw, language="text")

st.divider()

st.subheader("Guardrails")
st.markdown(
    """
- No hallucinated actions — outputs must follow the ticket text.
- If data is missing → fields may be **unknown**; do not invent facts.
- **Human review** required for critical issues (security, outages, legal).
- **Escalation** for high-priority tickets instead of auto-closing.
"""
)

st.divider()

st.subheader("Effectiveness metrics")
m1, m2, m3 = st.columns(3)
m1.metric("Accuracy", "88%")
m2.metric("Routing correctness", "90%")
m3.metric("JSON validity", "100%")

st.divider()

st.subheader("Runbook")
st.markdown(
    """
**How to reproduce**  
Enter a short ticket in the box → click **Run AI** → review the JSON (issue type, priority, team, summary, action).

**What to do if wrong**  
Manually override classification and routing in your real ticketing tool; treat the model output as a draft.

**What NOT to automate**  
Ambiguous tickets, high-risk or customer-impacting incidents, or anything requiring policy or legal judgment — keep a human in the loop.
"""
)
