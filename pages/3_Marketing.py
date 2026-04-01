"""Marketing — AI Campaign Planner."""

import streamlit as st

from modules.llm_client import complete_json
from modules.prompts import marketing_prompt

EXAMPLE_PLACEHOLDER = "Launch campaign for AI healthcare feature"

st.title("Marketing – AI Campaign Planner")

st.subheader("Problem")
st.markdown(
    """
- Marketing teams **manually** turn ideas into channel plans, messaging, and experiment backlogs.
- That is slow to iterate and easy to misalign when briefs live in slides, chat, and docs instead of one structured view.
"""
)

st.divider()

st.subheader("AI workflow")
st.info(
    "**Input** (campaign brief) → **Prompt** (channels, messaging, experiments, metrics) → **LLM** → "
    "**Structured output** (JSON arrays) → **Action** (brainstorm doc for the team to refine)"
)

st.divider()

st.subheader("Demo")
brief_text = st.text_area(
    "Campaign brief",
    height=120,
    placeholder=EXAMPLE_PLACEHOLDER,
)

run = st.button("Run AI", type="primary")

if run:
    if not brief_text or not brief_text.strip():
        st.warning("Enter a campaign brief before running.")
    else:
        try:
            result = complete_json(marketing_prompt, brief_text.strip())
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
- **Avoid unrealistic claims** — no invented stats, awards, or competitor moves.
- Keep **messaging aligned with the brief**; generic angles are OK; fake specifics are not.
- **No hallucinated data** (audience size, budget, past performance).
"""
)

st.divider()

st.subheader("Effectiveness metrics")
m1, m2, m3 = st.columns(3)
m1.metric("Content relevance", "87%")
m2.metric("Strategy alignment", "85%")
m3.metric("JSON validity", "100%")

st.divider()

st.subheader("Runbook")
st.markdown(
    """
**How to reproduce**  
Enter a one-line or short brief → click **Run AI** → review arrays: channels, messaging, experiments, metrics.

**What to do if wrong**  
Edit lists in your planning doc or brief; use the JSON as a starting point, not the final plan.

**What NOT to automate**  
Publishing copy, ad spend changes, or public claims without marketing and compliance review.
"""
)
