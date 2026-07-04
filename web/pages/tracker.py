"""Tracker page — application pipeline (applications.json, same schema as gui.py)."""
from __future__ import annotations

import csv
from datetime import datetime
from types import SimpleNamespace

from nicegui import ui

from ..layout import frame
from ..state import (ROOT, STATUSES, compute_peak_stage, load_applications,
                     save_applications)
from ..theme import STATUS_COLORS

COLUMNS = [
    {"name": "date_applied", "label": "Date",     "field": "date_applied", "sortable": True, "align": "left"},
    {"name": "company",      "label": "Company",  "field": "company",      "sortable": True, "align": "left"},
    {"name": "position",     "label": "Position", "field": "position",     "sortable": True, "align": "left"},
    {"name": "location",     "label": "Location", "field": "location",     "sortable": True, "align": "left"},
    {"name": "status",       "label": "Status",   "field": "status",       "sortable": True, "align": "left"},
    {"name": "salary_jd",    "label": "Salary (JD)", "field": "salary_jd", "sortable": True, "align": "left"},
]

FORM_FIELDS = ["company", "position", "location", "date_applied", "source",
               "status", "salary_jd", "salary_req", "date_interview",
               "date_decision", "notes"]


@ui.page("/tracker")
def tracker_page():
    with frame("Tracker"):
        apps = load_applications()
        selected = {"id": None}
        flt = {"status": None}
        form = SimpleNamespace(**{f: "" for f in FORM_FIELDS})

        def visible_rows() -> list[dict]:
            rows = [a for a in apps
                    if not flt["status"] or a.get("status") == flt["status"]]
            return [{**a, "_color": STATUS_COLORS.get(a.get("status", ""), "#4e5268")}
                    for a in rows]

        # ── Status filter chips ───────────────────────────────────────────
        @ui.refreshable
        def chips():
            counts: dict[str, int] = {}
            for a in apps:
                counts[a.get("status", "")] = counts.get(a.get("status", ""), 0) + 1
            with ui.row().classes("w-full gap-1 items-center"):
                def chip(label, value, count):
                    active = flt["status"] == value
                    b = ui.button(f"{label} · {count}",
                                  on_click=lambda v=value: set_filter(v)) \
                        .props("flat dense no-caps size=sm")
                    if active:
                        b.classes("jda-nav-active")
                    return b
                chip("All", None, len(apps))
                for s in STATUSES:
                    if counts.get(s):
                        chip(s, s, counts[s])

        def set_filter(value):
            flt["status"] = value
            refresh()

        # ── Layout ────────────────────────────────────────────────────────
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            with ui.column().classes("min-w-0 gap-2").style("flex: 2"):
                with ui.row().classes("w-full items-center"):
                    chips()
                    ui.space()
                    ui.button(icon="download", on_click=lambda: export_csv()) \
                        .props("flat round dense").tooltip("Export CSV")
                table = ui.table(columns=COLUMNS, rows=visible_rows(), row_key="id",
                                 pagination=12) \
                    .props("flat dense wrap-cells").classes("w-full jda-card")
                table.add_slot("body-cell-status", """
                    <q-td :props="props">
                        <q-badge :style="{background: props.row._color, color: '#0f1117'}"
                                 :label="props.row.status" />
                    </q-td>
                """)

            # ── Right: entry form ─────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-2"):
                form_title = ui.label("NEW ENTRY").classes("text-xs font-medium jda-label")
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Company").bind_value(form, "company") \
                        .props("outlined dense").classes("flex-1")
                    ui.input(label="Position").bind_value(form, "position") \
                        .props("outlined dense").classes("flex-1")
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Location").bind_value(form, "location") \
                        .props("outlined dense").classes("flex-1")
                    ui.input(label="Source").bind_value(form, "source") \
                        .props("outlined dense").classes("flex-1")
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Applied (YYYY-MM-DD)").bind_value(form, "date_applied") \
                        .props("outlined dense").classes("flex-1")
                    ui.select(STATUSES, label="Status").bind_value(form, "status") \
                        .props("outlined dense options-dense").classes("flex-1")
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Salary (JD)").bind_value(form, "salary_jd") \
                        .props("outlined dense").classes("flex-1")
                    ui.input(label="Salary (asked)").bind_value(form, "salary_req") \
                        .props("outlined dense").classes("flex-1")
                with ui.row().classes("w-full gap-2"):
                    ui.input(label="Interview date").bind_value(form, "date_interview") \
                        .props("outlined dense").classes("flex-1")
                    ui.input(label="Decision date").bind_value(form, "date_decision") \
                        .props("outlined dense").classes("flex-1")
                ui.textarea(label="Notes").bind_value(form, "notes") \
                    .props("outlined").classes("w-full jda-input") \
                    .style("min-height: 110px")
                with ui.row().classes("w-full gap-2"):
                    ui.button("New", icon="add", on_click=lambda: new_entry()) \
                        .props("outline no-caps")
                    ui.button("Save", icon="save", on_click=lambda: save_entry()) \
                        .props("unelevated no-caps")
                    ui.space()
                    ui.button("Delete", icon="delete", on_click=lambda: delete_entry()) \
                        .props("flat no-caps color=negative")

        # ── Handlers ──────────────────────────────────────────────────────
        def refresh():
            table.rows = visible_rows()
            table.update()
            chips.refresh()

        def on_row_click(e):
            row = e.args[1]
            entry = next((a for a in apps if a["id"] == row["id"]), None)
            if not entry:
                return
            selected["id"] = entry["id"]
            for f in FORM_FIELDS:
                setattr(form, f, entry.get(f, ""))
            form_title.set_text(f"EDITING — {entry.get('company') or entry.get('position')}")

        table.on("rowClick", on_row_click)

        def new_entry():
            selected["id"] = None
            for f in FORM_FIELDS:
                setattr(form, f, "")
            form.date_applied = datetime.now().strftime("%Y-%m-%d")
            form.status = "Applied"
            form_title.set_text("NEW ENTRY")

        def save_entry():
            if not (form.company or "").strip() and not (form.position or "").strip():
                ui.notify("Enter at least a Company or Position.", type="warning")
                return
            existing = next((a for a in apps if a["id"] == selected["id"]), None) \
                if selected["id"] else None
            entry = {
                "id": selected["id"] or datetime.now().strftime("%Y%m%d_%H%M%S%f"),
                **{f: (getattr(form, f) or "").strip() for f in FORM_FIELDS},
                "peak_stage": compute_peak_stage(
                    form.status, (existing or {}).get("peak_stage", "")),
            }
            if existing:
                apps[apps.index(existing)] = entry
            else:
                apps.insert(0, entry)
                selected["id"] = entry["id"]
            save_applications(apps)
            refresh()
            ui.notify(f"Saved: {entry['company'] or entry['position']}", type="positive")

        def delete_entry():
            if not selected["id"]:
                ui.notify("Select an entry to delete.", type="warning")
                return
            entry = next((a for a in apps if a["id"] == selected["id"]), None)
            if not entry:
                return
            with ui.dialog() as dialog, ui.card().classes("jda-card"):
                ui.label(f"Delete {entry.get('company') or entry.get('position')}?")
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=dialog.close).props("flat no-caps")

                    def _confirm():
                        apps.remove(entry)
                        save_applications(apps)
                        dialog.close()
                        new_entry()
                        refresh()
                        ui.notify("Deleted", type="positive")
                    ui.button("Delete", on_click=_confirm) \
                        .props("unelevated no-caps color=negative")
            dialog.open()

        def export_csv():
            path = ROOT / f"applications_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            fields = ["date_applied", "company", "position", "location", "source",
                      "status", "peak_stage", "salary_jd", "salary_req",
                      "date_interview", "date_decision", "notes"]
            try:
                with open(path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(apps)
                ui.notify(f"Exported {len(apps)} rows → {path.name}", type="positive")
            except Exception as e:
                ui.notify(f"Export failed: {e}", type="negative")

        new_entry()
