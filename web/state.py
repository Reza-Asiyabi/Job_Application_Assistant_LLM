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
CONFIG_FILE       = ROOT / "config.json"
HISTORY_FILE      = ROOT / "history.json"
APPLICATIONS_FILE = ROOT / "applications.json"
DEFAULT_MODELS = ["gpt-5.2", "gpt-5.1", "gpt-5-mini", "gpt-4o"]

# Tracker pipeline — same semantics as gui.py
STATUSES = [
    "Watching", "Applied", "Phone Screen", "Interview",
    "Final Round", "Offer", "Accepted", "Rejected", "Withdrawn",
]
STAGE_ORDER = {
    "Watching": 0, "Applied": 1, "Phone Screen": 2, "Interview": 3,
    "Final Round": 4, "Offer": 5, "Accepted": 6,
}
TERMINAL_STATUSES = {"Rejected", "Withdrawn"}

# USD per 1k tokens (rough blended estimates — for the Stats cost display)
MODEL_COSTS = {
    "gpt-4o": 0.005, "gpt-4-turbo": 0.016, "gpt-4": 0.040,
    "gpt-3.5-turbo": 0.001, "gpt-5.2": 0.020, "gpt-5.1": 0.006,
    "gpt-5-mini": 0.001,
}


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
    """Build (or reuse) the assistant using provider + active CV from config.json."""
    global _assistant
    if _assistant is None:
        cfg = _load_config()
        provider = cfg.get("provider", "openai")
        cv_path = None
        active = next((p for p in cfg.get("cv_profiles", [])
                       if p.get("name") == cfg.get("active_cv_name")), None)
        if active and active.get("path"):
            cv_path = active["path"]
        kwargs: dict = {"cv_path": cv_path, "provider": provider}
        if provider == "ollama":
            base = cfg.get("ollama_url", "http://localhost:11434").rstrip("/")
            kwargs["base_url"] = base + "/v1"
        _assistant = JobApplicationAssistant(**kwargs)
    return _assistant


def reset_assistant() -> None:
    """Drop the cached assistant so the next call reloads CV + profile + provider."""
    global _assistant
    _assistant = None


def update_config(**kwargs) -> None:
    """Merge keys into config.json without touching the tkinter GUI's other keys."""
    cfg = _load_config()
    cfg.update(kwargs)
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[web] config save error: {e}")


def get_config() -> dict:
    return _load_config()


def _load_json(path: Path) -> list:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_json(path: Path, data: list) -> None:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    except Exception as e:
        print(f"[web] save error ({path.name}): {e}")


def load_history() -> list[dict]:
    return _load_json(HISTORY_FILE)


def save_history(history: list[dict]) -> None:
    _save_json(HISTORY_FILE, history)


def load_applications() -> list[dict]:
    return _load_json(APPLICATIONS_FILE)


def save_applications(apps: list[dict]) -> None:
    _save_json(APPLICATIONS_FILE, apps)


def compute_peak_stage(new_status: str, existing_peak: str) -> str:
    """Advance peak_stage only on forward progression; terminal outcomes keep it."""
    if new_status not in TERMINAL_STATUSES:
        new_order  = STAGE_ORDER.get(new_status, 0)
        peak_order = STAGE_ORDER.get(existing_peak, -1)
        return new_status if new_order > peak_order else existing_peak
    return existing_peak or "Applied"


def add_history(entry_type: str, content: str, tokens: int = 0,
                company: str = "", role: str = "") -> None:
    """Append an entry to history.json using the same schema as gui.py."""
    history = load_history()
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
    save_history(history)
