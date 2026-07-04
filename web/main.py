"""Web GUI entry point — registers pages and starts the NiceGUI server."""
from __future__ import annotations

from nicegui import ui

from .pages import evaluate, generate, qa  # noqa: F401  (import registers routes)


def run_app(port: int = 8080, show: bool = True) -> None:
    ui.run(title="Job Application Assistant",
           port=port, reload=False, show=show)
