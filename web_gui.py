"""
NiceGUI web GUI prototype — Evaluate page only (Improvement Plan item 2.8).

Run:  python web_gui.py     then open http://localhost:8080
      http://localhost:8080/?demo=1 renders sample output for styling checks.

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

# Palette ported from gui.py's dark theme
BG        = "#0f1117"   # main canvas
SURFACE   = "#181b26"   # cards / panels
INPUT_BG  = "#0b0d16"   # text areas
HEADER_BG = "#13151f"
ACCENT    = "#e07640"   # coral — primary actions
TEXT      = "#eceef5"
TEXT_DIM  = "#868fa8"
TEXT_MUTED = "#4e5268"
BORDER    = "#2a2e42"

CSS = f"""
body {{ background: {BG}; color: {TEXT}; }}
.jda-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
.jda-input .q-field__control {{ background: {INPUT_BG}; }}
.jda-input textarea {{
    height: calc(100vh - 275px) !important;
    resize: none;
    line-height: 1.5;
}}
.eval-output {{
    height: calc(100vh - 210px);
    overflow-y: auto;
    padding: 16px 20px;
}}
/* Tame markdown typography — headings barely larger than body text */
.eval-output h1, .eval-output h2, .eval-output h3, .eval-output h4 {{
    font-size: 1rem;
    font-weight: 700;
    color: {ACCENT};
    margin: 1.1em 0 0.35em;
    line-height: 1.3;
}}
.eval-output h1:first-child, .eval-output h2:first-child {{ margin-top: 0; }}
.eval-output p, .eval-output li {{
    font-size: 0.895rem;
    line-height: 1.6;
    margin: 0.35em 0;
}}
.eval-output ul, .eval-output ol {{ padding-left: 1.2em; margin: 0.3em 0; }}
.eval-output hr {{ border-color: {BORDER}; margin: 0.9em 0; }}
.eval-output strong {{ color: {TEXT}; }}
"""

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
def index(demo: bool = False):
    cfg = load_config()
    models = cfg.get("openai_models") or DEFAULT_MODELS
    saved_model = cfg.get("model") if cfg.get("model") in models else models[0]

    ui.dark_mode(True)
    ui.colors(primary=ACCENT, dark=SURFACE, dark_page=BG)
    ui.add_css(CSS)

    with ui.header().classes("items-center").style(
            f"background: {HEADER_BG}; border-bottom: 1px solid {BORDER}"):
        ui.label("Job Application Assistant").classes("text-lg font-semibold")
        ui.badge("web prototype — Evaluate").props("color=primary outline")

    with ui.row().classes("w-full max-w-screen-2xl mx-auto p-4 gap-4 flex-nowrap items-start"):
        # ── Left: job description input ──────────────────────────────────
        with ui.column().classes("flex-1 min-w-0 gap-1"):
            ui.label("JOB DESCRIPTION").classes("text-xs font-medium") \
                .style(f"color: {TEXT_MUTED}; letter-spacing: 0.08em")
            jd = (ui.textarea(placeholder="Paste the full job posting here…")
                  .props("outlined")
                  .classes("w-full jda-input"))
            with ui.row().classes("w-full items-center gap-3"):
                word_count = ui.label("0 words").classes("text-xs") \
                    .style(f"color: {TEXT_MUTED}")
                ui.space()
                model = (ui.select(models, value=saved_model, label="Model")
                         .props("outlined dense options-dense")
                         .classes("w-44"))
                go = ui.button("Evaluate fit", icon="query_stats") \
                    .props("unelevated no-caps")
            jd.on_value_change(
                lambda e: word_count.set_text(f"{len((e.value or '').split())} words"))

        # ── Right: streaming evaluation output ───────────────────────────
        with ui.column().classes("flex-1 min-w-0 gap-1"):
            with ui.row().classes("w-full items-center"):
                ui.label("EVALUATION").classes("text-xs font-medium") \
                    .style(f"color: {TEXT_MUTED}; letter-spacing: 0.08em")
                ui.space()
                status = ui.label("").classes("text-xs").style(f"color: {TEXT_DIM}")
            with ui.element("div").classes("w-full jda-card eval-output"):
                out = ui.markdown(DEMO_OUTPUT if demo else "").classes("w-full")

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
