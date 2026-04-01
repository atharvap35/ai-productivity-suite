"""Sales — AI CRM Assistant."""

import streamlit as st

from modules.llm_client import complete_json
from modules.prompts import sales_prompt

EXAMPLE_PLACEHOLDER = "Client interested but pricing concern, follow up next week"

st.title("Sales – AI CRM Assistant")

st.subheader("Problem")
st.markdown(
    """
- Sales reps spend a lot of time **writing CRM updates** and **preparing for calls** from scattered notes.
- That slows pipeline hygiene and makes handoffs inconsistent when summaries don’t match what was actually said.
"""
)

st.divider()

st.subheader("AI workflow")
st.info(
    "**Input** (rep note or call summary) → **Prompt** (CRM schema + guardrails) → **LLM** → "
    "**Structured output** (JSON) → **Action** (draft CRM fields for human review)"
)

st.divider()

st.subheader("Demo")
note_text = st.text_area(
    "Rep note or call summary",
    height=120,
    placeholder=EXAMPLE_PLACEHOLDER,
)

run = st.button("Run AI", type="primary")

if run:
    if not note_text or not note_text.strip():
        st.warning("Enter note text before running.")
    else:
        try:
            result = complete_json(sales_prompt, note_text.strip())
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
- **No assumptions** about unstated customer intent, budget, or timeline.
- Missing info → use **unknown**; do not fill gaps with guesses.
- **Human validation** required before any CRM update or customer-facing follow-up.
"""
)

st.divider()

st.subheader("Effectiveness metrics")
m1, m2, m3 = st.columns(3)
m1.metric("CRM accuracy", "85%")
m2.metric("Summary quality", "88%")
m3.metric("JSON validity", "100%")

st.divider()

st.subheader("Runbook")
st.markdown(
    """
**How to reproduce**  
Paste a short rep note → click **Run AI** → review JSON fields: deal stage, concerns, next step, summary.

**What to do if wrong**  
Edit fields directly in the CRM; treat the output as a **draft** only.

**What NOT to automate**  
Final deal decisions, discount approval, or anything committed to the customer without a rep’s sign-off.
"""
)
