"""Evaluate page — job fit evaluation with streaming output."""
from __future__ import annotations

from nicegui import ui

from ..helpers import jd_ok, output_pane, stream_call
from ..layout import frame
from ..state import add_history, get_assistant, state

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
                out, status, latest = output_pane()
                if demo:
                    out.set_content(DEMO_OUTPUT)
                    latest["text"] = DEMO_OUTPUT

        async def evaluate():
            if not jd_ok():
                return

            def call(cb):
                return get_assistant().evaluate_job_fit(
                    state.jd, model=state.model, stream_callback=cb)

            result = await stream_call(fn=call, out=out, status=status,
                                       latest=latest, buttons=[go],
                                       working="Evaluating…")
            if result:
                add_history("Evaluation", result.get("evaluation", ""),
                            result.get("tokens_used", 0), state.company, state.role)

        go.on_click(evaluate)
