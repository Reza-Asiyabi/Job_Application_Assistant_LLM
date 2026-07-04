"""History page — browse, annotate and manage generated materials (history.json)."""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from nicegui import run, ui

from ..layout import frame
from ..state import (add_history, compute_peak_stage, get_assistant,
                     load_applications, load_history, save_applications,
                     save_history, state)
from ..theme import STATUS_COLORS

HIST_STATUSES = ["Applied", "Interview", "Offer", "Rejected"]

COLUMNS = [
    {"name": "timestamp", "label": "When",    "field": "timestamp", "sortable": True, "align": "left"},
    {"name": "type",      "label": "Type",    "field": "type",      "sortable": True, "align": "left"},
    {"name": "company",   "label": "Company", "field": "company",   "sortable": True, "align": "left"},
    {"name": "status",    "label": "Status",  "field": "status",    "sortable": True, "align": "left"},
]


@ui.page("/history")
def history_page():
    with frame("History"):
        hist = load_history()
        selected = {"i": None}
        flt = {"status": "", "search": ""}
        note = SimpleNamespace(text="")

        def visible_rows() -> list[dict]:
            rows = []
            for i, e in enumerate(hist):
                if flt["status"] and e.get("status", "") != flt["status"]:
                    continue
                if flt["search"]:
                    haystack = " ".join([e.get("type", ""), e.get("company", ""),
                                         e.get("role", ""), e.get("content", ""),
                                         e.get("notes", "")]).lower()
                    if flt["search"].lower() not in haystack:
                        continue
                rows.append({
                    "idx":       i,
                    "timestamp": e.get("timestamp", ""),
                    "type":      e.get("type", ""),
                    "company":   e.get("company", ""),
                    "status":    e.get("status", ""),
                    "_color":    STATUS_COLORS.get(e.get("status", ""), "#4e5268"),
                })
            return rows

        # ── Layout ────────────────────────────────────────────────────────
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # Left: filter + list
            with ui.column().classes("min-w-0 gap-2").style("flex: 1"):
                with ui.row().classes("w-full gap-1 items-center"):
                    search = ui.input(placeholder="Search…") \
                        .props("outlined dense clearable").classes("flex-1 jda-input")
                    status_filter = ui.select([""] + HIST_STATUSES, value="",
                                              label="Status") \
                        .props("outlined dense options-dense clearable").classes("w-32")
                table = ui.table(columns=COLUMNS, rows=visible_rows(), row_key="idx",
                                 pagination=14) \
                    .props("flat dense wrap-cells").classes("w-full jda-card")
                table.add_slot("body-cell-status", """
                    <q-td :props="props">
                        <q-badge v-if="props.row.status"
                                 :style="{background: props.row._color, color: '#0f1117'}"
                                 :label="props.row.status" />
                    </q-td>
                """)

            # Right: detail
            with ui.column().classes("min-w-0 gap-2").style("flex: 1.2"):
                meta = ui.label("Select an entry").classes("text-xs") \
                    .style("color: var(--jda-dim)")
                with ui.element("div").classes("w-full jda-card jda-output") \
                        .style("height: calc(100vh - 420px)"):
                    content = ui.markdown("").classes("w-full")
                with ui.row().classes("w-full gap-1 items-center"):
                    ui.label("STATUS").classes("text-xs jda-label")
                    status_btns = []
                    for s in HIST_STATUSES:
                        status_btns.append(
                            ui.button(s, on_click=lambda s=s: set_status(s))
                            .props("outline dense no-caps size=sm"))
                    ui.button("Clear", on_click=lambda: set_status("")) \
                        .props("flat dense no-caps size=sm")
                    ui.space()
                    ui.button(icon="playlist_add", on_click=lambda: add_to_tracker()) \
                        .props("flat round dense size=sm") \
                        .tooltip("Add to application tracker")
                    ui.button(icon="psychology", on_click=lambda: analyze_rejection()) \
                        .props("flat round dense size=sm") \
                        .tooltip("Analyze rejection (for rejected applications)")
                    ui.button(icon="content_copy", on_click=lambda: copy_content()) \
                        .props("flat round dense size=sm").tooltip("Copy content")
                    ui.button(icon="delete", on_click=lambda: delete_entry()) \
                        .props("flat round dense size=sm color=negative") \
                        .tooltip("Delete entry")
                notes = ui.textarea(label="Notes (auto-saved)") \
                    .bind_value(note, "text") \
                    .props("outlined dense").classes("w-full jda-input") \
                    .style("min-height: 70px")

        # ── Handlers ──────────────────────────────────────────────────────
        def refresh():
            table.rows = visible_rows()
            table.update()

        def on_search(e):
            flt["search"] = e.value or ""
            refresh()

        def on_status_filter(e):
            flt["status"] = e.value or ""
            refresh()

        search.on_value_change(on_search)
        status_filter.on_value_change(on_status_filter)

        def show_entry(i: int):
            e = hist[i]
            selected["i"] = i
            m = f"{e.get('timestamp', '')}  ·  {e.get('type', '')}"
            if e.get("company"):
                m += f"  ·  {e['company']}"
            if e.get("role"):
                m += f" — {e['role']}"
            m += f"  ·  {e.get('tokens', 0):,} tokens  ·  {e.get('model', '')}"
            meta.set_text(m)
            content.set_content(e.get("content", ""))
            note.text = e.get("notes", "")

        table.on("rowClick", lambda e: show_entry(e.args[1]["idx"]))

        def set_status(s: str):
            if selected["i"] is None:
                ui.notify("Select an entry first.", type="warning")
                return
            hist[selected["i"]]["status"] = s
            save_history(hist)
            refresh()
            ui.notify(f"Status: {s or 'cleared'}", type="positive")

        def save_notes():
            if selected["i"] is None:
                return
            hist[selected["i"]]["notes"] = note.text or ""
            save_history(hist)

        notes.on("blur", lambda e: save_notes())

        async def copy_content():
            if selected["i"] is None:
                return
            ui.clipboard.write(hist[selected["i"]].get("content", ""))
            ui.notify("Copied", type="positive")

        def add_to_tracker():
            if selected["i"] is None:
                ui.notify("Select an entry first.", type="warning")
                return
            e = hist[selected["i"]]
            apps = load_applications()
            entry = {
                "id":             datetime.now().strftime("%Y%m%d_%H%M%S%f"),
                "date_applied":   datetime.now().strftime("%Y-%m-%d"),
                "date_interview": "",
                "date_decision":  "",
                "company":        e.get("company", ""),
                "position":       e.get("role", ""),
                "location":       "",
                "source":         "",
                "status":         "Applied",
                "peak_stage":     compute_peak_stage("Applied", ""),
                "salary_jd":      "",
                "salary_req":     "",
                "notes":          f"Materials via assistant — {e.get('type', '')} "
                                  f"on {e.get('timestamp', '')}",
            }
            apps.insert(0, entry)
            save_applications(apps)
            ui.notify(f"Added to tracker: {entry['company'] or 'entry'} — "
                      "review it on the Tracker page", type="positive")

        def analyze_rejection():
            if selected["i"] is None:
                ui.notify("Select an entry first.", type="warning")
                return
            e = hist[selected["i"]]
            msg = SimpleNamespace(text="")
            with ui.dialog() as dialog, ui.card().classes("jda-card w-[520px]"):
                ui.label(f"Analyze rejection — {e.get('company') or e.get('type', '')}") \
                    .classes("font-medium")
                ui.textarea(label="Rejection message (optional — improves the analysis)") \
                    .bind_value(msg, "text") \
                    .props("outlined").classes("w-full jda-input") \
                    .style("min-height: 110px")
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=dialog.close).props("flat no-caps")

                    async def _run():
                        dialog.close()
                        meta.set_text("Analyzing rejection…")
                        buffer: list[str] = []
                        timer = ui.timer(0.15, lambda: content.set_content("".join(buffer)))
                        try:
                            r = await run.io_bound(
                                lambda: get_assistant().analyze_rejection(
                                    company_name=e.get("company") or None,
                                    role_title=e.get("role") or None,
                                    rejection_message=(msg.text or "").strip() or None,
                                    application_materials=e.get("content") or None,
                                    model=state.model,
                                    stream_callback=buffer.append))
                            add_history("Rejection Analysis",
                                        r.get("rejection_analysis", ""),
                                        r.get("tokens_used", 0),
                                        e.get("company", ""), e.get("role", ""))
                            meta.set_text(f"Rejection analysis — "
                                          f"{r.get('tokens_used', 0):,} tokens "
                                          "(saved to history)")
                        except Exception as exc:
                            meta.set_text("Analysis failed")
                            ui.notify(f"Analysis failed: {exc}", type="negative",
                                      multi_line=True)
                        finally:
                            timer.cancel()
                            content.set_content("".join(buffer))
                    ui.button("Analyze", on_click=_run).props("unelevated no-caps")
            dialog.open()

        def delete_entry():
            if selected["i"] is None:
                ui.notify("Select an entry first.", type="warning")
                return
            e = hist[selected["i"]]
            with ui.dialog() as dialog, ui.card().classes("jda-card"):
                ui.label(f"Delete this {e.get('type', 'entry')} from "
                         f"{e.get('timestamp', '')}?")
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=dialog.close).props("flat no-caps")

                    def _confirm():
                        hist.pop(selected["i"])
                        selected["i"] = None
                        save_history(hist)
                        dialog.close()
                        meta.set_text("Select an entry")
                        content.set_content("")
                        note.text = ""
                        refresh()
                        ui.notify("Deleted", type="positive")
                    ui.button("Delete", on_click=_confirm) \
                        .props("unelevated no-caps color=negative")
            dialog.open()
