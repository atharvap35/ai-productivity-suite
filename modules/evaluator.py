"""Golden-dataset evaluation: CSV goldens, LLM run, key-field accuracy."""

from __future__ import annotations

import csv
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from modules.llm_client import complete_json
from modules.prompts import (
    finance_prompt,
    marketing_prompt,
    operations_prompt,
    sales_prompt,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MODULES: dict[str, dict[str, Any]] = {
    "operations": {
        "csv": DATA_DIR / "ops_test_cases.csv",
        "prompt": operations_prompt,
    },
    "sales": {
        "csv": DATA_DIR / "sales_test_cases.csv",
        "prompt": sales_prompt,
    },
    "marketing": {
        "csv": DATA_DIR / "marketing_test_cases.csv",
        "prompt": marketing_prompt,
    },
    "finance": {
        "csv": DATA_DIR / "finance_test_cases.csv",
        "prompt": finance_prompt,
    },
}


def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip().lower()


def _similarity(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _match_team(expected: str, actual: str) -> bool:
    e, a = _norm(expected), _norm(actual)
    if not e and not a:
        return True
    if not e or not a:
        return False
    if e == a:
        return True
    if e in a or a in e:
        return True
    return _similarity(e, a) >= 0.55


def _match_issue_type(expected: str, actual: str) -> bool:
    e, a = _norm(expected), _norm(actual)
    if e == "unknown" or a == "unknown":
        return e == a
    if e == a:
        return True
    return e in a or a in e


def _match_priority(expected: str, actual: str) -> bool:
    e, a = _norm(expected), _norm(actual)
    if e == a:
        return True
    if e == "unknown" or a == "unknown":
        return False
    return False


def _match_risk_level(expected: str, actual: str) -> bool:
    return _norm(expected) == _norm(actual)


def _match_deal_stage(expected: str, actual: str) -> bool:
    e, a = _norm(expected), _norm(actual)
    if e == a:
        return True
    return e in a or a in e


def _match_next_step(expected: str, actual: str) -> bool:
    if _norm(expected) == _norm(actual):
        return True
    return _similarity(expected, actual) >= 0.48


def _expected_channel_in_channels(expected: str, channels: Any) -> bool:
    if not isinstance(channels, list):
        return False
    exp = _norm(expected)
    if not exp:
        return False
    for c in channels:
        s = _norm(c)
        if not s:
            continue
        if exp == s or exp in s or s in exp:
            return True
    return False


def _score_operations(expected: dict[str, str], actual: dict[str, Any] | None) -> float:
    if not actual:
        return 0.0
    m1 = _match_issue_type(expected["issue_type"], actual.get("issue_type"))
    m2 = _match_priority(expected["priority"], actual.get("priority"))
    m3 = _match_team(expected["team"], actual.get("team"))
    return (float(m1) + float(m2) + float(m3)) / 3.0


def _score_sales(expected: dict[str, str], actual: dict[str, Any] | None) -> float:
    if not actual:
        return 0.0
    m1 = _match_deal_stage(expected["deal_stage"], actual.get("deal_stage"))
    m2 = _match_next_step(expected["next_step"], actual.get("next_step"))
    return (float(m1) + float(m2)) / 2.0


def _score_marketing(expected: dict[str, str], actual: dict[str, Any] | None) -> float:
    if not actual:
        return 0.0
    ok = _expected_channel_in_channels(expected["channel"], actual.get("channels"))
    return 1.0 if ok else 0.0


def _score_finance(expected: dict[str, str], actual: dict[str, Any] | None) -> float:
    if not actual:
        return 0.0
    ok = _match_risk_level(expected["risk_level"], actual.get("risk_level"))
    return 1.0 if ok else 0.0


def _row_expected(module: str, row: dict[str, str]) -> dict[str, str]:
    if module == "operations":
        return {
            "issue_type": (row.get("expected_issue_type") or "").strip(),
            "priority": (row.get("expected_priority") or "").strip(),
            "team": (row.get("expected_team") or "").strip(),
        }
    if module == "sales":
        return {
            "deal_stage": (row.get("expected_deal_stage") or "").strip(),
            "next_step": (row.get("expected_next_step") or "").strip(),
        }
    if module == "marketing":
        return {"channel": (row.get("expected_channel") or "").strip()}
    if module == "finance":
        return {"risk_level": (row.get("expected_risk_level") or "").strip()}
    raise ValueError(module)


def _case_score(module: str, expected: dict[str, str], actual: dict[str, Any] | None) -> float:
    if module == "operations":
        return _score_operations(expected, actual)
    if module == "sales":
        return _score_sales(expected, actual)
    if module == "marketing":
        return _score_marketing(expected, actual)
    if module == "finance":
        return _score_finance(expected, actual)
    return 0.0


def load_cases(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def evaluate_module(
    module: str,
    *,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Run each golden input through the LLM; compare only key fields per module.

    Returns keys: ``accuracy``, ``json_validity``, ``total_cases``, plus ``module`` and ``cases``.
    """
    module = module.lower().strip()
    if module not in MODULES:
        raise ValueError(f"Unknown module: {module}. Choose from {list(MODULES)}.")

    cfg = MODULES[module]
    rows = load_cases(cfg["csv"])
    prompt = cfg["prompt"]

    cases_out: list[dict[str, Any]] = []
    json_ok = 0
    case_scores: list[float] = []

    for row in rows:
        inp = (row.get("input") or "").strip()
        expected = _row_expected(module, row)

        try:
            if not inp:
                result = {"ok": False, "error": "empty input", "raw": None}
            else:
                result = complete_json(prompt, inp, temperature=temperature)
        except Exception as exc:
            result = {"ok": False, "error": str(exc), "raw": None}

        valid = bool(result.get("ok") and isinstance(result.get("data"), dict))
        if valid:
            json_ok += 1

        actual = result.get("data") if valid else None
        if isinstance(actual, dict):
            try:
                score = _case_score(module, expected, actual)
            except Exception:
                score = 0.0
        else:
            score = 0.0

        case_scores.append(score)

        cases_out.append(
            {
                "input": inp,
                "expected": expected,
                "actual": actual,
                "llm_ok": valid,
                "error": result.get("error") if not valid else None,
                "case_accuracy": round(score, 4),
            }
        )

    n = len(rows)
    accuracy = round(sum(case_scores) / len(case_scores), 4) if case_scores else 0.0
    json_validity = round(json_ok / n, 4) if n else 0.0

    return {
        "module": module,
        "accuracy": accuracy,
        "json_validity": json_validity,
        "total_cases": n,
        "cases": cases_out,
    }


def summarize_report(report: dict[str, Any]) -> str:
    lines = [
        f"Module: {report['module']}",
        f"Total cases: {report['total_cases']}",
        f"JSON validity: {report['json_validity']:.1%}",
        f"Accuracy (key fields): {report['accuracy']:.1%}",
        "",
    ]
    for i, c in enumerate(report["cases"], 1):
        lines.append(f"--- Case {i} ---")
        lines.append(f"accuracy: {c['case_accuracy']:.1%} | llm_ok: {c['llm_ok']}")
        if c.get("error"):
            lines.append(f"error: {c['error']}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    name = (sys.argv[1] if len(sys.argv) > 1 else "operations").lower()
    rep = evaluate_module(name)
    print(summarize_report(rep))
