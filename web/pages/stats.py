"""Stats page — pipeline counts, conversion funnel, generated-materials totals."""
from __future__ import annotations

from nicegui import ui

from ..layout import frame
from ..state import (MODEL_COSTS, STAGE_ORDER, STATUSES, TERMINAL_STATUSES,
                     load_applications, load_history)
from ..theme import STATUS_COLORS


def _stat(value: str, label: str, color: str = "var(--jda-text)", subtitle: str = ""):
    with ui.element("div").classes("jda-stat"):
        ui.label(value).classes("text-xl font-bold").style(f"color: {color}")
        ui.label(label).classes("text-xs").style("color: var(--jda-muted)")
        if subtitle:
            ui.label(subtitle).classes("text-xs").style("color: var(--jda-muted)")


@ui.page("/stats")
def stats_page():
    with frame("Stats"):
        apps = load_applications()
        hist = load_history()

        # ── Current pipeline (by current status) ──────────────────────────
        with ui.element("div").classes("w-full jda-card").style("padding: 16px 20px"):
            ui.label("CURRENT PIPELINE  (by current status)") \
                .classes("text-xs font-medium jda-label")
            counts = {s: 0 for s in STATUSES}
            for a in apps:
                s = a.get("status", "Applied")
                if s in counts:
                    counts[s] += 1
            with ui.row().classes("w-full gap-2 mt-2 flex-wrap"):
                for s in STATUSES:
                    _stat(str(counts[s]), s, STATUS_COLORS.get(s, "var(--jda-text)"))

        # ── Conversion funnel (by peak stage) ─────────────────────────────
        with ui.element("div").classes("w-full jda-card mt-4").style("padding: 16px 20px"):
            ui.label("CONVERSION FUNNEL  (by peak stage reached)") \
                .classes("text-xs font-medium jda-label")
            ui.label("Peak stage tracks the furthest point each application reached — "
                     "so rejections after interview still count as interviewed.") \
                .classes("text-xs mt-1").style("color: var(--jda-muted)")

            peak_counts = {s: 0 for s in STAGE_ORDER}
            for a in apps:
                peak = a.get("peak_stage") or (
                    a.get("status") if a.get("status") not in TERMINAL_STATUSES
                    else "Applied")
                if peak in peak_counts:
                    peak_counts[peak] += 1

            with ui.row().classes("w-full gap-2 mt-3 flex-wrap"):
                for stage, _ in sorted(STAGE_ORDER.items(), key=lambda x: x[1]):
                    _stat(str(peak_counts[stage]), stage,
                          STATUS_COLORS.get(stage, "var(--jda-text)"))

            n_total = len(apps)
            n_responded = sum(peak_counts[s] for s in
                              ["Phone Screen", "Interview", "Final Round",
                               "Offer", "Accepted"])
            n_interviewed = sum(peak_counts[s] for s in
                                ["Interview", "Final Round", "Offer", "Accepted"])
            n_offers = peak_counts.get("Offer", 0) + peak_counts.get("Accepted", 0)

            def pct(n):
                return f"{n / n_total * 100:.0f}%" if n_total else "—"

            with ui.row().classes("w-full gap-2 mt-3 flex-wrap"):
                _stat(str(n_total), "Total Applied")
                _stat(pct(n_responded), "Response Rate", "#e0a840",
                      f"{n_responded} got to Phone Screen+")
                _stat(pct(n_interviewed), "Interview Rate", "#f0a070",
                      f"{n_interviewed} reached Interview+")
                _stat(pct(n_offers), "Offer Rate", "#3aaa6e",
                      f"{n_offers} received an offer")

        # ── Generated materials ───────────────────────────────────────────
        with ui.element("div").classes("w-full jda-card mt-4").style("padding: 16px 20px"):
            ui.label("GENERATED MATERIALS").classes("text-xs font-medium jda-label")
            type_counts: dict[str, int] = {}
            total_tokens = 0
            total_cost = 0.0
            for h in hist:
                t = h.get("type", "Unknown")
                type_counts[t] = type_counts.get(t, 0) + 1
                toks = h.get("tokens", 0) or 0
                total_tokens += toks
                rate = MODEL_COSTS.get(h.get("model", "gpt-4o"), 0.010)
                total_cost += (toks / 1000) * rate

            with ui.row().classes("w-full gap-2 mt-2 flex-wrap"):
                for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
                    _stat(str(c), t, "#f0a070")
            with ui.row().classes("w-full gap-2 mt-3 flex-wrap"):
                _stat(f"{total_tokens:,}", "Total tokens")
                _stat(f"${total_cost:.2f}", "Estimated cost", "#e0a840")
