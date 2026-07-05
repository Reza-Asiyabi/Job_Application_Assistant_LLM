"""Setup page — provider, Ollama connection, CV profiles, assistant status."""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

from nicegui import run, ui

from job_application_assistant import JobApplicationAssistant, get_profile_paths

from ..layout import frame
from ..state import (get_assistant, get_config, reset_assistant, state,
                     update_config)


@ui.page("/setup")
def setup_page():
    cfg = get_config()
    local = SimpleNamespace(
        provider=cfg.get("provider", "openai"),
        ollama_url=cfg.get("ollama_url", "http://localhost:11434"),
        cv_name="", cv_path="",
    )

    with frame("Setup"):
        with ui.row().classes("w-full gap-4 flex-nowrap items-start"):
            # ── Left column ───────────────────────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-4"):

                # Provider
                with ui.element("div").classes("w-full jda-card") \
                        .style("padding: 16px 20px"):
                    ui.label("PROVIDER").classes("text-xs font-medium jda-label")
                    provider_toggle = ui.toggle(
                        {"openai": "OpenAI API", "ollama": "Ollama (local)"}) \
                        .bind_value(local, "provider").props("no-caps")

                    # OpenAI status
                    openai_box = ui.column().classes("w-full gap-1 mt-2")
                    with openai_box:
                        key = os.getenv("OPENAI_API_KEY", "")
                        ui.label(("✓ API key found in .env" if key
                                  else "✗ OPENAI_API_KEY missing — add it to .env")) \
                            .classes("text-xs") \
                            .style(f"color: {'#3aaa6e' if key else '#d44e4e'}")
                        ui.label("Model is selected in the header — the list comes "
                                 "from config.json (openai_models).") \
                            .classes("text-xs").style("color: var(--jda-muted)")

                    # Ollama controls
                    ollama_box = ui.column().classes("w-full gap-2 mt-2")
                    with ollama_box:
                        with ui.row().classes("w-full gap-2 items-center"):
                            ui.input(label="Ollama URL") \
                                .bind_value(local, "ollama_url") \
                                .props("outlined dense").classes("flex-1")
                            check_btn = ui.button("Check", icon="wifi_tethering") \
                                .props("outline no-caps dense")
                        ollama_status = ui.label("").classes("text-xs") \
                            .style("color: var(--jda-muted)")
                        model_select = ui.select([], label="Installed models") \
                            .props("outlined dense options-dense").classes("w-full")
                        use_btn = ui.button("Use selected model", icon="check") \
                            .props("unelevated no-caps dense")

                    def apply_provider():
                        update_config(provider=local.provider,
                                      ollama_url=local.ollama_url)
                        reset_assistant()
                        openai_box.set_visibility(local.provider == "openai")
                        ollama_box.set_visibility(local.provider == "ollama")

                    provider_toggle.on_value_change(lambda e: apply_provider())
                    apply_provider()

                    async def check_ollama():
                        ok, err = await run.io_bound(
                            lambda: JobApplicationAssistant.check_ollama_connection(
                                local.ollama_url))
                        if ok:
                            models = await run.io_bound(
                                lambda: JobApplicationAssistant.list_ollama_models(
                                    local.ollama_url))
                            names = [m["name"] for m in models]
                            model_select.options = names
                            model_select.update()
                            ollama_status.set_text(
                                f"✓ Connected — {len(names)} model(s) installed")
                            update_config(ollama_url=local.ollama_url)
                        else:
                            ollama_status.set_text(err.replace("\n", " "))

                    def use_ollama_model():
                        if not model_select.value:
                            ui.notify("Pick a model first.", type="warning")
                            return
                        state.model = model_select.value
                        update_config(ollama_model=model_select.value,
                                      model=model_select.value)
                        reset_assistant()
                        ui.notify(f"Using {model_select.value}", type="positive")

                    check_btn.on_click(check_ollama)
                    use_btn.on_click(use_ollama_model)

                # CV profiles
                with ui.element("div").classes("w-full jda-card") \
                        .style("padding: 16px 20px"):
                    ui.label("CV PROFILES").classes("text-xs font-medium jda-label")
                    cv_list = ui.column().classes("w-full gap-1 mt-2")

                    def render_cvs():
                        cv_list.clear()
                        c = get_config()
                        with cv_list:
                            for p in c.get("cv_profiles", []):
                                active = p.get("name") == c.get("active_cv_name")
                                with ui.row().classes("w-full items-center gap-2"):
                                    ui.label("●" if active else "○") \
                                        .style(f"color: {'#3aaa6e' if active else 'var(--jda-muted)'}")
                                    ui.label(f"{p.get('name')} — {p.get('path')}") \
                                        .classes("text-sm flex-1")
                                    if not active:
                                        ui.button("Use", on_click=lambda n=p.get("name"): use_cv(n)) \
                                            .props("flat dense no-caps size=sm")
                                        ui.button(icon="close",
                                                  on_click=lambda n=p.get("name"): remove_cv(n)) \
                                            .props("flat round dense size=sm color=negative")

                    def use_cv(name: str):
                        update_config(active_cv_name=name)
                        reset_assistant()
                        render_cvs()
                        ui.notify(f"Active CV: {name} — assistant will reload",
                                  type="positive")

                    def remove_cv(name: str):
                        c = get_config()
                        profiles = [p for p in c.get("cv_profiles", [])
                                    if p.get("name") != name]
                        update_config(cv_profiles=profiles)
                        render_cvs()

                    def add_cv():
                        path = (local.cv_path or "").strip()
                        name = (local.cv_name or "").strip() or Path(path).stem
                        if not path:
                            ui.notify("Enter the path to a CV PDF.", type="warning")
                            return
                        if not Path(path).exists():
                            ui.notify(f"File not found: {path}", type="negative")
                            return
                        c = get_config()
                        profiles = c.get("cv_profiles", [])
                        profiles.append({"name": name, "path": path})
                        update_config(cv_profiles=profiles)
                        local.cv_name = ""
                        local.cv_path = ""
                        render_cvs()
                        ui.notify(f"Added CV profile: {name}", type="positive")

                    render_cvs()
                    with ui.row().classes("w-full gap-2 items-center mt-2"):
                        ui.input(label="Name").bind_value(local, "cv_name") \
                            .props("outlined dense").classes("w-32")
                        ui.input(label="Path to CV PDF (relative or absolute)") \
                            .bind_value(local, "cv_path") \
                            .props("outlined dense").classes("flex-1")
                        ui.button("Add", icon="add", on_click=add_cv) \
                            .props("outline no-caps dense")

            # ── Right column: assistant status ────────────────────────────
            with ui.column().classes("flex-1 min-w-0 gap-4"):
                with ui.element("div").classes("w-full jda-card") \
                        .style("padding: 16px 20px"):
                    ui.label("ASSISTANT").classes("text-xs font-medium jda-label")
                    status_area = ui.column().classes("w-full gap-1 mt-2")

                    def render_status(extra: str = ""):
                        status_area.clear()
                        c = get_config()
                        paths = get_profile_paths()
                        active = next((p for p in c.get("cv_profiles", [])
                                       if p.get("name") == c.get("active_cv_name")),
                                      None)
                        cv_path = (active or {}).get("path") or \
                            os.getenv("CV_PATH", "cv.pdf")
                        with status_area:
                            def line(label, value, ok=True):
                                with ui.row().classes("w-full gap-2"):
                                    ui.label(label).classes("text-xs w-28") \
                                        .style("color: var(--jda-muted)")
                                    ui.label(value).classes("text-xs") \
                                        .style(f"color: {'var(--jda-text)' if ok else '#d44e4e'}")
                            line("Provider", c.get("provider", "openai"))
                            line("CV file", f"{cv_path}"
                                 f"{'' if Path(cv_path).exists() else '  (missing!)'}",
                                 ok=Path(cv_path).exists())
                            prof = []
                            if paths["instructions"].exists():
                                prof.append(paths["instructions"].name)
                            if paths["personal"].exists():
                                prof.append(paths["personal"].name)
                            line("Profile", " + ".join(prof) or
                                 (paths["legacy"].name if paths["legacy"].exists()
                                  else "built-in"), ok=bool(prof))
                            if extra:
                                ui.label(extra).classes("text-xs mt-1") \
                                    .style("color: #3aaa6e")

                    render_status()

                    async def init_assistant():
                        init_btn.disable()
                        try:
                            reset_assistant()
                            a = await run.io_bound(get_assistant)
                            render_status(
                                f"✓ Initialized — CV: {len(a.cv_text):,} chars · "
                                f"profile: {len(a.system_prompt):,} chars · "
                                f"candidate: {a.user_name}")
                            ui.notify("Assistant initialized", type="positive")
                        except Exception as e:
                            render_status()
                            ui.notify(f"Initialization failed: {e}",
                                      type="negative", multi_line=True)
                        finally:
                            init_btn.enable()

                    with ui.row().classes("w-full mt-2"):
                        init_btn = ui.button("Initialize / reload assistant",
                                             icon="restart_alt",
                                             on_click=init_assistant) \
                            .props("unelevated no-caps")
