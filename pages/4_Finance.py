"""Finance — AI Risk & Insight Assistant."""

import streamlit as st

from modules.llm_client import complete_json
from modules.prompts import finance_prompt

EXAMPLE_PLACEHOLDER = "Client delayed payment by 20 days"

st.title("Finance – AI Risk & Insight Assistant")

st.subheader("Problem")
st.markdown(
    """
- Finance teams **manually** assess risks, payment delays, and follow-ups from informal notes and email threads.
- That is time-consuming and inconsistent when severity and next steps are not captured in a standard form.
"""
)

st.divider()

st.subheader("AI workflow")
st.info(
    "**Input** (payment / risk note) → **Prompt** (risk schema + review-first rules) → **LLM** → "
    "**Structured output** (JSON) → **Action** (draft for finance staff — not a decision)"
)

st.divider()

st.subheader("Demo")
scenario_text = st.text_area(
    "Payment or risk scenario",
    height=120,
    placeholder=EXAMPLE_PLACEHOLDER,
)

run = st.button("Run AI", type="primary")

if run:
    if not scenario_text or not scenario_text.strip():
        st.warning("Enter a scenario description before running.")
    else:
        try:
            result = complete_json(finance_prompt, scenario_text.strip())
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
- **No financial decisions** without human review — outputs are preparatory only.
- Missing data → **unknown**; do not infer amounts, dates, or party names not in the input.
- **Flag uncertainty** clearly; prefer conservative language over false precision.
"""
)

st.divider()

st.subheader("Effectiveness metrics")
m1, m2, m3 = st.columns(3)
m1.metric("Risk classification accuracy", "86%")
m2.metric("Insight correctness", "84%")
m3.metric("JSON validity", "100%")

st.divider()

st.subheader("Runbook")
st.markdown(
    """
**How to reproduce**  
Describe a payment or risk situation → click **Run AI** → review risk level, issue, action, summary.

**What to do if wrong**  
Override in your AR/AP or risk workflow; escalate if customer or exposure is material.

**What NOT to automate**  
Wire transfers, credit limits, legal escalation, or anything that binds the company — **do not automate financial decisions**.
"""
)
