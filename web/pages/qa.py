"""Q&A page — answer specific application / interview questions."""
from __future__ import annotations

from nicegui import ui

from ..helpers import jd_ok, output_pane, stream_call
from ..layout import frame
from ..state import add_history, get_assistant, state


@ui.page("/qa")
def qa_page():
    with frame("Q & A"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left: JD + question ───────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                ui.label("JOB DESCRIPTION").classes("text-xs font-medium jda-label")
                (ui.textarea(placeholder="Paste the full job posting here…")
                    .bind_value(state, "jd")
                    .props("outlined")
                    .classes("w-full jda-input jda-fill jda-fill-md"))

                ui.label("APPLICATION QUESTION").classes("text-xs font-medium jda-label mt-2")
                (ui.textarea(placeholder='e.g. "Why do you want to work at this company?"')
                    .bind_value(state, "question")
                    .props("outlined")
                    .classes("w-full jda-input jda-fill")
                    .style("min-height: 90px"))

                with ui.row().classes("w-full items-center"):
                    ui.space()
                    go = ui.button("Answer question", icon="quiz") \
                        .props("unelevated no-caps")

            # ── Right: answer ─────────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                out, status, latest = output_pane()

        async def answer():
            if not jd_ok():
                return
            question = (state.question or "").strip()
            if not question:
                ui.notify("Enter the question first.", type="warning")
                return

            def call(cb):
                a = get_assistant()
                return a.answer_application_question(
                    state.jd, question, fit_evaluation=a._last_evaluation,
                    model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, [go],
                                  working="Answering…")
            if r:
                display = (f"QUESTION\n{'─' * 60}\n{question}\n\n"
                           f"ANSWER\n{'─' * 60}\n\n{r.get('answer', '')}")
                add_history("Q&A", display, r.get("tokens_used", 0),
                            state.company, state.role)

        go.on_click(answer)
