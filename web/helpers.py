"""Shared page building blocks: streaming runner, output pane, JD validation."""
from __future__ import annotations

from nicegui import run, ui

from .state import state


def jd_ok() -> bool:
    if len((state.jd or "").strip()) < 80:
        ui.notify("Paste a full job description first (this looks too short).",
                  type="warning")
        return False
    return True


def output_pane():
    """Standard right-hand output: label row with status + copy, markdown card.

    Returns (markdown_element, status_label, latest) where latest["text"]
    always holds the full current output for the copy button.
    """
    latest = {"text": ""}
    with ui.row().classes("w-full items-center"):
        ui.label("OUTPUT").classes("text-xs font-medium jda-label")
        ui.space()
        status = ui.label("").classes("text-xs").style("color: var(--jda-dim)")
        ui.button(icon="content_copy",
                  on_click=lambda: (ui.clipboard.write(latest["text"]),
                                    ui.notify("Copied", type="positive"))) \
            .props("flat round dense size=sm").tooltip("Copy output")
    with ui.element("div").classes("w-full jda-card jda-output"):
        out = ui.markdown("").classes("w-full")
    return out, status, latest


async def stream_call(fn, out, status, latest, buttons, working="Working…"):
    """Run fn(stream_callback) in a worker thread, streaming markdown into out.

    fn receives a stream_callback(str) and returns the assistant's result dict.
    Returns the result dict, or None on failure.
    """
    for b in buttons:
        b.disable()
    buffer: list[str] = []
    out.set_content("")
    status.set_text(working)
    timer = ui.timer(0.15, lambda: out.set_content("".join(buffer)))
    try:
        result = await run.io_bound(lambda: fn(buffer.append))
        status.set_text(f"Done — {result.get('tokens_used', 0):,} tokens ({state.model})")
        return result
    except Exception as e:
        status.set_text("Failed")
        ui.notify(f"Request failed: {e}", type="negative", multi_line=True)
        return None
    finally:
        timer.cancel()
        text = "".join(buffer)
        out.set_content(text)
        latest["text"] = text
        for b in buttons:
            b.enable()
