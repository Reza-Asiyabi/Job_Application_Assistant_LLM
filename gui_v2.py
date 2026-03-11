#!/usr/bin/env python3
"""
Job Application Assistant — GUI v2
Dark, modern desktop interface with sidebar navigation.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import os
import json
from datetime import datetime

from dotenv import load_dotenv
from job_application_assistant import JobApplicationAssistant

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":           "#1e1e2e",
    "surface":      "#2a2a3e",
    "surface2":     "#252537",
    "surface3":     "#16162a",
    "input_bg":     "#13131f",
    "accent":       "#7c6af7",
    "accent_dim":   "#5a4fd6",
    "accent2":      "#4f8ef7",
    "success":      "#4ade80",
    "success_dim":  "#166534",
    "warning":      "#fb923c",
    "danger":       "#f87171",
    "danger_dim":   "#7f1d1d",
    "text":         "#e2e2f0",
    "text_dim":     "#9a9ab0",
    "text_muted":   "#5a5a78",
    "border":       "#35354f",
}

FF = "Segoe UI"
FM = "Consolas"
HISTORY_FILE = "history.json"

NAV_ITEMS = [
    ("^", "Setup"),
    ("*", "Evaluate"),
    ("+", "Generate"),
    ("?", "Q & A"),
    ("#", "Package"),
    ("~", "Interview"),
    ("=", "History"),
]

STATUS_COLORS = {
    "Applied":   "#4f8ef7",
    "Interview": "#fb923c",
    "Offer":     "#4ade80",
    "Rejected":  "#f87171",
    "":          "#5a5a78",
}


# ─────────────────────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────────────────────
class JobAssistantV2:

    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Assistant")
        self.root.geometry("1400x860")
        self.root.minsize(1100, 700)
        self.root.configure(bg=C["bg"])

        # ── State ─────────────────────────────────────────────────────────
        self.assistant = None
        self.cv_path       = tk.StringVar(value=os.getenv("CV_PATH", "cv.pdf"))
        self.model_var     = tk.StringVar(value="gpt-4o")
        self.company_name  = tk.StringVar()
        self.role_title    = tk.StringVar()
        self.recruiter_name = tk.StringVar()
        self._session_tokens = 0
        self._pkg_running    = False
        self._shared_jd      = ""
        self._current_page   = "Setup"
        self.history = self._load_history()

        # ── Build UI ──────────────────────────────────────────────────────
        self._build_header()
        self._build_body()
        self._build_statusbar()
        self._nav_to("Setup")
        self.root.after(400, self._auto_init)

    # ═════════════════════════════════════════════════════════════════════════
    # Layout builders
    # ═════════════════════════════════════════════════════════════════════════

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=C["surface"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Job Application Assistant",
                 font=(FF, 15, "bold"), bg=C["surface"], fg=C["text"]).pack(side="left", padx=22, pady=14)
        self._init_dot = tk.Label(hdr, text="  Not initialized",
                                  font=(FF, 9), bg=C["surface"], fg=C["danger"])
        self._init_dot.pack(side="right", padx=22)
        tk.Frame(self.root, bg=C["accent"], height=2).pack(fill="x")

    def _build_body(self):
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)
        self._build_sidebar(body)
        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {
            "Setup":     self._page_setup(self.content),
            "Evaluate":  self._page_evaluate(self.content),
            "Generate":  self._page_generate(self.content),
            "Q & A":     self._page_qa(self.content),
            "Package":   self._page_package(self.content),
            "Interview": self._page_interview(self.content),
            "History":   self._page_history(self.content),
        }
        # Mapping of page names to their JD text widgets (for shared JD sync)
        self._jd_widgets = {
            "Evaluate":  self.eval_job_text,
            "Generate":  self.gen_job_text,
            "Q & A":     self.qa_job_text,
            "Package":   self.pkg_job_text,
            "Interview": self.interview_job_text,
        }

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=C["surface"], width=176)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=C["border"], width=1).pack(side="right", fill="y")
        tk.Label(sb, text="NAVIGATION", font=(FF, 7, "bold"),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=18, pady=(20, 6))
        self._nav_btns = {}
        for _icon, name in NAV_ITEMS:
            btn = tk.Button(sb, text=f"   {name}", font=(FF, 11),
                            anchor="w", relief="flat", bd=0, cursor="hand2",
                            bg=C["surface"], fg=C["text_dim"],
                            activebackground=C["surface2"], activeforeground=C["text"],
                            padx=8, pady=11, command=lambda n=name: self._nav_to(n))
            btn.pack(fill="x", padx=4, pady=1)
            self._nav_btns[name] = btn

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["surface3"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._status_lbl = tk.Label(bar, text="Ready", font=(FF, 9),
                                    bg=C["surface3"], fg=C["text_dim"], anchor="w")
        self._status_lbl.pack(side="left", padx=14)
        self._token_lbl = tk.Label(bar, text="Session tokens: 0  |  Est. cost: $0.000",
                                   font=(FF, 9), bg=C["surface3"], fg=C["text_dim"], anchor="e")
        self._token_lbl.pack(side="right", padx=14)

    # ═════════════════════════════════════════════════════════════════════════
    # Navigation (with shared JD sync)
    # ═════════════════════════════════════════════════════════════════════════

    def _nav_to(self, name):
        # Save JD from the page we're leaving
        if self._current_page in self._jd_widgets:
            text = self._jd_widgets[self._current_page].get(1.0, "end").strip()
            if text:
                self._shared_jd = text

        # Switch pages
        for p in self.pages.values():
            p.pack_forget()
        for n, b in self._nav_btns.items():
            b.configure(bg=C["surface"], fg=C["text_dim"])
        self.pages[name].pack(fill="both", expand=True)
        self._nav_btns[name].configure(bg=C["surface2"], fg=C["accent"])
        self._current_page = name

        # Restore shared JD into destination if it is empty
        if name in self._jd_widgets and self._shared_jd:
            target = self._jd_widgets[name]
            if not target.get(1.0, "end").strip():
                target.delete(1.0, "end")
                target.insert(1.0, self._shared_jd)

    # ═════════════════════════════════════════════════════════════════════════
    # Widget factory helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _card(self, parent, title=None, padx=16, pady=12):
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=C["surface"], padx=padx, pady=pady)
        inner.pack(fill="both", expand=True)
        if title:
            tk.Label(inner, text=title.upper(), font=(FF, 7, "bold"),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 8))
        return outer, inner

    def _btn(self, parent, text, cmd, style="primary", **kw):
        palettes = {
            "primary":   (C["accent"],      C["text"],      C["accent_dim"]),
            "secondary": (C["surface2"],    C["text_dim"],  C["border"]),
            "success":   (C["success_dim"], C["success"],   "#14532d"),
            "danger":    (C["danger_dim"],  C["danger"],    "#450a0a"),
            "ghost":     (C["bg"],          C["text_muted"],C["surface2"]),
            "warning":   ("#7c3d12",        C["warning"],   "#92400e"),
        }
        bg, fg, abg = palettes.get(style, palettes["primary"])
        return tk.Button(parent, text=text, command=cmd, relief="flat", bd=0,
                         cursor="hand2", font=(FF, 10, "bold"),
                         bg=bg, fg=fg, activebackground=abg, activeforeground=fg,
                         padx=14, pady=7, **kw)

    def _textarea(self, parent, height=8, mono=False):
        ff = FM if mono else FF
        t = tk.Text(parent, height=height, font=(ff, 10),
                    bg=C["input_bg"], fg=C["text"],
                    insertbackground=C["accent"], selectbackground=C["accent_dim"],
                    selectforeground=C["text"], relief="flat", bd=0,
                    wrap="word", padx=10, pady=8, spacing1=2)
        sb = tk.Scrollbar(parent, command=t.yview, bg=C["surface2"],
                          troughcolor=C["surface3"], relief="flat")
        t.configure(yscrollcommand=sb.set)
        return t, sb

    def _entry(self, parent, textvariable=None, width=30):
        return tk.Entry(parent, textvariable=textvariable, font=(FF, 10),
                        bg=C["input_bg"], fg=C["text"],
                        insertbackground=C["accent"], relief="flat", bd=0, width=width)

    def _section_header(self, parent, title, subtitle=None):
        f = tk.Frame(parent, bg=C["bg"])
        tk.Label(f, text=title, font=(FF, 19, "bold"), bg=C["bg"], fg=C["text"]).pack(anchor="w")
        if subtitle:
            tk.Label(f, text=subtitle, font=(FF, 10), bg=C["bg"], fg=C["text_dim"]).pack(anchor="w", pady=(2, 0))
        tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=(10, 0))
        return f

    def _lbl(self, parent, text, bg=None, size=9, bold=False, dim=False):
        bg = bg or C["bg"]
        return tk.Label(parent, text=text, font=(FF, size, "bold" if bold else ""),
                        bg=bg, fg=C["text_muted"] if dim else C["text"])

    def _inset_area(self, parent, height=10, mono=False):
        """A textarea inside a 1px border frame. Exposes ._container for packing."""
        border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner  = tk.Frame(border, bg=C["input_bg"])
        inner.pack(fill="both", expand=True)
        t, sb = self._textarea(inner, height=height, mono=mono)
        t.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        t._container = border
        return t, sb

    def _optional_details_card(self, parent, show_recruiter=False):
        """Shared Optional Details card used in Generate and Package tabs."""
        opt_outer, opt_card = self._card(parent, "Optional Details", padx=12, pady=10)
        opt_card.configure(bg=C["surface"])
        for label, var in [("Company", self.company_name), ("Role Title", self.role_title)]:
            row = tk.Frame(opt_card, bg=C["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=(FF, 9), bg=C["surface"],
                     fg=C["text_dim"], width=10, anchor="w").pack(side="left")
            self._entry(row, textvariable=var, width=42).pack(side="left", fill="x", expand=True, ipady=5)
        if show_recruiter:
            row = tk.Frame(opt_card, bg=C["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text="Recruiter", font=(FF, 9), bg=C["surface"],
                     fg=C["text_dim"], width=10, anchor="w").pack(side="left")
            self._entry(row, textvariable=self.recruiter_name, width=42).pack(side="left", fill="x", expand=True, ipady=5)
        # Auto-extract button
        ext_row = tk.Frame(opt_card, bg=C["surface"])
        ext_row.pack(fill="x", pady=(8, 0))
        self._btn(ext_row, "Auto-extract from JD", self._auto_extract_job_details, style="ghost").pack(side="left")
        return opt_outer

    def _eval_context_label(self, parent):
        """A small label showing whether evaluation context is available."""
        lbl = tk.Label(parent, text="", font=(FF, 8), bg=C["bg"])
        lbl._update = lambda: lbl.configure(
            text="  Evaluation context: available (used in generation)" if (self.assistant and self.assistant._last_evaluation) else "  Evaluation context: not available",
            fg=C["success"] if (self.assistant and self.assistant._last_evaluation) else C["text_muted"],
        )
        return lbl

    # ═════════════════════════════════════════════════════════════════════════
    # Pages
    # ═════════════════════════════════════════════════════════════════════════

    def _page_setup(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Setup", "Configure your CV and API settings").pack(fill="x", pady=(0, 24))

        # CV card
        cv_outer, cv_card = self._card(inner, "CV Configuration")
        cv_outer.pack(fill="x", pady=(0, 14))
        self._lbl(cv_card, "CV PDF File", bg=C["surface"], dim=True).pack(anchor="w", pady=(0, 4))
        cv_row = tk.Frame(cv_card, bg=C["surface"])
        cv_row.pack(fill="x")
        self._entry(cv_row, textvariable=self.cv_path, width=64).pack(side="left", fill="x", expand=True, ipady=6)
        self._btn(cv_row, "Browse ...", self._browse_cv, style="ghost").pack(side="left", padx=(8, 0))

        # API card
        api_outer, api_card = self._card(inner, "API Configuration")
        api_outer.pack(fill="x", pady=(0, 14))
        self._lbl(api_card, "Model", bg=C["surface"], dim=True).pack(anchor="w", pady=(0, 6))
        model_row = tk.Frame(api_card, bg=C["surface"])
        model_row.pack(anchor="w", pady=(0, 12))
        self._model_btns = {}
        for m in ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]:
            b = tk.Button(model_row, text=m, relief="flat", bd=0, cursor="hand2",
                          font=(FF, 9), bg=C["input_bg"], fg=C["text_dim"],
                          activebackground=C["accent_dim"], activeforeground=C["text"],
                          padx=12, pady=5, command=lambda mv=m: self._select_model(mv))
            b.pack(side="left", padx=2)
            self._model_btns[m] = b
        self._select_model("gpt-4o")
        key_row = tk.Frame(api_card, bg=C["surface"])
        key_row.pack(fill="x")
        self._lbl(key_row, "API Key:", bg=C["surface"], dim=True).pack(side="left", padx=(0, 10))
        self._api_status = tk.Label(key_row, text="Checking ...", font=(FF, 9),
                                    bg=C["surface"], fg=C["warning"])
        self._api_status.pack(side="left")

        # Buttons
        btn_row = tk.Frame(inner, bg=C["bg"])
        btn_row.pack(pady=10)
        self._btn(btn_row, "Initialize Assistant", self._initialize_assistant, style="primary").pack(side="left", padx=(0, 8))
        self._btn(btn_row, "Test Configuration",   self._test_configuration,   style="secondary").pack(side="left")

        # Log
        log_outer, log_card = self._card(inner, "Initialization Log")
        log_outer.pack(fill="both", expand=True, pady=(6, 0))
        log_card.configure(bg=C["surface"])
        self._setup_log, log_sb = self._textarea(log_card, height=14, mono=True)
        self._setup_log.configure(bg=C["surface3"], state="disabled")
        self._setup_log.pack(side="left", fill="both", expand=True)
        log_sb.pack(side="left", fill="y")
        return page

    def _page_evaluate(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Evaluate Fit",
                             "Paste a job description and get a strategic analysis").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.eval_job_text, _ = self._inset_area(left, height=22)
        self.eval_job_text._container.pack(fill="both", expand=True)
        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(10, 0))
        self._btn(lb, "Evaluate Fit",    self._evaluate_job_fit,                         style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard", lambda: self._paste_to(self.eval_job_text),     style="ghost").pack(side="left", padx=(0, 8))
        self._btn(lb, "Clear",           lambda: self.eval_job_text.delete(1.0, "end"),  style="ghost").pack(side="left")

        # Right
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self._lbl(right, "EVALUATION RESULTS", dim=True).pack(anchor="w", pady=(0, 4))
        self.eval_results, _ = self._inset_area(right, height=22)
        self.eval_results.configure(state="disabled")
        self.eval_results._container.pack(fill="both", expand=True)
        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save", lambda: self._save_text(self.eval_results), style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy", lambda: self._copy_text(self.eval_results), style="secondary").pack(side="left")
        return page

    def _page_generate(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Generate Materials",
                             "CV summaries, cover letters, and LinkedIn messages").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.gen_job_text, _ = self._inset_area(left, height=14)
        self.gen_job_text._container.pack(fill="both", expand=True)
        self._optional_details_card(left, show_recruiter=True).pack(fill="x", pady=(10, 0))
        # Eval context indicator
        self._gen_eval_lbl = self._eval_context_label(left)
        self._gen_eval_lbl.pack(anchor="w", pady=(6, 0))
        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(6, 0))
        self._btn(lb, "CV Summary",      self._generate_cv_summary,              style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Cover Letter",    self._generate_cover_letter,            style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "LinkedIn Message",self._generate_linkedin_message,        style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard", lambda: self._paste_to(self.gen_job_text), style="ghost").pack(side="left")

        # Right
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

    def _page_qa(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Application Q & A",
                             "Ask specific questions about the job or your application strategy").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left
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
        self._btn(lb, "Answer Question",  self._answer_question,                     style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard",  lambda: self._paste_to(self.qa_job_text),  style="ghost").pack(side="left")

        # Right
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

    def _page_package(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Complete Package",
                             "Evaluation + CV summary + cover letter — all streamed in sequence").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.pkg_job_text, _ = self._inset_area(left, height=13)
        self.pkg_job_text._container.pack(fill="both", expand=True)
        self._optional_details_card(left).pack(fill="x", pady=(10, 0))
        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(12, 0))
        self._btn(lb, "Generate Complete Package", self._generate_package, style="success").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard", lambda: self._paste_to(self.pkg_job_text), style="ghost").pack(side="left")
        self._progress_lbl = tk.Label(left, text="", font=(FF, 9), bg=C["bg"], fg=C["accent"])
        self._progress_lbl.pack(anchor="w", pady=(8, 0))

        # Right
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

    def _page_interview(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "Interview Prep",
                             "Technical questions, STAR stories, and smart questions to ask").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left
        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._lbl(left, "JOB DESCRIPTION", dim=True).pack(anchor="w", pady=(0, 4))
        self.interview_job_text, _ = self._inset_area(left, height=22)
        self.interview_job_text._container.pack(fill="both", expand=True)
        # Eval context indicator
        self._int_eval_lbl = self._eval_context_label(left)
        self._int_eval_lbl.pack(anchor="w", pady=(6, 0))
        lb = tk.Frame(left, bg=C["bg"])
        lb.pack(fill="x", pady=(6, 0))
        self._btn(lb, "Generate Interview Prep", self._generate_interview_prep,              style="primary").pack(side="left", padx=(0, 8))
        self._btn(lb, "Paste Clipboard",          lambda: self._paste_to(self.interview_job_text), style="ghost").pack(side="left", padx=(0, 8))
        self._btn(lb, "Clear",                    lambda: self.interview_job_text.delete(1.0, "end"), style="ghost").pack(side="left")

        # Right
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self._lbl(right, "INTERVIEW PREPARATION", dim=True).pack(anchor="w", pady=(0, 4))
        self.interview_output, _ = self._inset_area(right, height=22)
        self.interview_output.configure(state="disabled")
        self.interview_output._container.pack(fill="both", expand=True)
        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save",  lambda: self._save_text(self.interview_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",  lambda: self._copy_text(self.interview_output),  style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Clear", lambda: self._clear_text(self.interview_output), style="ghost").pack(side="left")
        return page

    def _page_history(self, parent):
        page  = tk.Frame(parent, bg=C["bg"])
        inner = tk.Frame(page, bg=C["bg"])
        inner.pack(fill="both", expand=True, padx=36, pady=28)
        self._section_header(inner, "History",
                             "All generated results — auto-saved with pipeline status tracking").pack(fill="x", pady=(0, 20))
        split = tk.Frame(inner, bg=C["bg"])
        split.pack(fill="both", expand=True)

        # Left — entry list
        left = tk.Frame(split, bg=C["bg"], width=310)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        self._lbl(left, "ENTRIES", dim=True).pack(anchor="w", pady=(0, 4))
        list_border = tk.Frame(left, bg=C["border"], padx=1, pady=1)
        list_border.pack(fill="both", expand=True)
        list_inner = tk.Frame(list_border, bg=C["surface"])
        list_inner.pack(fill="both", expand=True)
        self._hist_list = tk.Listbox(list_inner, font=(FM, 8),
                                     bg=C["surface"], fg=C["text"],
                                     selectbackground=C["accent_dim"],
                                     selectforeground=C["text"],
                                     relief="flat", bd=0, activestyle="none")
        hist_sb = tk.Scrollbar(list_inner, command=self._hist_list.yview,
                               bg=C["surface2"], troughcolor=C["surface3"], relief="flat")
        self._hist_list.configure(yscrollcommand=hist_sb.set)
        self._hist_list.pack(side="left", fill="both", expand=True)
        hist_sb.pack(side="left", fill="y")
        self._hist_list.bind("<<ListboxSelect>>", self._on_hist_select)
        hb = tk.Frame(left, bg=C["bg"])
        hb.pack(fill="x", pady=(10, 0))
        self._btn(hb, "Delete Selected", self._delete_hist_entry, style="danger").pack(side="left", padx=(0, 8))
        self._btn(hb, "Clear All",       self._clear_history,     style="ghost").pack(side="left")

        # Right — content viewer
        right = tk.Frame(split, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self._hist_meta = tk.Label(right, text="Select an entry to view its content",
                                   font=(FF, 9), bg=C["bg"], fg=C["text_dim"], anchor="w")
        self._hist_meta.pack(anchor="w", pady=(0, 4))

        # Status buttons
        status_row = tk.Frame(right, bg=C["bg"])
        status_row.pack(fill="x", pady=(0, 6))
        self._lbl(status_row, "Set Status:", dim=True).pack(side="left", padx=(0, 8))
        for label, style in [("Applied", "secondary"), ("Interview", "warning"),
                              ("Offer", "success"), ("Rejected", "danger"), ("Clear", "ghost")]:
            self._btn(status_row, label,
                      lambda s=label: self._set_hist_status(s),
                      style=style).pack(side="left", padx=(0, 4))

        self.hist_content, _ = self._inset_area(right, height=22)
        self.hist_content.configure(state="disabled")
        self.hist_content._container.pack(fill="both", expand=True)
        rb = tk.Frame(right, bg=C["bg"])
        rb.pack(fill="x", pady=(10, 0))
        self._btn(rb, "Save Entry", lambda: self._save_text(self.hist_content), style="secondary").pack(side="left", padx=(0, 8))
        self._btn(rb, "Copy",       lambda: self._copy_text(self.hist_content), style="secondary").pack(side="left")

        self._refresh_hist_list()
        return page

    # ═════════════════════════════════════════════════════════════════════════
    # Streaming helpers
    # ═════════════════════════════════════════════════════════════════════════

    def _stream_into(self, widget, prefix=""):
        """
        Prepare a widget for streaming and return a thread-safe chunk callback.
        MUST be called from the main thread. The returned callback is safe to
        call from a background thread.
        """
        widget.configure(state="normal")
        widget.delete(1.0, "end")
        if prefix:
            widget.insert("end", prefix)
        widget.configure(state="disabled")

        def _callback(chunk):
            def _do():
                widget.configure(state="normal")
                widget.insert("end", chunk)
                widget.see("end")
                widget.configure(state="disabled")
            self.root.after(0, _do)

        return _callback

    def _append_to(self, widget, text):
        """Thread-safe: append text to a widget without clearing it."""
        def _do():
            widget.configure(state="normal")
            widget.insert("end", text)
            widget.see("end")
            widget.configure(state="disabled")
        self.root.after(0, _do)

    def _make_append_callback(self, widget):
        """Return a stream_callback that appends (never clears) the widget."""
        def _callback(chunk):
            def _do():
                widget.configure(state="normal")
                widget.insert("end", chunk)
                widget.see("end")
                widget.configure(state="disabled")
            self.root.after(0, _do)
        return _callback

    # ═════════════════════════════════════════════════════════════════════════
    # Setup actions
    # ═════════════════════════════════════════════════════════════════════════

    def _select_model(self, model):
        self.model_var.set(model)
        for m, b in self._model_btns.items():
            b.configure(bg=C["accent"] if m == model else C["input_bg"],
                        fg=C["text"]   if m == model else C["text_dim"])

    def _browse_cv(self):
        f = filedialog.askopenfilename(title="Select CV PDF",
                                       filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if f:
            self.cv_path.set(f)

    def _log(self, msg):
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

    def _initialize_assistant(self, silent=False):
        cv = self.cv_path.get()
        if not Path(cv).exists():
            messagebox.showerror("CV Not Found", f"File not found:\n{cv}")
            return
        self._setup_log.configure(state="normal")
        self._setup_log.delete(1.0, "end")
        self._setup_log.configure(state="disabled")
        self._log("Initializing ...")
        self._set_status("Initializing assistant ...")
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self._log("ERROR: OPENAI_API_KEY not found in .env file")
            self._api_status.configure(text="Not configured", fg=C["danger"])
            if not silent:
                messagebox.showerror("API Key Missing",
                                     "Create a .env file in the project folder with:\n\nOPENAI_API_KEY=your-key")
            return
        self._api_status.configure(text="Found", fg=C["success"])
        self._log("API key found.")

        def _do():
            try:
                self.assistant = JobApplicationAssistant(cv_path=cv)
                self._log(f"CV loaded:  {Path(cv).name}")
                self._log(f"Model:      {self.model_var.get()}")
                profile_path = Path(__file__).parent / "profile.md"
                self._log(f"Profile:    {'profile.md' if profile_path.exists() else 'built-in'}")
                self._log("Ready.")
                self._set_status("Assistant ready")
                self.root.after(0, lambda: self._init_dot.configure(text="  Ready", fg=C["success"]))
                if not silent:
                    self.root.after(0, lambda: messagebox.showinfo("Ready", "Assistant initialized successfully!"))
            except Exception as e:
                self._log(f"ERROR: {e}")
                self._set_status("Initialization failed")
                if not silent:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=_do, daemon=True).start()

    def _test_configuration(self):
        if not self._check_init():
            return
        self._log("\nRunning configuration test ...")
        self._set_status("Testing ...")

        def _do():
            try:
                r = self.assistant.evaluate_job_fit("ML Engineer, Python, PyTorch",
                                                     model=self.model_var.get())
                toks = r.get("tokens_used", 0)
                self._log(f"Test passed!  Tokens: {toks}")
                self._set_status(f"Test passed — {toks} tokens")
                self.root.after(0, lambda: messagebox.showinfo("Test Passed", f"Working!\nTokens used: {toks}"))
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
        cb = self._stream_into(self.eval_results)
        self._set_status("Evaluating job fit ...")

        def _do():
            try:
                r    = self.assistant.evaluate_job_fit(jd, model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("evaluation", "")
                self._add_tokens(toks)
                self._set_status(f"Evaluation complete — {toks:,} tokens")
                self._add_history("Evaluation", text, toks, self.company_name.get(), self.role_title.get())
                # Update eval context indicators
                self.root.after(0, self._refresh_eval_labels)
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
        self._gen_eval_lbl._update()
        cb = self._stream_into(self.gen_output, prefix="CV SUMMARY\n" + "\u2500" * 60 + "\n\n")
        self._set_status("Generating CV summary ...")

        def _do():
            try:
                r    = self.assistant.generate_cv_summary(
                    jd, fit_evaluation=self.assistant._last_evaluation,
                    model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("summary", "")
                self._add_tokens(toks)
                self._set_status(f"CV summary generated — {toks:,} tokens")
                self._add_history("CV Summary", text, toks, self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.gen_output, f"Error: {e}")
                self._set_status("Error generating CV summary")

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
        self._gen_eval_lbl._update()
        cb = self._stream_into(self.gen_output, prefix="COVER LETTER\n" + "\u2500" * 60 + "\n\n")
        self._set_status("Generating cover letter ...")

        def _do():
            try:
                r    = self.assistant.generate_cover_letter(
                    jd, fit_evaluation=self.assistant._last_evaluation,
                    company_name=company, role_title=role,
                    model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("cover_letter", "")
                self._add_tokens(toks)
                self._set_status(f"Cover letter generated — {toks:,} tokens")
                self._add_history("Cover Letter", text, toks, company, role)
            except Exception as e:
                self._write(self.gen_output, f"Error: {e}")
                self._set_status("Error generating cover letter")

        threading.Thread(target=_do, daemon=True).start()

    def _generate_linkedin_message(self):
        if not self._check_init():
            return
        jd = self.gen_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        recruiter = self.recruiter_name.get().strip() or None
        cb = self._stream_into(self.gen_output, prefix="LINKEDIN MESSAGE\n" + "\u2500" * 60 + "\n\n")
        self._set_status("Generating LinkedIn message ...")

        def _do():
            try:
                r    = self.assistant.generate_linkedin_message(
                    jd, recruiter_name=recruiter,
                    fit_evaluation=self.assistant._last_evaluation,
                    model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("linkedin_message", "")
                self._add_tokens(toks)
                self._set_status(f"LinkedIn message generated — {toks:,} tokens")
                self._add_history("LinkedIn", text, toks, self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.gen_output, f"Error: {e}")
                self._set_status("Error generating LinkedIn message")

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
        cb = self._stream_into(self.qa_output)
        self._set_status("Answering question ...")

        def _do():
            try:
                r    = self.assistant.answer_application_question(
                    jd, question, fit_evaluation=self.assistant._last_evaluation,
                    model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("answer", "")
                self._add_tokens(toks)
                self._set_status(f"Answer generated — {toks:,} tokens")
                display = f"QUESTION\n{chr(8212)*60}\n{question}\n\nANSWER\n{chr(8212)*60}\n\n{text}"
                self._add_history("Q&A", display, toks, self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.qa_output, f"Error: {e}")
                self._set_status("Error during Q&A")

        threading.Thread(target=_do, daemon=True).start()

    def _generate_interview_prep(self):
        if not self._check_init():
            return
        jd = self.interview_job_text.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("Input Required", "Please paste a job description.")
            return
        self._int_eval_lbl._update()
        cb = self._stream_into(self.interview_output)
        self._set_status("Generating interview prep ...")

        def _do():
            try:
                r    = self.assistant.generate_interview_prep(
                    jd, fit_evaluation=self.assistant._last_evaluation,
                    model=self.model_var.get(), stream_callback=cb)
                toks = r.get("tokens_used", 0)
                text = r.get("interview_prep", "")
                self._add_tokens(toks)
                self._set_status(f"Interview prep generated — {toks:,} tokens")
                self._add_history("Interview Prep", text, toks, self.company_name.get(), self.role_title.get())
            except Exception as e:
                self._write(self.interview_output, f"Error: {e}")
                self._set_status("Error generating interview prep")

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

        # Clear the output widget for append-mode streaming
        self.pkg_output.configure(state="normal")
        self.pkg_output.delete(1.0, "end")
        self.pkg_output.configure(state="disabled")
        self._set_status("Generating package — Step 1/3: Evaluation ...")

        # Animated progress dots
        self._pkg_running = True

        def _animate():
            import time
            frames = ["   ", ".  ", ".. ", "..."]
            i = 0
            while self._pkg_running:
                dot = frames[i % 4]
                self.root.after(0, lambda d=dot: self._progress_lbl.configure(text="Working" + d))
                i += 1
                time.sleep(0.5)
            self.root.after(0, lambda: self._progress_lbl.configure(text=""))

        threading.Thread(target=_animate, daemon=True).start()

        def _do():
            total_tokens = 0
            eval_text = ""
            try:
                # Step 1: Evaluation
                self._append_to(self.pkg_output,
                                f"COMPLETE APPLICATION PACKAGE\n{'=' * 60}\n\n"
                                f"{'=' * 60}\nJOB FIT EVALUATION\n{'-' * 60}\n\n")
                cb1 = self._make_append_callback(self.pkg_output)
                r1  = self.assistant.evaluate_job_fit(jd, model=self.model_var.get(), stream_callback=cb1)
                eval_text = r1.get("evaluation", "")
                total_tokens += r1.get("tokens_used", 0)
                self._set_status("Generating package — Step 2/3: CV Summary ...")

                # Step 2: CV Summary
                self._append_to(self.pkg_output,
                                f"\n\n{'=' * 60}\nCV SUMMARY\n{'-' * 60}\n\n")
                cb2 = self._make_append_callback(self.pkg_output)
                r2  = self.assistant.generate_cv_summary(
                    jd, fit_evaluation=eval_text,
                    model=self.model_var.get(), stream_callback=cb2)
                total_tokens += r2.get("tokens_used", 0)
                self._set_status("Generating package — Step 3/3: Cover Letter ...")

                # Step 3: Cover Letter
                self._append_to(self.pkg_output,
                                f"\n\n{'=' * 60}\nCOVER LETTER\n{'-' * 60}\n\n")
                cb3 = self._make_append_callback(self.pkg_output)
                r3  = self.assistant.generate_cover_letter(
                    jd, fit_evaluation=eval_text,
                    company_name=company, role_title=role,
                    model=self.model_var.get(), stream_callback=cb3)
                total_tokens += r3.get("tokens_used", 0)

                self._pkg_running = False
                self._add_tokens(total_tokens)
                self._set_status(f"Package complete — {total_tokens:,} tokens")

                def _finalise():
                    full_text = self.pkg_output.get(1.0, "end").strip()
                    self._add_history("Package", full_text, total_tokens, company, role)
                    messagebox.showinfo("Done", f"Package generated!\n\nTotal tokens: {total_tokens:,}")

                self.root.after(0, _finalise)

            except Exception as e:
                self._pkg_running = False
                self._write(self.pkg_output, f"Error: {e}")
                self._set_status("Error during package generation")

        threading.Thread(target=_do, daemon=True).start()

    def _auto_extract_job_details(self):
        if not self._check_init():
            return
        jd_widget = self._jd_widgets.get(self._current_page)
        if jd_widget is None:
            messagebox.showwarning("No JD", "Navigate to a tab with a job description first.")
            return
        jd = jd_widget.get(1.0, "end").strip()
        if not jd:
            messagebox.showwarning("No JD", "Paste a job description first.")
            return
        self._set_status("Extracting job details ...")

        def _do():
            try:
                r = self.assistant.extract_job_details(jd, model=self.model_var.get())
                def _apply():
                    if r.get("company"):
                        self.company_name.set(r["company"])
                    if r.get("role"):
                        self.role_title.set(r["role"])
                    self._set_status(
                        f"Extracted: {r.get('company', '?')} — {r.get('role', '?')}"
                    )
                self.root.after(0, _apply)
            except Exception as e:
                self._set_status(f"Extraction error: {e}")

        threading.Thread(target=_do, daemon=True).start()

    # ═════════════════════════════════════════════════════════════════════════
    # History management
    # ═════════════════════════════════════════════════════════════════════════

    def _load_history(self):
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

    def _add_history(self, entry_type, content, tokens=0, company=None, role=None, status=""):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type":      entry_type,
            "company":   company or "",
            "role":      role    or "",
            "model":     self.model_var.get(),
            "tokens":    tokens,
            "content":   content,
            "status":    status,
        }
        self.history.insert(0, entry)
        self._save_history()
        self.root.after(0, self._refresh_hist_list)

    def _refresh_hist_list(self):
        if not hasattr(self, "_hist_list"):
            return
        self._hist_list.delete(0, "end")
        status_tag = {"Applied": "[Applied]  ", "Interview": "[Intv]     ",
                      "Offer": "[Offer]    ", "Rejected": "[Rejctd]   ", "": "           "}
        for e in self.history:
            st  = status_tag.get(e.get("status", ""), "           ")
            tag = "[{:<12}]".format(e.get("type", ""))
            co  = "  " + e["company"] if e.get("company") else ""
            self._hist_list.insert("end", f"{e['timestamp']}  {st}{tag}{co}")

    def _on_hist_select(self, _event=None):
        sel = self._hist_list.curselection()
        if not sel or sel[0] >= len(self.history):
            return
        e = self.history[sel[0]]
        status_txt = f" [{e.get('status')}]" if e.get("status") else ""
        meta = f"[{e['type']}]{status_txt}  {e['timestamp']}"
        if e.get("company"): meta += f"  |  {e['company']}"
        if e.get("role"):    meta += f"  —  {e['role']}"
        meta += f"  |  {e['tokens']:,} tokens  |  {e['model']}"
        self._hist_meta.configure(text=meta)
        self._write(self.hist_content, e.get("content", ""))

    def _set_hist_status(self, status):
        sel = self._hist_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a history entry first.")
            return
        idx = sel[0]
        new_status = "" if status == "Clear" else status
        self.history[idx]["status"] = new_status
        self._save_history()
        self._refresh_hist_list()
        self._hist_list.selection_set(idx)
        self._set_status(f"Status set to: {new_status or 'cleared'}")

    def _delete_hist_entry(self):
        sel = self._hist_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an entry to delete.")
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

    def _refresh_eval_labels(self):
        """Update eval context indicators on Generate and Interview tabs."""
        if hasattr(self, "_gen_eval_lbl"):
            self._gen_eval_lbl._update()
        if hasattr(self, "_int_eval_lbl"):
            self._int_eval_lbl._update()

    def _check_init(self):
        if not self.assistant:
            messagebox.showwarning("Not Initialized",
                                   "Please initialize the assistant in the Setup tab first.")
            self._nav_to("Setup")
            return False
        return True

    def _set_status(self, msg):
        self.root.after(0, lambda: self._status_lbl.configure(text=msg))

    def _add_tokens(self, n):
        self._session_tokens += n
        cost = (self._session_tokens / 1000) * 0.01
        self.root.after(0, lambda: self._token_lbl.configure(
            text=f"Session tokens: {self._session_tokens:,}  |  Est. cost: ${cost:.3f}"))

    def _write(self, widget, text):
        """Thread-safe: replace widget content entirely."""
        def _do():
            widget.configure(state="normal")
            widget.delete(1.0, "end")
            widget.insert("end", text)
            widget.configure(state="disabled")
        self.root.after(0, _do)

    def _paste_to(self, widget):
        try:
            text = self.root.clipboard_get()
            widget.delete(1.0, "end")
            widget.insert(1.0, text)
        except Exception:
            messagebox.showwarning("Clipboard", "Nothing to paste.")

    def _save_text(self, widget):
        content = widget.get(1.0, "end").strip()
        if not content:
            messagebox.showwarning("Empty", "Nothing to save.")
            return
        fname = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown", "*.md")],
            initialfile=f"application_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
                self._set_status(f"Saved: {Path(fname).name}")
                messagebox.showinfo("Saved", f"File saved:\n{fname}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def _copy_text(self, widget):
        content = widget.get(1.0, "end").strip()
        if not content:
            messagebox.showwarning("Empty", "Nothing to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._set_status("Copied to clipboard")

    def _clear_text(self, widget):
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
