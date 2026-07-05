"""Profile page — edit the AI instructions and personal profile files."""
from __future__ import annotations

from types import SimpleNamespace

from nicegui import ui

from job_application_assistant import get_profile_paths

from ..layout import frame
from ..state import reset_assistant


@ui.page("/profile")
def profile_page():
    paths = get_profile_paths()
    personal_path = paths["personal"]
    instr_path    = paths["instructions"]
    editors = SimpleNamespace(personal="", instructions="")

    def load_files():
        try:
            editors.personal = personal_path.read_text(encoding="utf-8") \
                if personal_path.exists() else ""
        except Exception as e:
            editors.personal = f"# Error reading {personal_path.name}\n# {e}"
        try:
            editors.instructions = instr_path.read_text(encoding="utf-8") \
                if instr_path.exists() else ""
        except Exception as e:
            editors.instructions = f"# Error reading {instr_path.name}\n# {e}"

    load_files()

    with frame("Profile"):
        ui.label("The personal profile is ground truth about you; the instructions "
                 "define how the AI writes. Both feed every generation. "
                 "Task-specific prompts live in prompts/*.md.") \
            .classes("text-xs").style("color: var(--jda-muted)")

        with ui.tabs().classes("w-full") as tabs:
            tab_personal = ui.tab(f"Personal Profile  ({personal_path.name})")
            tab_instr    = ui.tab(f"AI Instructions  ({instr_path.name})")
        with ui.tab_panels(tabs, value=tab_personal).classes("w-full") \
                .style("background: transparent"):
            with ui.tab_panel(tab_personal).classes("p-0"):
                (ui.textarea()
                    .bind_value(editors, "personal")
                    .props("outlined")
                    .classes("w-full jda-input jda-mono jda-editor"))
            with ui.tab_panel(tab_instr).classes("p-0"):
                (ui.textarea()
                    .bind_value(editors, "instructions")
                    .props("outlined")
                    .classes("w-full jda-input jda-mono jda-editor"))

        with ui.row().classes("w-full items-center gap-2"):
            def save():
                if not editors.personal.strip() and not editors.instructions.strip():
                    ui.notify("Both editors are empty — nothing saved.", type="warning")
                    return
                errors = []
                if editors.personal.strip():
                    try:
                        personal_path.write_text(editors.personal, encoding="utf-8")
                    except Exception as e:
                        errors.append(f"{personal_path.name}: {e}")
                if editors.instructions.strip():
                    try:
                        instr_path.write_text(editors.instructions, encoding="utf-8")
                    except Exception as e:
                        errors.append(f"{instr_path.name}: {e}")
                if errors:
                    ui.notify("Could not save: " + "; ".join(errors), type="negative")
                    return
                reset_assistant()   # next generation reloads the new profile
                ui.notify("Profile saved — the assistant will reload it on the "
                          "next generation.", type="positive")

            def reload():
                load_files()
                ui.notify("Reloaded from disk.", type="positive")

            ui.button("Save profile", icon="save", on_click=save) \
                .props("unelevated no-caps")
            ui.button("Reload from disk", icon="refresh", on_click=reload) \
                .props("outline no-caps")
            ui.space()
            ui.label("Tip: point PROFILE_PERSONAL_PATH in .env at a private file "
                     "to keep personal data out of git.") \
                .classes("text-xs").style("color: var(--jda-muted)")
