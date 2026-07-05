"""Package page — evaluation + CV summary + cover letter in one run."""
from __future__ import annotations

from nicegui import run, ui

from ..helpers import jd_ok, output_pane, refine_row
from ..layout import frame
from ..state import add_history, get_assistant, state


@ui.page("/package")
def package_page():
    with frame("Package"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left: JD + details ────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-1"):
                ui.label("JOB DESCRIPTION").classes("text-xs font-medium jda-label")
                (ui.textarea(placeholder="Paste the full job posting here…")
                    .bind_value(state, "jd")
                    .props("outlined")
                    .classes("w-full jda-input jda-fill jda-fill-md"))
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Company").bind_value(state, "company") \
                        .props("outlined dense").classes("flex-1")
                    ui.input(label="Role title").bind_value(state, "role") \
                        .props("outlined dense").classes("flex-1")
                ui.label("Runs three steps in sequence: fit evaluation → tailored "
                         "CV summary → cover letter. Each step feeds the next.") \
                    .classes("text-xs").style("color: var(--jda-muted)")
                with ui.row().classes("w-full"):
                    ui.space()
                    go = ui.button("Generate package", icon="inventory_2") \
                        .props("unelevated no-caps")

            # ── Right: combined streaming output ──────────────────────────
            with ui.column().classes("min-w-0 gap-1").style("flex: 1.2"):
                out, status, latest = output_pane()
                buttons = [go]
                refine_row(out, status, latest, buttons)

        buffer: list[str] = []

        async def generate_package():
            if not jd_ok():
                return
            go.disable()
            buffer.clear()
            out.set_content("")
            total = 0
            timer = ui.timer(0.15, lambda: out.set_content("".join(buffer)))
            try:
                status.set_text("Step 1/3 — Fit evaluation…")
                buffer.append("## EVALUATION\n\n")
                r1 = await run.io_bound(
                    lambda: get_assistant().evaluate_job_fit(
                        state.jd, model=state.model, stream_callback=buffer.append))
                total += r1.get("tokens_used", 0)
                eval_text = r1.get("evaluation", "")

                status.set_text("Step 2/3 — CV summary…")
                buffer.append("\n\n---\n\n## CV SUMMARY\n\n")
                r2 = await run.io_bound(
                    lambda: get_assistant().generate_cv_summary(
                        state.jd, fit_evaluation=eval_text,
                        model=state.model, stream_callback=buffer.append))
                total += r2.get("tokens_used", 0)

                status.set_text("Step 3/3 — Cover letter…")
                buffer.append("\n\n---\n\n## COVER LETTER\n\n")
                r3 = await run.io_bound(
                    lambda: get_assistant().generate_cover_letter(
                        state.jd, fit_evaluation=eval_text,
                        company_name=state.company or None,
                        role_title=state.role or None,
                        model=state.model, stream_callback=buffer.append))
                total += r3.get("tokens_used", 0)

                status.set_text(f"Package complete — {total:,} tokens ({state.model})")
                latest["type"] = "Cover Letter"   # refine applies to the last step
                add_history("Package", "".join(buffer), total,
                            state.company, state.role)
            except Exception as e:
                status.set_text("Failed")
                ui.notify(f"Package failed: {e}", type="negative", multi_line=True)
            finally:
                timer.cancel()
                text = "".join(buffer)
                out.set_content(text)
                latest["text"] = text
                go.enable()

        go.on_click(generate_package)
