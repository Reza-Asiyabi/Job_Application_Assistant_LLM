"""Interview page — interview prep and post-interview follow-up email."""
from __future__ import annotations

from types import SimpleNamespace

from nicegui import ui

from ..helpers import jd_ok, output_pane, refine_row, stream_call
from ..layout import frame
from ..state import add_history, get_assistant, state


@ui.page("/interview")
def interview_page():
    local = SimpleNamespace(interviewer="", notes="")

    with frame("Interview"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left: JD + follow-up details ──────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                ui.label("JOB DESCRIPTION").classes("text-xs font-medium jda-label")
                (ui.textarea(placeholder="Paste the full job posting here…")
                    .bind_value(state, "jd")
                    .props("outlined")
                    .classes("w-full jda-input jda-fill jda-fill-md"))
                with ui.row().classes("w-full"):
                    prep_btn = ui.button("Interview prep", icon="school") \
                        .props("unelevated no-caps")
                    ui.label("Technical + behavioral Q&A, questions to ask, "
                             "gap handling").classes("text-xs self-center") \
                        .style("color: var(--jda-muted)")

                ui.separator().classes("my-2")
                ui.label("POST-INTERVIEW FOLLOW-UP").classes("text-xs font-medium jda-label")
                ui.input(label="Interviewer name(s)").bind_value(local, "interviewer") \
                    .props("outlined dense").classes("w-full")
                ui.textarea(label="What was discussed (for a specific, genuine reference)") \
                    .bind_value(local, "notes") \
                    .props("outlined").classes("w-full jda-input") \
                    .style("min-height: 90px")
                with ui.row().classes("w-full"):
                    followup_btn = ui.button("Follow-up email", icon="mail") \
                        .props("outline no-caps")

            # ── Right: output ─────────────────────────────────────────────
            with ui.column().classes("min-w-0 gap-1").style("flex: 1.2"):
                out, status, latest = output_pane()
                buttons = [prep_btn, followup_btn]
                refine_row(out, status, latest, buttons)

        async def gen_prep():
            if not jd_ok():
                return

            def call(cb):
                a = get_assistant()
                return a.generate_interview_prep(
                    state.jd, fit_evaluation=a._last_evaluation,
                    model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, buttons,
                                  working="Preparing interview materials…")
            if r:
                latest["type"] = "Interview Prep"
                add_history("Interview Prep", r.get("interview_prep", ""),
                            r.get("tokens_used", 0), state.company, state.role)

        async def gen_followup():
            if not jd_ok():
                return

            def call(cb):
                return get_assistant().generate_followup_email(
                    state.jd,
                    interviewer_name=local.interviewer or None,
                    interview_notes=local.notes or None,
                    model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, buttons,
                                  working="Writing follow-up email…")
            if r:
                latest["type"] = "Follow-Up Email"
                add_history("Follow-Up Email", r.get("followup_email", ""),
                            r.get("tokens_used", 0), state.company, state.role)

        prep_btn.on_click(gen_prep)
        followup_btn.on_click(gen_followup)
