"""Shared page building blocks: streaming runner, output pane, JD validation."""
from __future__ import annotations

from types import SimpleNamespace

from nicegui import run, ui

from .state import add_history, get_assistant, state


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


def refine_row(out, status, latest, buttons):
    """Follow-up refinement input under an output pane.

    Continues the assistant's last conversation ("shorter", "more technical",
    "mention project X") instead of regenerating from scratch. Pages set
    latest["type"] after each generation so the refined result is logged
    under the right history type.
    """
    ns = SimpleNamespace(instruction="")
    with ui.row().classes("w-full gap-2 items-center"):
        inp = (ui.input(placeholder='Refine: e.g. "shorter", "more technical", '
                                    '"mention project X"…')
               .bind_value(ns, "instruction")
               .props("outlined dense")
               .classes("flex-1 jda-input"))
        btn = ui.button("Refine", icon="tune").props("outline no-caps dense")
    buttons.append(btn)

    async def do_refine():
        instruction = (ns.instruction or "").strip()
        if not instruction:
            ui.notify("Describe what to change first.", type="warning")
            return
        if not (latest["text"] or "").strip():
            ui.notify("Generate something first, then refine it.", type="warning")
            return

        def call(cb):
            return get_assistant().refine_output(
                instruction=instruction, model=state.model, stream_callback=cb)

        r = await stream_call(call, out, status, latest, buttons,
                              working="Refining…")
        if r:
            label = latest.get("type") or "Output"
            add_history(f"{label} (refined)", r.get("refined", ""),
                        r.get("tokens_used", 0), state.company, state.role)
            ns.instruction = ""

    btn.on_click(do_refine)
    inp.on("keydown.enter", do_refine)


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
