"""AI Internal Productivity Suite — main entry (home page)."""

from __future__ import annotations

import streamlit as st

from modules.evaluator import MODULES, evaluate_module
from modules.llm_client import is_llm_configured

st.set_page_config(
    page_title="AI Internal Productivity Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("AI Internal Productivity Suite")
st.markdown(
    "*AI workflows to improve internal team efficiency, productivity, and decision-making*"
)

st.divider()

st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("**Operations**")
    st.caption("Faster ticket triage")
    st.caption("Reduced manual routing")
with c2:
    st.markdown("**Sales**")
    st.caption("Faster CRM updates")
    st.caption("Better deal tracking")
with c3:
    st.markdown("**Marketing**")
    st.caption("Structured campaign planning")
    st.caption("Faster content generation")
with c4:
    st.markdown("**Finance**")
    st.caption("Faster risk analysis")
    st.caption("Better decision support")

st.divider()

st.subheader("Key capabilities")
st.success(
    "**Prompt-based workflows** · **Structured JSON outputs** · "
    "**Evaluation with golden datasets** · **Guardrails for safe usage**"
)

st.divider()

st.subheader("How it works")
st.info(
    "**Input** → **Prompt** (role + schema + guardrails) → **LLM** → "
    "**Structured output** (JSON) → **Action** (human review, routing, or planning)"
)

st.divider()

st.subheader("Evaluation (golden datasets)")
st.markdown(
    "Run the offline evaluator against CSV goldens: compares model output to expected fields "
    "and reports accuracy and JSON validity per module."
)

if "eval_snapshot" not in st.session_state:
    st.session_state.eval_snapshot = None

if not is_llm_configured():
    st.warning(
        "LLM not configured — evaluation skipped. Set **OPENAI_API_KEY** in a project **`.env`** file, "
        "your environment, or **`.streamlit/secrets.toml`**, then refresh this page."
    )
else:
    if st.button("Run evaluation", type="primary"):
        progress = st.progress(0)
        reports: list[dict] = []
        modules = list(MODULES.keys())
        n_mod = len(modules) or 1
        for i, name in enumerate(modules):
            reports.append(evaluate_module(name, temperature=0.0))
            progress.progress((i + 1) / n_mod)

        rows = []
        acc_sum = 0.0
        json_sum = 0.0
        for r in reports:
            acc_sum += r["accuracy"]
            json_sum += r["json_validity"]
            rows.append(
                {
                    "Module": r["module"].title(),
                    "Accuracy %": round(r["accuracy"] * 100, 1),
                    "JSON validity %": round(r["json_validity"] * 100, 1),
                    "Cases": r["total_cases"],
                }
            )
        n = len(reports) or 1
        st.session_state.eval_snapshot = {
            "rows": rows,
            "acc_pct": (acc_sum / n) * 100,
            "json_pct": (json_sum / n) * 100,
            "n_modules": len(reports),
        }

    snap = st.session_state.eval_snapshot
    if snap:
        st.metric(
            "Overall mean accuracy",
            f"{snap['acc_pct']:.1f}%",
            help="Average of per-module mean field accuracy.",
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Overall JSON validity", f"{snap['json_pct']:.1f}%")
        with col_b:
            st.metric("Modules evaluated", snap["n_modules"])

        st.dataframe(snap["rows"], hide_index=True, use_container_width=True)

st.divider()

st.markdown(
    "**Open a workflow** from the sidebar: **Operations**, **Sales**, **Marketing**, or **Finance** — "
    "each page includes a live demo, guardrails, demo metrics, and a runbook."
)

st.caption(
    "Demo project: AI-driven internal productivity workflows. "
    "The first item in the sidebar is this overview; workflow pages follow."
)
