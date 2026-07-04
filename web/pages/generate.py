"""Generate page — CV summary, cover letter (3 tones), LinkedIn message."""
from __future__ import annotations

from nicegui import run, ui

from ..helpers import jd_ok, output_pane, stream_call
from ..layout import frame
from ..state import add_history, get_assistant, state

TONES = ["hybrid", "research", "engineering"]


@ui.page("/generate")
def generate_page():
    with frame("Generate"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left: JD + details + actions ──────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                ui.label("JOB DESCRIPTION").classes("text-xs font-medium jda-label")
                (ui.textarea(placeholder="Paste the full job posting here…")
                    .bind_value(state, "jd")
                    .props("outlined")
                    .classes("w-full jda-input jda-fill jda-fill-md"))

                with ui.row().classes("w-full gap-2 items-center"):
                    company = ui.input(label="Company").bind_value(state, "company") \
                        .props("outlined dense").classes("flex-1")
                    role = ui.input(label="Role title").bind_value(state, "role") \
                        .props("outlined dense").classes("flex-1")
                    extract_btn = ui.button(icon="auto_fix_high") \
                        .props("flat round dense").tooltip("Auto-extract from JD")
                ui.input(label="Recruiter name (LinkedIn message)") \
                    .bind_value(state, "recruiter") \
                    .props("outlined dense").classes("w-full")

                eval_chip = ui.label().classes("text-xs") \
                    .style("color: var(--jda-muted)")

                ui.separator().classes("my-1")
                with ui.row().classes("w-full gap-2 items-center"):
                    summary_btn = ui.button("CV Summary", icon="badge") \
                        .props("unelevated no-caps")
                    letter_btn = ui.button("Cover Letter", icon="drafts") \
                        .props("unelevated no-caps")
                    tone = ui.select(TONES, value="hybrid", label="Tone") \
                        .props("outlined dense options-dense").classes("w-36")
                with ui.row().classes("w-full gap-2 items-center"):
                    linkedin_btn = ui.button("LinkedIn Message", icon="send") \
                        .props("unelevated no-caps")

            # ── Right: output ─────────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                out, status, latest = output_pane()

        buttons = [summary_btn, letter_btn, linkedin_btn, extract_btn]

        def refresh_eval_chip():
            has_eval = getattr(get_assistant_or_none(), "_last_evaluation", None)
            eval_chip.set_text(
                "✓ Using the last fit evaluation as strategic context" if has_eval
                else "No evaluation yet — run Evaluate first for better targeting")

        def get_assistant_or_none():
            from ..state import _assistant
            return _assistant

        refresh_eval_chip()

        async def extract_details():
            if not jd_ok():
                return
            extract_btn.disable()
            status.set_text("Extracting company / role…")
            try:
                r = await run.io_bound(
                    lambda: get_assistant().extract_job_details(state.jd, model=state.model))
                if r.get("company"):
                    state.company = r["company"]
                if r.get("role"):
                    state.role = r["role"]
                status.set_text(f"Extracted: {r.get('company') or '?'} — {r.get('role') or '?'}")
            except Exception as e:
                ui.notify(f"Extraction failed: {e}", type="negative")
                status.set_text("")
            finally:
                extract_btn.enable()

        async def gen_summary():
            if not jd_ok():
                return

            def call(cb):
                a = get_assistant()
                return a.generate_cv_summary(
                    state.jd, fit_evaluation=a._last_evaluation,
                    model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, buttons,
                                  working="Writing CV summary…")
            if r:
                add_history("CV Summary", r.get("summary", ""),
                            r.get("tokens_used", 0), state.company, state.role)
            refresh_eval_chip()

        async def gen_letter():
            if not jd_ok():
                return
            tone_val = tone.value or "hybrid"

            def call(cb):
                a = get_assistant()
                return a.generate_cover_letter(
                    state.jd, fit_evaluation=a._last_evaluation,
                    company_name=state.company or None, role_title=state.role or None,
                    tone=tone_val, model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, buttons,
                                  working=f"Writing cover letter ({tone_val})…")
            if r:
                add_history(f"Cover Letter ({tone_val.title()})",
                            r.get("cover_letter", ""),
                            r.get("tokens_used", 0), state.company, state.role)
            refresh_eval_chip()

        async def gen_linkedin():
            if not jd_ok():
                return

            def call(cb):
                a = get_assistant()
                return a.generate_linkedin_message(
                    state.jd, recruiter_name=state.recruiter or None,
                    fit_evaluation=a._last_evaluation,
                    model=state.model, stream_callback=cb)

            r = await stream_call(call, out, status, latest, buttons,
                                  working="Writing LinkedIn message…")
            if r:
                add_history("LinkedIn", r.get("linkedin_message", ""),
                            r.get("tokens_used", 0), state.company, state.role)
            refresh_eval_chip()

        extract_btn.on_click(extract_details)
        summary_btn.on_click(gen_summary)
        letter_btn.on_click(gen_letter)
        linkedin_btn.on_click(gen_linkedin)
