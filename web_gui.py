"""
NiceGUI web GUI prototype — Evaluate page only (Improvement Plan item 2.8).

Run:  python web_gui.py     then open http://localhost:8080

Purpose: prove out the framework for migrating off tkinter (plan 2.8/2.9).
Reuses JobApplicationAssistant unchanged — this is view-layer only.
"""
from __future__ import annotations

import json
from pathlib import Path

from nicegui import run, ui

from job_application_assistant import JobApplicationAssistant

CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_MODELS = ["gpt-5.2", "gpt-5.1", "gpt-5-mini", "gpt-4o"]

_assistant: JobApplicationAssistant | None = None


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_assistant() -> JobApplicationAssistant:
    global _assistant
    if _assistant is None:
        _assistant = JobApplicationAssistant()
    return _assistant


@ui.page("/")
def index():
    cfg = load_config()
    models = cfg.get("openai_models") or DEFAULT_MODELS
    saved_model = cfg.get("model") if cfg.get("model") in models else models[0]

    ui.dark_mode(cfg.get("theme", "dark") == "dark")

    with ui.header().classes("items-center"):
        ui.label("Job Application Assistant").classes("text-lg font-semibold")
        ui.badge("web prototype — Evaluate").props("color=orange")

    with ui.row().classes("w-full max-w-7xl mx-auto p-4 gap-4 flex-nowrap items-start"):
        # ── Left: job description input ──────────────────────────────────
        with ui.column().classes("flex-1 min-w-0"):
            ui.label("Job description").classes("text-sm text-gray-400")
            jd = (ui.textarea(placeholder="Paste the full job posting here…")
                  .props("outlined")
                  .classes("w-full")
                  .style("min-height: 340px"))
            word_count = ui.label("0 words").classes("text-xs text-gray-500")
            jd.on_value_change(
                lambda e: word_count.set_text(f"{len((e.value or '').split())} words"))

            with ui.row().classes("items-center gap-3"):
                model = (ui.select(models, value=saved_model, label="Model")
                         .props("outlined dense")
                         .classes("w-48"))
                go = ui.button("Evaluate fit", icon="query_stats")
            status = ui.label("").classes("text-xs text-gray-500")

        # ── Right: streaming evaluation output ───────────────────────────
        with ui.column().classes("flex-1 min-w-0"):
            ui.label("Evaluation").classes("text-sm text-gray-400")
            with ui.card().classes("w-full").style("min-height: 420px"):
                out = ui.markdown("").classes("w-full text-sm")

    buffer: list[str] = []

    async def evaluate():
        jd_text = (jd.value or "").strip()
        if len(jd_text) < 80:
            ui.notify("Paste a full job description first (this looks too short).",
                      type="warning")
            return
        go.disable()
        buffer.clear()
        out.set_content("")
        status.set_text("Initializing assistant…" if _assistant is None else "Evaluating…")

        # stream_callback appends from a worker thread; this timer renders
        # the accumulating markdown in the UI loop
        timer = ui.timer(0.15, lambda: out.set_content("".join(buffer)))
        try:
            result = await run.io_bound(
                lambda: get_assistant().evaluate_job_fit(
                    jd_text, model=model.value, stream_callback=buffer.append))
            status.set_text(
                f"Done — {result.get('tokens_used', 0):,} tokens ({model.value})")
        except Exception as e:
            status.set_text("Failed")
            ui.notify(f"Evaluation failed: {e}", type="negative", multi_line=True)
        finally:
            timer.cancel()
            out.set_content("".join(buffer))
            go.enable()

    go.on_click(evaluate)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Job Application Assistant (web prototype)",
           port=8080, reload=False, show=False)
