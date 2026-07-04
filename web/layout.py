"""Page frame: header (title, model selector, theme toggle) + sidebar nav."""
from __future__ import annotations

from contextlib import contextmanager

from nicegui import ui

from .state import state
from .theme import ACCENT, CSS

NAV = [
    ("Evaluate", "/",          "query_stats"),
    ("Generate", "/generate",  "auto_awesome"),
    ("Q & A",    "/qa",        "quiz"),
    ("Tracker",  "/tracker",   "table_rows"),
    ("History",  "/history",   "history"),
]
COMING_SOON = ["Package", "Interview", "Profile", "Stats", "Setup"]


@contextmanager
def frame(title: str):
    ui.colors(primary=ACCENT)
    ui.add_css(CSS)
    dark = ui.dark_mode(state.dark)

    with ui.header().classes("items-center gap-3"):
        ui.label("Job Application Assistant").classes("text-lg font-semibold")
        ui.badge("web beta").props("color=primary outline")
        ui.space()
        (ui.select(state.models, label="Model")
            .bind_value(state, "model")
            .props("outlined dense options-dense")
            .classes("w-44")
            .on_value_change(lambda e: state.save_prefs()))

        def toggle_theme():
            state.dark = not state.dark
            dark.value = state.dark
            state.save_prefs()

        ui.button(icon="brightness_6", on_click=toggle_theme) \
            .props("flat round dense").tooltip("Toggle dark / light")

    with ui.left_drawer(value=True).props("width=185 breakpoint=800"):
        with ui.column().classes("w-full gap-0"):
            for name, path, icon in NAV:
                btn = (ui.button(name, icon=icon, on_click=lambda p=path: ui.navigate.to(p))
                       .props("flat no-caps align=left")
                       .classes("w-full justify-start"))
                if name == title:
                    btn.classes("jda-nav-active")
            ui.separator().classes("my-2")
            ui.label("COMING SOON").classes("text-xs jda-label q-px-md")
            for name in COMING_SOON:
                ui.label(name).classes("text-sm q-px-md q-py-xs") \
                    .style("color: var(--jda-muted)")

    with ui.column().classes("w-full p-4"):
        yield
