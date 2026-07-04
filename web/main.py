"""Web GUI entry point — registers pages and starts the NiceGUI server."""
from __future__ import annotations

from nicegui import ui

from .pages import (  # noqa: F401  (import registers routes)
    evaluate, generate, history, interview, package, qa, tracker)


def run_app(port: int = 8080, show: bool = True) -> None:
    ui.run(title="Job Application Assistant",
           port=port, reload=False, show=show)
