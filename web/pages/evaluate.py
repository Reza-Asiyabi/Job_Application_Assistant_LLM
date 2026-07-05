"""Evaluate page — job fit evaluation with streaming output."""
from __future__ import annotations

from nicegui import ui

from ..helpers import jd_ok, output_pane, refine_row, stream_call
from ..layout import frame
from ..state import add_history, get_assistant, state
from ..theme import STATUS_COLORS

DEMO_OUTPUT = """\
1. FIT ASSESSMENT

**State: Strong fit.** This role is almost a direct match: PhD-level geospatial AI,
strong PyTorch computer vision, and hands-on SAR + multispectral experience.

## 2. MATCH ANALYSIS

- Core strength one with **specific CV evidence** cited inline
- Unique advantage the JD didn't ask for but will value
- A "preferred" requirement that is a disguised must-have

## 3. GAPS AND RISKS

- Missing skill named specifically, with employer-perspective concern
- No genuine red flags

## 5. SALARY ESTIMATE

Expected range **£65,000–80,000** — justified by company stage and specialisation.
"""


@ui.page("/")
def evaluate_page(demo: bool = False):
    with frame("Evaluate"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left: job description ─────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                ui.label("JOB DESCRIPTION").classes("text-xs font-medium jda-label")
                jd = (ui.textarea(placeholder="Paste the full job posting here…")
                      .bind_value(state, "jd")
                      .props("outlined")
                      .classes("w-full jda-input jda-fill jda-fill-lg"))
                with ui.row().classes("w-full items-center gap-3"):
                    word_count = ui.label("0 words").classes("text-xs") \
                        .style("color: var(--jda-muted)")
                    ui.space()
                    go = ui.button("Evaluate fit", icon="query_stats") \
                        .props("unelevated no-caps")
                jd.on_value_change(
                    lambda e: word_count.set_text(f"{len((e.value or '').split())} words"))

            # ── Right: streaming evaluation ───────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                badges = ui.row().classes("w-full gap-2 items-center")
                badges.set_visibility(False)
                out, status, latest = output_pane()
                buttons = [go]
                refine_row(out, status, latest, buttons)
                if demo:
                    out.set_content(DEMO_OUTPUT)
                    latest["text"] = DEMO_OUTPUT

        def show_badges(result: dict):
            badges.clear()
            score = result.get("score")
            verdict = (result.get("verdict") or "").strip()
            salary = (result.get("salary") or "").strip()
            if score is None and not verdict and not salary:
                badges.set_visibility(False)
                return
            with badges:
                if score is not None:
                    color = ("#3aaa6e" if score >= 75 else
                             "#e0a840" if score >= 50 else "#d44e4e")
                    ui.badge(f"Score {score}/100") \
                        .style(f"background: {color}; color: #0f1117") \
                        .props("outline=false").classes("text-sm px-3 py-1")
                if verdict:
                    v_color = {"yes": "#3aaa6e", "conditional": "#e0a840",
                               "no": "#d44e4e"}.get(verdict.lower(),
                                                    STATUS_COLORS[""])
                    ui.badge(verdict) \
                        .style(f"background: {v_color}; color: #0f1117") \
                        .classes("text-sm px-3 py-1")
                if salary:
                    ui.badge(f"~ {salary}") \
                        .style("background: var(--jda-surface2); "
                               "color: var(--jda-text)") \
                        .classes("text-sm px-3 py-1")
            badges.set_visibility(True)

        async def evaluate():
            if not jd_ok():
                return
            badges.set_visibility(False)

            def call(cb):
                return get_assistant().evaluate_job_fit(
                    state.jd, model=state.model, stream_callback=cb)

            result = await stream_call(fn=call, out=out, status=status,
                                       latest=latest, buttons=buttons,
                                       working="Evaluating…")
            if result:
                latest["type"] = "Evaluation"
                show_badges(result)
                add_history("Evaluation", result.get("evaluation", ""),
                            result.get("tokens_used", 0), state.company, state.role)

        go.on_click(evaluate)
