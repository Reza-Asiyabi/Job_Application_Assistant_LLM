#!/usr/bin/env python3
"""
Job Application Assistant — GUI v2
A dark, modern desktop interface with sidebar navigation.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import os
import json
from datetime import datetime

from job_application_assistant import JobApplicationAssistant

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":           "#1e1e2e",   # main background
    "surface":      "#2a2a3e",   # cards / sidebar
    "surface2":     "#252537",   # hover / secondary surface
    "surface3":     "#16162a",   # status bar / deep bg
    "input_bg":     "#13131f",   # text areas / entries
    "accent":       "#7c6af7",   # primary accent (purple)
    "accent_dim":   "#5a4fd6",   # accent hover / pressed
    "accent2":      "#4f8ef7",   # secondary accent (blue)
    "success":      "#4ade80",   # green
    "success_dim":  "#166534",   # green hover bg
    "warning":      "#fb923c",   # orange
    "danger":       "#f87171",   # red
    "danger_dim":   "#7f1d1d",   # red hover bg
    "text":         "#e2e2f0",   # primary text
    "text_dim":     "#9a9ab0",   # secondary text
    "text_muted":   "#5a5a78",   # labels / section headers
    "border":       "#35354f",   # card borders / dividers
}

FF  = "Segoe UI"          # main font family
FM  = "Consolas"          # monospace font
HISTORY_FILE = "history.json"

NAV_ITEMS = [
    ("⚙", "Setup"),
    ("◈", "Evaluate"),
    ("✎", "Generate"),
    ("?", "Q & A"),
    ("▣", "Package"),
    ("☰", "History"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Application class
# ─────────────────────────────────────────────────────────────────────────────
class JobAssistantV2:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Job Application Assistant")
        self.root.geometry("1400x860")
        self.root.minsize(1100, 700)
        self.root.configure(bg=C["bg"])

        # ── State ─────────────────────────────────────────────────────────
        self.assistant: JobApplicationAssistant | None = None
        self.cv_path      = tk.StringVar(value="reza_cv.pdf")
        self.model_var    = tk.StringVar(value="gpt-4o")
        self.company_name = tk.StringVar()
        self.role_title   = tk.StringVar()
        self._session_tokens = 0
        self._pkg_running    = False
        self.history: list[dict] = self._load_history()

        # ── Build UI ──────────────────────────────────────────────────────
        self._build_header()
        self._build_body()
        self._build_statusbar()

        # Navigate to first page
        self._nav_to("Setup")

        # Try silent auto-init
        self.root.after(300, self._auto_init)

    # ═════════════════════════════════════════════════════════════════════════
    # Layout builders
    # ═════════════════════════════════════════════════════════════════════════

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C["surface"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text="Job Application Assistant",
            font=(FF, 15, "bold"), bg=C["surface"], fg=C["text"],
        ).pack(side="left", padx=22, pady=14)

        # Status indicator (right side)
        self._init_dot = tk.Label(
            hdr, text="⬤  Not initialized",
            font=(FF, 9), bg=C["surface"], fg=C["danger"],
        )
        self._init_dot.pack(side="right", padx=22)

        # Thin accent rule under header
        tk.Frame(self.root, bg=C["accent"], height=2).pack(fill="x")

    def _build_body(self):
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.pages: dict[str, tk.Frame] = {
            "Setup":    self._page_setup(self.content),
            "Evaluate": self._page_evaluate(self.content),
            "Generate": self._page_generate(self.content),
            "Q & A":    self._page_qa(self.content),
            "Package":  self._page_package(self.content),
            "History":  self._page_history(self.content),
        }

    def _build_sidebar(self, parent: tk.Frame):
        sb = tk.Frame(parent, bg=C["surface"], width=176)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Right-edge separator
        tk.Frame(sb, bg=C["border"], width=1).pack(side="right", fill="y")

        tk.Label(
            sb, text="NAVIGATION",
            font=(FF, 7, "bold"), bg=C["surface"], fg=C["text_muted"],
        ).pack(anchor="w", padx=18, pady=(20, 6))

        self._nav_btns: dict[str, tk.Button] = {}
        for icon, name in NAV_ITEMS:
            btn = tk.Button(
                sb,
                text=f"  {icon}   {name}",
                font=(FF, 11),
                anchor="w",
                relief="flat", bd=0,
                cursor="hand2",
                bg=C["surface"], fg=C["text_dim"],
                activebackground=C["surface2"],
                activeforeground=C["text"],
                padx=8, pady=11,
                command=lambda n=name: self._nav_to(n),
            )
            btn.pack(fill="x", padx=4, pady=1)
            self._nav_btns[name] = btn

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["surface3"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_lbl = tk.Label(
            bar, text="Ready",
            font=(FF, 9), bg=C["surface3"], fg=C["text_dim"], anchor="w",
        )
        self._status_lbl.pack(side="left", padx=14)

        self._token_lbl = tk.Label(
            bar, text="Session tokens: 0  |  Est. cost: $0.000",
            font=(FF, 9), bg=C["surface3"], fg=C["text_dim"], anchor="e",
        )
        self._token_lbl.pack(side="right", padx=14)

    # ═════════════════════════════════════════════════════════════════════════
    # Navigation
    # ═════════════════════════════════════════════════════════════════════════

    def _nav_to(self, name: str):
        for p in self.pages.values():
            p.pack_forget()
        for n, b in self._nav_btns.items():
            b.configure(bg=C["surface"], fg=C["text_dim"])

        self.pages[name].pack(fill="both", expand=True)
        self._nav_btns[name].configure(bg=C["surface2"], fg=C["accent"])

    # ═════════════════════════════════════════════════════════════════════════
    # Widget factory helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _card(self, parent: tk.Widget, title: str | None = None,
              padx: int = 16, pady: int = 12) -> tuple[tk.Frame, tk.Frame]:
        """A bordered dark card. Returns (outer_border_frame, inner_content_frame)."""
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=C["surface"], padx=padx, pady=pady)
        inner.pack(fill="both", expand=True)
        if title:
            tk.Label(
                inner, text=title.upper(),
                font=(FF, 7, "bold"), bg=C["surface"], fg=C["text_muted"],
            ).pack(anchor="w", pady=(0, 8))
        return outer, inner

    def _btn(self, parent: tk.Widget, text: str, cmd,
             style: str = "primary", **kw) -> tk.Button:
        palettes = {
            "primary":   (C["accent"],      C["text"],      C["accent_dim"]),
            "secondary": (C["surface2"],    C["text_dim"],  C["border"]),
            "success":   (C["success_dim"], C["success"],   "#14532d"),
            "danger":    (C["danger_dim"],  C["danger"],    "#450a0a"),
            "ghost":     (C["bg"],          C["text_muted"],C["surface2"]),
        }
        bg, fg, abg = palettes.get(style, palettes["primary"])
        return tk.Button(
            parent, text=text, command=cmd,
            relief="flat", bd=0, cursor="hand2",
            font=(FF, 10, "bold"),
            bg=bg, fg=fg,
            activebackground=abg, activeforeground=fg,
            padx=14, pady=7,
            **kw,
        )

    def _textarea(self, parent: tk.Widget, height: int = 8,
                  mono: bool = False) -> tuple[tk.Text, tk.Scrollbar]:
        ff = FM if mono else FF
        t = tk.Text(
            parent,
            height=height,
            font=(ff, 10),
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"],
            selectbackground=C["accent_dim"],
            selectforeground=C["text"],
            relief="flat", bd=0,
            wrap="word",
            padx=10, pady=8,
            spacing1=2,
        )
        sb = tk.Scrollbar(parent, command=t.yview,
                          bg=C["surface2"], troughcolor=C["surface3"],
                          relief="flat")
        t.configure(yscrollcommand=sb.set)
        return t, sb

    def _entry(self, parent: tk.Widget, textvariable=None,
               width: int = 30) -> tk.Entry:
        return tk.Entry(
            parent,
            textvariable=textvariable,
            font=(FF, 10),
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", bd=0,
            width=width,
        )

    def _section_header(self, parent: tk.Widget, title: str,
                        subtitle: str | None = None) -> tk.Frame:
        f = tk.Frame(parent, bg=C["bg"])
        tk.Label(f, text=title, font=(FF, 19, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        if subtitle:
            tk.Label(f, text=subtitle, font=(FF, 10),
                     bg=C["bg"], fg=C["text_dim"]).pack(anchor="w", pady=(2, 0))
        tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=(10, 0))
        return f

    def _lbl(self, parent: tk.Widget, text: str, bg: str = C["bg"],
             size: int = 9, bold: bool = False, dim: bool = False) -> tk.Label:
        return tk.Label(
            parent, text=text,
            font=(FF, size, "bold" if bold else ""),
            bg=bg, fg=C["text_muted"] if dim else C["text"],
        )

    def _inset_area(self, parent: tk.Widget, height: int = 10,
                    mono: bool = False) -> tuple[tk.Text, tk.Scrollbar]:
        """A textarea inside a 1px border frame, ready to pack."""
        border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner  = tk.Frame(border, bg=C["input_bg"])
        inner.pack(fill="both", expand=True)
        t, sb = self._textarea(inner, height=height, mono=mono)
        t.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        # Expose the border frame as .container so caller can pack it
        t._container = border
        return t, sb

    # ═════════════════════════════════════════════════════════════════════════
    # Pages
    # ═════════════════════════════════════════════════════════════════════════

    # ── Setup ─────────────────────────────────────────────────────────────
    def _page_setup(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "Setup", "Configure your CV and API settings"
        ).pack(fill="x", pady=(0, 24))

        # ── CV card ───────────────────────────────────────────────────────
        cv_outer, cv_card = self._card(inner, "CV Configuration")
        cv_outer.pack(fill="x", pady=(0, 14))

        self._lbl(cv_card, "CV PDF File", bg=C["surface"], dim=True).pack(anchor="w", pady=(0, 4))
        cv_row = tk.Frame(cv_card, bg=C["surface"])
        cv_row.pack(fill="x")
        cv_entry = self._entry(cv_row, textvariable=self.cv_path, width=64)
        cv_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self._btn(cv_row, "Browse …", self._browse_cv, style="ghost").pack(side="left", padx=(8, 0))

        # ── API card ──────────────────────────────────────────────────────
        api_outer, api_card = self._card(inner, "API Configuration")
        api_outer.pack(fill="x", pady=(0, 14))

        self._lbl(api_card, "Model", bg=C["surface"], dim=True).pack(anchor="w", pady=(0, 6))
        model_row = tk.Frame(api_card, bg=C["surface"])
        model_row.pack(anchor="w", pady=(0, 12))
        self._model_btns: dict[str, tk.Button] = {}
        for m in ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]:
            b = tk.Button(
                model_row, text=m,
                relief="flat", bd=0, cursor="hand2",
                font=(FF, 9),
                bg=C["input_bg"], fg=C["text_dim"],
                activebackground=C["accent_dim"], activeforeground=C["text"],
                padx=12, pady=5,
                command=lambda mv=m: self._select_model(mv),
            )
            b.pack(side="left", padx=2)
            self._model_btns[m] = b
        self._select_model("gpt-4o")

        key_row = tk.Frame(api_card, bg=C["surface"])
        key_row.pack(fill="x")
        self._lbl(key_row, "API Key:", bg=C["surface"], dim=True).pack(side="left", padx=(0, 10))
        self._api_status = tk.Label(key_row, text="Checking …",
                                    font=(FF, 9), bg=C["surface"], fg=C["warning"])
        self._api_status.pack(side="left")

        # ── Buttons ───────────────────────────────────────────────────────
        btn_row = tk.Frame(inner, bg=C["bg"])
        btn_row.pack(pady=10)
        self._btn(btn_row, "Initialize Assistant",
                  self._initialize_assistant, style="primary").pack(side="left", padx=(0, 8))
        self._btn(btn_row, "Test Configuration",
                  self._test_configuration, style="secondary").pack(side="left")

        # ── Log ───────────────────────────────────────────────────────────
        log_outer, log_card = self._card(inner, "Initialization Log")
        log_outer.pack(fill="both", expand=True, pady=(6, 0))
        log_card.configure(bg=C["surface"])
        self._setup_log, log_sb = self._textarea(log_card, height=14, mono=True)
        self._setup_log.configure(bg=C["surface3"], state="disabled")
        self._setup_log.pack(side="left", fill="both", expand=True)
        log_sb.pack(side="left", fill="y")

        return page

    # ── Evaluate ──────────────────────────────────────────────────────────
    def _page_evaluate(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "Evaluate Fit",
            "Paste a job description and get a strategic analysis"
        ).pack(fill="x", pady=(0, 20))

        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left ─ input
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.eval_job_text, _ = self._inset_area(left, height=22)
        self.eval_job_text._container.pack(fill="both", expand=True)

        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(10, 0))
        self._btn(lb, "Evaluate Fit",      self._evaluate_job_fit, style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard",   lambda: self._paste_to(self.eval_job_text), style="ghost").pack(side="left", padx=(0, 8))
        self._btn(lb, "Clear",             lambda: self.eval_job_text.delete(1.0, "end"), style="ghost").pack(side="left")

        # Right ─ output
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._lbl(right, "EVALUATION RESULTS", dim=True).pack(anchor="w", pady=(0, 4))
        self.eval_results, _ = self._inset_area(right, height=22)
        self.eval_results.configure(state="disabled")
        self.eval_results._container.pack(fill="both", expand=True)

        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save",  lambda: self._save_text(self.eval_results),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",  lambda: self._copy_text(self.eval_results),  style="secondary").pack(side="left")

        return page

    # ── Generate ──────────────────────────────────────────────────────────
    def _page_generate(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "Generate Materials",
            "Create tailored CV summaries and cover letters"
        ).pack(fill="x", pady=(0, 20))

        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left ─ input
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.gen_job_text, _ = self._inset_area(left, height=16)
        self.gen_job_text._container.pack(fill="both", expand=True)

        # Optional details card
        opt_outer, opt_card = self._card(left, "Optional Details", padx=12, pady=10)
        opt_outer.pack(fill="x", pady=(10, 0))
        opt_card.configure(bg=C["surface"])
        for label, var in [("Company", self.company_name), ("Role Title", self.role_title)]:
            row = tk.Frame(opt_card, bg=C["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=(FF, 9), bg=C["surface"],
                     fg=C["text_dim"], width=10, anchor="w").pack(side="left")
            self._entry(row, textvariable=var, width=42).pack(side="left", fill="x", expand=True, ipady=5)

        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(10, 0))
        self._btn(lb, "CV Summary",      self._generate_cv_summary,   style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Cover Letter",    self._generate_cover_letter, style="secondary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard", lambda: self._paste_to(self.gen_job_text), style="ghost").pack(side="left")

        # Right ─ output
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._lbl(right, "GENERATED CONTENT", dim=True).pack(anchor="w", pady=(0, 4))
        self.gen_output, _ = self._inset_area(right, height=24)
        self.gen_output.configure(state="disabled")
        self.gen_output._container.pack(fill="both", expand=True)

        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save",  lambda: self._save_text(self.gen_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",  lambda: self._copy_text(self.gen_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Clear", lambda: self._clear_text(self.gen_output), style="ghost").pack(side="left")

        return page

    # ── Q & A ─────────────────────────────────────────────────────────────
    def _page_qa(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "Application Q & A",
            "Ask specific questions about the job or your application strategy"
        ).pack(fill="x", pady=(0, 20))

        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left ─ inputs
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.qa_job_text, _ = self._inset_area(left, height=13)
        self.qa_job_text._container.pack(fill="both", expand=True)

        self._lbl(left, "YOUR QUESTION", dim=True).pack(anchor="w", pady=(14, 4))
        self.qa_question, _ = self._inset_area(left, height=6)
        self.qa_question._container.pack(fill="x")

        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(10, 0))
        self._btn(lb, "Answer Question",   self._answer_question,            style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard",   lambda: self._paste_to(self.qa_job_text), style="ghost").pack(side="left")

        # Right ─ output
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._lbl(right, "AI ANSWER", dim=True).pack(anchor="w", pady=(0, 4))
        self.qa_output, _ = self._inset_area(right, height=24)
        self.qa_output.configure(state="disabled")
        self.qa_output._container.pack(fill="both", expand=True)

        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save",  lambda: self._save_text(self.qa_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",  lambda: self._copy_text(self.qa_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Clear", lambda: self._clear_text(self.qa_output), style="ghost").pack(side="left")

        return page

    # ── Package ───────────────────────────────────────────────────────────
    def _page_package(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "Complete Package",
            "Generate evaluation + CV summary + cover letter in one go"
        ).pack(fill="x", pady=(0, 20))

        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left ─ input
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.pkg_job_text, _ = self._inset_area(left, height=14)
        self.pkg_job_text._container.pack(fill="both", expand=True)

        opt_outer, opt_card = self._card(left, "Details", padx=12, pady=10)
        opt_outer.pack(fill="x", pady=(10, 0))
        opt_card.configure(bg=C["surface"])
        for label, var in [("Company", self.company_name), ("Role Title", self.role_title)]:
            row = tk.Frame(opt_card, bg=C["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=(FF, 9), bg=C["surface"],
                     fg=C["text_dim"], width=10, anchor="w").pack(side="left")
            self._entry(row, textvariable=var, width=42).pack(side="left", fill="x", expand=True, ipady=5)

        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(12, 0))
        self._btn(lb, "Generate Complete Package", self._generate_package, style="success").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard", lambda: self._paste_to(self.pkg_job_text), style="ghost").pack(side="left")

        self._progress_lbl = tk.Label(left, text="", font=(FF, 9),
                                      bg=C["bg"], fg=C["accent"])
        self._progress_lbl.pack(anchor="w", pady=(8, 0))

        # Right ─ output
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._lbl(right, "GENERATED PACKAGE", dim=True).pack(anchor="w", pady=(0, 4))
        self.pkg_output, _ = self._inset_area(right, height=24)
        self.pkg_output.configure(state="disabled")
        self.pkg_output._container.pack(fill="both", expand=True)

        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save Package", lambda: self._save_text(self.pkg_output), style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy All",     lambda: self._copy_text(self.pkg_output), style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Clear",        lambda: self._clear_text(self.pkg_output), style="ghost").pack(side="left")

        return page

    # ── History ───────────────────────────────────────────────────────────
    def _page_history(self, parent: tk.Widget) -> tk.Frame:
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        self._section_header(
            inner, "History",
            "All generated results are automatically saved here"
        ).pack(fill="x", pady=(0, 20))

        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left ─ list panel
        left = tk.Frame(split, bg=C["bg"], width=310)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        self._lbl(left, "ENTRIES", dim=True).pack(anchor="w", pady=(0, 4))

        list_border = tk.Frame(left, bg=C["border"], padx=1, pady=1)
        list_border.pack(fill="both", expand=True)
        list_inner  = tk.Frame(list_border, bg=C["surface"])
        list_inner.pack(fill="both", expand=True)

        self._hist_list = tk.Listbox(
            list_inner,
            font=(FF, 9),
            bg=C["surface"], fg=C["text"],
            selectbackground=C["accent_dim"],
            selectforeground=C["text"],
            relief="flat", bd=0,
            activestyle="none",
        )
        hist_sb = tk.Scrollbar(list_inner, command=self._hist_list.yview,
                               bg=C["surface2"], troughcolor=C["surface3"],
                               relief="flat")
        self._hist_list.configure(yscrollcommand=hist_sb.set)
        self._hist_list.pack(side="left", fill="both", expand=True)
        hist_sb.pack(side="left", fill="y")
        self._hist_list.bind("<<ListboxSelect>>", self._on_hist_select)

        hb = tk.Frame(left, bg=C["bg"])
        hb.pack(fill="x", pady=(10, 0))
        self._btn(hb, "Delete Selected", self._delete_hist_entry, style="danger").pack(side="left", padx=(0, 8))
        self._btn(hb, "Clear All",       self._clear_history,     style="ghost").pack(side="left")

        # Right ─ content viewer
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._hist_meta = tk.Label(
            right, text="Select an entry to view its content",
            font=(FF, 9), bg=C["bg"], fg=C["text_dim"], anchor="w",
        )
        self._hist_meta.pack(anchor="w", pady=(0, 6))

        self.hist_content, _ = self._inset_area(right, height=24)
        self.hist_content.configure(state="disabled")
        self.hist_content._container.pack(fill="both", expand=True)

        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save Entry", lambda: self._save_text(self.hist_content), style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",       lambda: self._copy_text(self.hist_content), style="secondary").pack(side="left")

        self._refresh_hist_list()
        return page

    # ═════════════════════════════════════════════════════════════════════════
    # Setup actions
    # ═════════════════════════════════════════════════════════════════════════

    def _select_model(self, model: str):
        self.model_var.set(model)
        for m, b in self._model_btns.items():
            if m == model:
                b.configure(bg=C["accent"], fg=C["text"])
            else:
                b.configure(bg=C["input_bg"], fg=C["text_dim"])

    def _browse_cv(self):
        f = filedialog.askopenfilename(
            title="Select CV PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if f:
            self.cv_path.set(f)

    def _log(self, msg: str):
        def _do():
            self._setup_log.configure(state="normal")
            self._setup_log.insert("end", msg + "\n")
            self._setup_log.see("end")
            self._setup_log.configure(state="disabled")
        self.root.after(0, _do)

    def _auto_init(self):
        from dotenv import load_dotenv
        load_dotenv()
        if Path(self.cv_path.get()).exists() and os.getenv("OPENAI_API_KEY"):
            self._initialize_assistant(silent=True)

    def _initialize_assistant(self, silent: bool = False):
        cv = self.cv_path.get()
        if not Path(cv).exists():
            messagebox.showerror("CV Not Found", f"File not found:\n{cv}")
            return

        # Clear log
        self._setup_log.configure(state="normal")
        self._setup_log.delete(1.0, "end")
        self._setup_log.configure(state="disabled")
        self._log("Initializing …")
        self._set_status("Initializing assistant …")

        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            self._log("ERROR: OPENAI_API_KEY not found in .env file")
            self._api_status.configure(text="Not configured", fg=C["danger"])
            if not silent:
                messagebox.showerror(
                    "API Key Missing",
                    "Create a .env file in the project folder with:\n\nOPENAI_API_KEY=your-key-here"
                )
            return

        self._api_status.configure(text="Found", fg=C["success"])
        self._log("API key found.")

        def _do():
            try:
                self.assistant = JobApplicationAssistant(cv_path=cv)
                self._log(f"CV loaded:  {Path(cv).name}")
                self._log(f"Model:      {self.model_var.get()}")
                self._log("Ready.")
                self._set_status("Assistant ready")
                self.root.after(0, lambda: self._init_dot.configure(
                    text="⬤  Ready", fg=C["success"]))
                if not silent:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Ready", "Assistant initialized successfully!"))
            except Exception as e:
                self._log(f"ERROR: {e}")
                self._set_status("Initialization failed")
                if not silent:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=_do, daemon=True).start()

    def _test_configuration(self):
        if not self._check_init():
            return
        self._log("\nRunning configuration test …")
        self._set_status("Testing …")

        def _do():
            try:
                r    = self.assistant.evaluate_job_fit(
                    "ML Engineer, Python, PyTorch", model=self.model_var.get()
                )
                toks = r.get("tokens_used", 0)
                self._log(f"Test passed!  Tokens used: {toks}")
                self._set_status(f"Test passed — {toks} tokens")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Test Passed", f"Everything is working.\nTokens used: {toks}"))
            except Exception as e:
                self._log(f"Test FAILED: {e}")
                self.root.after(0, lambda: messagebox.showerror("Test Failed", str(e)))

        threading.Thread(target=_do, daemon=True).start()

    # ═════════════════════════════════════════════════════════════════════════
    # Feature actions
    # ═════════════════════════════════════════════════════════════════════════

    def _evaluate_job_fit(self):
        if not self._check_init():
            return
        jd = self.eval_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        self._write(self.eval_results, "Analyzing … (this may take 10–30 seconds)")
        self._set_status("Evaluating job fit …")

        def _do():
            try:
                r    = self.assistant.evaluate_job_fit(jd, model=self.model_var.get())
                text = r.get("evaluation", r.get("error", "No result returned."))
                toks = r.get("tokens_used", 0)
                self._write(self.eval_results, text)
                self._add_tokens(toks)
                self._set_status(f"Evaluation complete — {toks:,} tokens")
                self._add_history("Evaluation", text, toks,
                                  self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.eval_results, f"Error: {e}")
                self._set_status("Error during evaluation")

        threading.Thread(target=_do, daemon=True).start()

    def _generate_cv_summary(self):
        if not self._check_init():
            return
        jd = self.gen_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        self._write(self.gen_output, "Generating CV summary …")
        self._set_status("Generating CV summary …")

        def _do():
            try:
                r    = self.assistant.generate_cv_summary(jd, model=self.model_var.get())
                text = r.get("summary", r.get("error", "No result returned."))
                toks = r.get("tokens_used", 0)
                self._write(self.gen_output,
                            f"CV SUMMARY\n{'─' * 60}\n\n{text}")
                self._add_tokens(toks)
                self._set_status(f"CV summary generated — {toks:,} tokens")
                self._add_history("CV Summary", text, toks,
                                  self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.gen_output, f"Error: {e}")
                self._set_status("Error during generation")

        threading.Thread(target=_do, daemon=True).start()

    def _generate_cover_letter(self):
        if not self._check_init():
            return
        jd = self.gen_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        company = self.company_name.get().strip() or None
        role    = self.role_title.get().strip()    or None
        self._write(self.gen_output, "Generating cover letter …")
        self._set_status("Generating cover letter …")

        def _do():
            try:
                r    = self.assistant.generate_cover_letter(
                    jd, company_name=company, role_title=role,
                    model=self.model_var.get()
                )
                text = r.get("cover_letter", r.get("error", "No result returned."))
                toks = r.get("tokens_used", 0)
                self._write(self.gen_output,
                            f"COVER LETTER\n{'─' * 60}\n\n{text}")
                self._add_tokens(toks)
                self._set_status(f"Cover letter generated — {toks:,} tokens")
                self._add_history("Cover Letter", text, toks, company, role)
            except Exception as e:
                self._write(self.gen_output, f"Error: {e}")
                self._set_status("Error during generation")

        threading.Thread(target=_do, daemon=True).start()

    def _answer_question(self):
        if not self._check_init():
            return
        jd       = self.qa_job_text.get(1.0, "end").strip()
        question = self.qa_question.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        if not question:
            messagebox.showwarning("Input Required", "Please enter your question.")
            return
        self._write(self.qa_output, "Generating answer …")
        self._set_status("Answering question …")

        def _do():
            try:
                r    = self.assistant.answer_application_question(
                    jd, question, model=self.model_var.get()
                )
                text = r.get("answer", r.get("error", "No result returned."))
                toks = r.get("tokens_used", 0)
                display = (
                    f"QUESTION\n{'─' * 60}\n{question}\n\n"
                    f"ANSWER\n{'─' * 60}\n\n{text}"
                )
                self._write(self.qa_output, display)
                self._add_tokens(toks)
                self._set_status(f"Answer generated — {toks:,} tokens")
                self._add_history("Q&A", display, toks,
                                  self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.qa_output, f"Error: {e}")
                self._set_status("Error during Q&A")

        threading.Thread(target=_do, daemon=True).start()

    def _generate_package(self):
        if not self._check_init():
            return
        jd = self.pkg_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        company = self.company_name.get().strip() or None
        role    = self.role_title.get().strip()    or None

        self._write(self.pkg_output,
                    "Generating complete package …\nThis typically takes 30–60 seconds.")
        self._set_status("Generating package …")

        # Animated progress dots
        self._pkg_running = True

        def _animate():
            import time
            frames = ["   ", ".  ", ".. ", "..."]
            i = 0
            while self._pkg_running:
                dot = frames[i % 4]
                self.root.after(0, lambda d=dot: self._progress_lbl.configure(
                    text=f"Working{d}"))
                i += 1
                time.sleep(0.5)
            self.root.after(0, lambda: self._progress_lbl.configure(text=""))

        threading.Thread(target=_animate, daemon=True).start()

        def _do():
            try:
                r    = self.assistant.full_application_package(
                    jd, company_name=company, role_title=role,
                    model=self.model_var.get()
                )
                self._pkg_running = False
                toks = r.get("total_tokens_used", 0)

                meta_lines = []
                if company: meta_lines.append(f"Company:  {company}")
                if role:    meta_lines.append(f"Role:     {role}")
                meta_lines.append(f"Date:     {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                meta = "\n".join(meta_lines)

                output = (
                    f"COMPLETE APPLICATION PACKAGE\n{'═' * 60}\n{meta}\n\n"
                    f"{'═' * 60}\nJOB FIT EVALUATION\n{'─' * 60}\n\n"
                    f"{r.get('evaluation', '')}\n\n"
                    f"{'═' * 60}\nCV SUMMARY\n{'─' * 60}\n\n"
                    f"{r.get('cv_summary', '')}\n\n"
                    f"{'═' * 60}\nCOVER LETTER\n{'─' * 60}\n\n"
                    f"{r.get('cover_letter', '')}\n"
                )
                self._write(self.pkg_output, output)
                self._add_tokens(toks)
                self._set_status(f"Package complete — {toks:,} tokens")
                self._add_history("Package", output, toks, company, role)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Done", f"Package generated!\n\nTotal tokens used: {toks:,}"))
            except Exception as e:
                self._pkg_running = False
                self._write(self.pkg_output, f"Error: {e}")
                self._set_status("Error during package generation")

        threading.Thread(target=_do, daemon=True).start()

    # ═════════════════════════════════════════════════════════════════════════
    # History management
    # ═════════════════════════════════════════════════════════════════════════

    def _load_history(self) -> list:
        if Path(HISTORY_FILE).exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[History] save error: {e}")

    def _add_history(self, entry_type: str, content: str, tokens: int = 0,
                     company: str | None = None, role: str | None = None):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type":      entry_type,
            "company":   company or "",
            "role":      role    or "",
            "model":     self.model_var.get(),
            "tokens":    tokens,
            "content":   content,
        }
        self.history.insert(0, entry)
        self._save_history()
        self.root.after(0, self._refresh_hist_list)

    def _refresh_hist_list(self):
        if not hasattr(self, "_hist_list"):
            return
        self._hist_list.delete(0, "end")
        for e in self.history:
            tag  = f"[{e['type']:<12}]"
            ts   = e["timestamp"]
            co   = f"  {e['company']}" if e.get("company") else ""
            self._hist_list.insert("end", f"{ts}  {tag}{co}")

    def _on_hist_select(self, _event=None):
        sel = self._hist_list.curselection()
        if not sel or sel[0] >= len(self.history):
            return
        e   = self.history[sel[0]]
        meta = f"[{e['type']}]  {e['timestamp']}"
        if e.get("company"): meta += f"  |  {e['company']}"
        if e.get("role"):    meta += f"  —  {e['role']}"
        meta += f"  |  {e['tokens']:,} tokens  |  {e['model']}"
        self._hist_meta.configure(text=meta)
        self._write(self.hist_content, e.get("content", ""))

    def _delete_hist_entry(self):
        sel = self._hist_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an entry first.")
            return
        if messagebox.askyesno("Delete", "Delete this history entry?"):
            del self.history[sel[0]]
            self._save_history()
            self._refresh_hist_list()
            self._clear_text(self.hist_content)
            self._hist_meta.configure(text="Select an entry to view its content")

    def _clear_history(self):
        if not self.history:
            return
        if messagebox.askyesno("Clear All", "Delete all history entries?\nThis cannot be undone."):
            self.history.clear()
            self._save_history()
            self._refresh_hist_list()
            self._clear_text(self.hist_content)
            self._hist_meta.configure(text="Select an entry to view its content")

    # ═════════════════════════════════════════════════════════════════════════
    # Utility helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _check_init(self) -> bool:
        if not self.assistant:
            messagebox.showwarning(
                "Not Initialized",
                "Please initialize the assistant in the Setup tab first."
            )
            self._nav_to("Setup")
            return False
        return True

    def _set_status(self, msg: str):
        self.root.after(0, lambda: self._status_lbl.configure(text=msg))

    def _add_tokens(self, n: int):
        self._session_tokens += n
        cost = (self._session_tokens / 1000) * 0.01
        self.root.after(0, lambda: self._token_lbl.configure(
            text=f"Session tokens: {self._session_tokens:,}  |  Est. cost: ${cost:.3f}"
        ))

    def _write(self, widget: tk.Text, text: str):
        """Thread-safe: replace widget content."""
        def _do():
            widget.configure(state="normal")
            widget.delete(1.0, "end")
            widget.insert("end", text)
            widget.configure(state="disabled")
        self.root.after(0, _do)

    def _paste_to(self, widget: tk.Text):
        try:
            text = self.root.clipboard_get()
            widget.delete(1.0, "end")
            widget.insert(1.0, text)
        except Exception:
            messagebox.showwarning("Clipboard", "Nothing to paste.")

    def _save_text(self, widget: tk.Text):
        content = widget.get(1.0, "end").strip()
        if not content:
            messagebox.showwarning("Empty", "Nothing to save.")
            return
        fname = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown", "*.md")],
            initialfile=f"application_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        )
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
                self._set_status(f"Saved: {Path(fname).name}")
                messagebox.showinfo("Saved", f"File saved:\n{fname}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def _copy_text(self, widget: tk.Text):
        content = widget.get(1.0, "end").strip()
        if not content:
            messagebox.showwarning("Empty", "Nothing to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._set_status("Copied to clipboard")

    def _clear_text(self, widget: tk.Text):
        widget.configure(state="normal")
        widget.delete(1.0, "end")
        widget.configure(state="disabled")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    JobAssistantV2(root)
    root.mainloop()


if __name__ == "__main__":
    main()
