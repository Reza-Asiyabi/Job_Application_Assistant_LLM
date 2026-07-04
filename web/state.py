"""Shared application state: assistant singleton, config, history.

Single-user local app — module-level state is fine and keeps pages in sync
(the JD pasted on Evaluate is the same JD used on Generate and Q&A).
Reads/writes the same config.json and history.json as the tkinter GUI.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from job_application_assistant import JobApplicationAssistant

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE  = ROOT / "config.json"
HISTORY_FILE = ROOT / "history.json"
DEFAULT_MODELS = ["gpt-5.2", "gpt-5.1", "gpt-5-mini", "gpt-4o"]


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


class AppState:
    def __init__(self):
        cfg = _load_config()
        self.models: list[str] = cfg.get("openai_models") or list(DEFAULT_MODELS)
        saved = cfg.get("model")
        self.model: str = saved if saved in self.models else self.models[0]
        self.dark: bool = cfg.get("theme", "dark") != "light"
        # Shared inputs (persist while the server runs)
        self.jd        = ""
        self.company   = ""
        self.role      = ""
        self.recruiter = ""
        self.question  = ""

    def save_prefs(self) -> None:
        """Persist model + theme without touching the tkinter GUI's other keys."""
        cfg = _load_config()
        cfg["model"] = self.model
        cfg["theme"] = "dark" if self.dark else "light"
        try:
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[web] config save error: {e}")


state = AppState()

_assistant: JobApplicationAssistant | None = None


def get_assistant() -> JobApplicationAssistant:
    global _assistant
    if _assistant is None:
        _assistant = JobApplicationAssistant()
    return _assistant


def add_history(entry_type: str, content: str, tokens: int = 0,
                company: str = "", role: str = "") -> None:
    """Append an entry to history.json using the same schema as gui.py."""
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        history = []
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type":      entry_type,
        "company":   company or "",
        "role":      role or "",
        "model":     state.model,
        "tokens":    tokens,
        "content":   content,
        "status":    "",
    }
    if entry_type == "Evaluation" and _assistant is not None:
        entry["evaluation_context"] = getattr(_assistant, "_last_evaluation", "")
    history.insert(0, entry)
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False),
                                encoding="utf-8")
    except Exception as e:
        print(f"[web] history save error: {e}")
