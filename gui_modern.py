#!/usr/bin/env python3
"""
Job Application Assistant - Modern GUI with ttkbootstrap
A beautiful, modern interface for the job application assistant
"""

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    BOOTSTRAP_AVAILABLE = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    BOOTSTRAP_AVAILABLE = False
    print("Note: Install ttkbootstrap for enhanced UI: pip install ttkbootstrap")

from tkinter import scrolledtext, filedialog, messagebox
import threading
from pathlib import Path
from job_application_assistant import JobApplicationAssistant
import os
from datetime import datetime


class ModernJobApplicationGUI:
    """Modern GUI application with enhanced design"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Assistant - Reza")
        self.root.geometry("1400x900")
        
        # Initialize variables
        self.assistant = None
        self.cv_path = tk.StringVar(value="reza_cv.pdf")
        self.model_var = tk.StringVar(value="gpt-4o")
        self.company_name = tk.StringVar()
        self.role_title = tk.StringVar()
        self.current_tokens = 0
        
        # Create UI
        self.create_ui()
        
        # Try to auto-initialize
        self.auto_initialize()
    
    def create_ui(self):
        """Create the main user interface"""
        
        # Header
        self.create_header()
        
        # Main content area with notebook
        self.create_notebook()
        
        # Footer/Status bar
        self.create_footer()
    
    def create_header(self):
        """Create header section"""
        if BOOTSTRAP_AVAILABLE:
            header = ttk.Frame(self.root, bootstyle="primary")
        else:
            header = tk.Frame(self.root, bg="#2196F3", height=80)
        
        header.pack(fill='x', side='top')
        
        # Title
        title_label = tk.Label(
            header,
            text="🎯 Job Application Assistant",
            font=('Segoe UI', 24, 'bold'),
            bg="#2196F3" if not BOOTSTRAP_AVAILABLE else None,
            fg="white",
            pady=15
        )
        title_label.pack(side='left', padx=30)
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text="AI-Powered Job Application Support for Reza",
            font=('Segoe UI', 11),
            bg="#2196F3" if not BOOTSTRAP_AVAILABLE else None,
            fg="white",
            pady=15
        )
        subtitle.pack(side='left', padx=10)
    
    def create_notebook(self):
        """Create tabbed interface"""
        if BOOTSTRAP_AVAILABLE:
            self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self.root)
        
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create tabs
        self.setup_tab = self.create_setup_tab()
        self.evaluate_tab = self.create_evaluate_tab()
        self.materials_tab = self.create_materials_tab()
        self.package_tab = self.create_package_tab()
        self.history_tab = self.create_history_tab()
        
        self.notebook.add(self.setup_tab, text="  ⚙️ Setup  ")
        self.notebook.add(self.evaluate_tab, text="  📊 Evaluate  ")
        self.notebook.add(self.materials_tab, text="  ✍️ Generate  ")
        self.notebook.add(self.package_tab, text="  📦 Package  ")
        self.notebook.add(self.history_tab, text="  📜 History  ")
    
    def create_footer(self):
        """Create footer with status bar"""
        if BOOTSTRAP_AVAILABLE:
            footer = ttk.Frame(self.root, bootstyle="secondary")
        else:
            footer = tk.Frame(self.root, bg="#1976D2", height=35)
        
        footer.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            footer,
            text="Ready",
            font=('Segoe UI', 9),
            bg="#1976D2" if not BOOTSTRAP_AVAILABLE else None,
            fg="white",
            anchor='w',
            padx=15,
            pady=8
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        self.token_label = tk.Label(
            footer,
            text="Tokens: 0 | Est. Cost: $0.00",
            font=('Segoe UI', 9),
            bg="#1976D2" if not BOOTSTRAP_AVAILABLE else None,
            fg="white",
            anchor='e',
            padx=15,
            pady=8
        )
        self.token_label.pack(side='right')
    
    def create_setup_tab(self):
        """Create setup/configuration tab"""
        if BOOTSTRAP_AVAILABLE:
            tab = ttk.Frame(self.notebook)
        else:
            tab = tk.Frame(self.notebook, bg='#f5f5f5')
        
        # Main container
        container = tk.Frame(tab, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title section
        title_frame = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        title_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(
            title_frame,
            text="Configuration",
            font=('Segoe UI', 22, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Set up your CV and API configuration",
            font=('Segoe UI', 11),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None,
            fg='#666'
        ).pack(anchor='w', pady=(5, 0))
        
        # CV Configuration
        if BOOTSTRAP_AVAILABLE:
            cv_frame = ttk.LabelFrame(container, text="CV Configuration", bootstyle="primary", padding=20)
        else:
            cv_frame = tk.LabelFrame(container, text="CV Configuration", font=('Segoe UI', 11, 'bold'), 
                                     bg='white', padx=20, pady=20)
        cv_frame.pack(fill='x', pady=(0, 20))
        
        cv_inner = tk.Frame(cv_frame, bg='white' if not BOOTSTRAP_AVAILABLE else None)
        cv_inner.pack(fill='x')
        
        tk.Label(
            cv_inner,
            text="CV PDF File:",
            font=('Segoe UI', 10, 'bold'),
            bg='white' if not BOOTSTRAP_AVAILABLE else None
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        if BOOTSTRAP_AVAILABLE:
            cv_entry = ttk.Entry(cv_inner, textvariable=self.cv_path, width=60)
        else:
            cv_entry = tk.Entry(cv_inner, textvariable=self.cv_path, font=('Segoe UI', 10), width=60)
        cv_entry.grid(row=0, column=1, padx=(15, 10), pady=10)
        
        if BOOTSTRAP_AVAILABLE:
            browse_btn = ttk.Button(cv_inner, text="Browse", command=self.browse_cv, bootstyle="info-outline")
        else:
            browse_btn = tk.Button(cv_inner, text="Browse", command=self.browse_cv, 
                                   bg='#2196F3', fg='white', relief='flat', padx=20, pady=5)
        browse_btn.grid(row=0, column=2, pady=10)
        
        # API Configuration
        if BOOTSTRAP_AVAILABLE:
            api_frame = ttk.LabelFrame(container, text="API Configuration", bootstyle="primary", padding=20)
        else:
            api_frame = tk.LabelFrame(container, text="API Configuration", font=('Segoe UI', 11, 'bold'),
                                      bg='white', padx=20, pady=20)
        api_frame.pack(fill='x', pady=(0, 20))
        
        api_inner = tk.Frame(api_frame, bg='white' if not BOOTSTRAP_AVAILABLE else None)
        api_inner.pack(fill='x')
        
        tk.Label(
            api_inner,
            text="OpenAI Model:",
            font=('Segoe UI', 10, 'bold'),
            bg='white' if not BOOTSTRAP_AVAILABLE else None
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        model_combo = ttk.Combobox(
            api_inner,
            textvariable=self.model_var,
            values=["gpt-4o (Recommended)", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo (Budget)"],
            state='readonly',
            width=40
        )
        model_combo.grid(row=0, column=1, sticky='w', padx=(15, 0), pady=10)
        model_combo.current(0)
        
        tk.Label(
            api_inner,
            text="API Key Status:",
            font=('Segoe UI', 10, 'bold'),
            bg='white' if not BOOTSTRAP_AVAILABLE else None
        ).grid(row=1, column=0, sticky='w', pady=10)
        
        self.api_status_label = tk.Label(
            api_inner,
            text="⏳ Checking...",
            font=('Segoe UI', 10),
            bg='white' if not BOOTSTRAP_AVAILABLE else None,
            fg='#FF9800'
        )
        self.api_status_label.grid(row=1, column=1, sticky='w', padx=(15, 0), pady=10)
        
        # Initialize button
        btn_frame = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        btn_frame.pack(pady=20)
        
        if BOOTSTRAP_AVAILABLE:
            init_btn = ttk.Button(btn_frame, text="🚀 Initialize Assistant", 
                                 command=self.initialize_assistant, bootstyle="success", width=30)
        else:
            init_btn = tk.Button(btn_frame, text="🚀 Initialize Assistant",
                               command=self.initialize_assistant, bg='#4CAF50', fg='white',
                               font=('Segoe UI', 12, 'bold'), relief='flat', padx=40, pady=12)
        init_btn.pack()
        
        # Status output
        if BOOTSTRAP_AVAILABLE:
            status_frame = ttk.LabelFrame(container, text="Status", bootstyle="secondary", padding=15)
        else:
            status_frame = tk.LabelFrame(container, text="Status", font=('Segoe UI', 11, 'bold'),
                                        bg='white', padx=15, pady=15)
        status_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.setup_status = scrolledtext.ScrolledText(
            status_frame,
            height=12,
            font=('Consolas', 9),
            wrap=tk.WORD,
            bg='#f9f9f9'
        )
        self.setup_status.pack(fill='both', expand=True)
        
        # Test button
        if BOOTSTRAP_AVAILABLE:
            test_btn = ttk.Button(container, text="🧪 Test Configuration",
                                 command=self.test_configuration, bootstyle="info-outline")
        else:
            test_btn = tk.Button(container, text="🧪 Test Configuration",
                               command=self.test_configuration, bg='#2196F3', fg='white',
                               relief='flat', padx=25, pady=8)
        test_btn.pack()
        
        return tab
    
    def create_evaluate_tab(self):
        """Create job evaluation tab"""
        if BOOTSTRAP_AVAILABLE:
            tab = ttk.Frame(self.notebook)
        else:
            tab = tk.Frame(self.notebook, bg='#f5f5f5')
        
        container = tk.Frame(tab, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(
            container,
            text="Job Fit Evaluation",
            font=('Segoe UI', 22, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            container,
            text="Strategic analysis of how well the role matches your profile",
            font=('Segoe UI', 11),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None,
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))
        
        # Input section
        if BOOTSTRAP_AVAILABLE:
            input_frame = ttk.LabelFrame(container, text="Job Description", bootstyle="primary", padding=15)
        else:
            input_frame = tk.LabelFrame(container, text="Job Description", 
                                       font=('Segoe UI', 11, 'bold'), bg='white', padx=15, pady=15)
        input_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.eval_job_text = scrolledtext.ScrolledText(
            input_frame,
            height=10,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.eval_job_text.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        btn_frame.pack(fill='x', pady=(0, 15))
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(btn_frame, text="🔍 Evaluate Fit", command=self.evaluate_job_fit,
                      bootstyle="success", width=20).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="📋 Paste from Clipboard", command=self.paste_from_clipboard,
                      bootstyle="info-outline", width=20).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="🗑️ Clear", command=lambda: self.eval_job_text.delete(1.0, tk.END),
                      bootstyle="danger-outline", width=15).pack(side='left', padx=5)
        else:
            tk.Button(btn_frame, text="🔍 Evaluate Fit", command=self.evaluate_job_fit,
                     bg='#4CAF50', fg='white', relief='flat', padx=20, pady=8).pack(side='left', padx=5)
            tk.Button(btn_frame, text="🗑️ Clear", command=lambda: self.eval_job_text.delete(1.0, tk.END),
                     bg='#FF9800', fg='white', relief='flat', padx=20, pady=8).pack(side='left', padx=5)
        
        # Results section
        if BOOTSTRAP_AVAILABLE:
            result_frame = ttk.LabelFrame(container, text="Evaluation Results", bootstyle="secondary", padding=15)
        else:
            result_frame = tk.LabelFrame(container, text="Evaluation Results",
                                        font=('Segoe UI', 11, 'bold'), bg='white', padx=15, pady=15)
        result_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.eval_results = scrolledtext.ScrolledText(
            result_frame,
            height=15,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.eval_results.pack(fill='both', expand=True)
        
        # Action buttons
        action_frame = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        action_frame.pack(fill='x')
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(action_frame, text="💾 Save Results", 
                      command=lambda: self.save_results(self.eval_results.get(1.0, tk.END)),
                      bootstyle="primary", width=18).pack(side='left', padx=5)
            ttk.Button(action_frame, text="📋 Copy", 
                      command=lambda: self.copy_to_clipboard(self.eval_results.get(1.0, tk.END)),
                      bootstyle="info-outline", width=18).pack(side='left', padx=5)
        else:
            tk.Button(action_frame, text="💾 Save Results",
                     command=lambda: self.save_results(self.eval_results.get(1.0, tk.END)),
                     bg='#2196F3', fg='white', relief='flat', padx=20, pady=8).pack(side='left', padx=5)
        
        return tab
    
    def create_materials_tab(self):
        """Create materials generation tab"""
        if BOOTSTRAP_AVAILABLE:
            tab = ttk.Frame(self.notebook)
        else:
            tab = tk.Frame(self.notebook, bg='#f5f5f5')
        
        # Use PanedWindow for split view
        paned = tk.PanedWindow(tab, orient='horizontal', sashrelief='flat', bg='#f5f5f5')
        paned.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Input
        left_panel = tk.Frame(paned, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        paned.add(left_panel, width=600)
        
        tk.Label(
            left_panel,
            text="Input",
            font=('Segoe UI', 18, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(10, 20), padx=15)
        
        # Job description
        if BOOTSTRAP_AVAILABLE:
            job_frame = ttk.LabelFrame(left_panel, text="Job Description", bootstyle="primary", padding=10)
        else:
            job_frame = tk.LabelFrame(left_panel, text="Job Description",
                                     font=('Segoe UI', 10, 'bold'), bg='white', padx=10, pady=10)
        job_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.gen_job_text = scrolledtext.ScrolledText(
            job_frame,
            height=18,
            font=('Segoe UI', 9),
            wrap=tk.WORD
        )
        self.gen_job_text.pack(fill='both', expand=True)
        
        # Optional info
        if BOOTSTRAP_AVAILABLE:
            info_frame = ttk.LabelFrame(left_panel, text="Optional Details", bootstyle="info", padding=10)
        else:
            info_frame = tk.LabelFrame(left_panel, text="Optional Details",
                                      font=('Segoe UI', 10, 'bold'), bg='white', padx=10, pady=10)
        info_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        tk.Label(info_frame, text="Company:", bg='white' if not BOOTSTRAP_AVAILABLE else None).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(info_frame, textvariable=self.company_name, width=35).grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        tk.Label(info_frame, text="Role Title:", bg='white' if not BOOTSTRAP_AVAILABLE else None).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(info_frame, textvariable=self.role_title, width=35).grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        info_frame.columnconfigure(1, weight=1)
        
        # Generation buttons
        gen_btn_frame = tk.Frame(left_panel, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        gen_btn_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(gen_btn_frame, text="📝 CV Summary", command=self.generate_cv_summary,
                      bootstyle="success", width=20).pack(fill='x', pady=3)
            ttk.Button(gen_btn_frame, text="✉️ Cover Letter", command=self.generate_cover_letter,
                      bootstyle="primary", width=20).pack(fill='x', pady=3)
        else:
            tk.Button(gen_btn_frame, text="📝 CV Summary", command=self.generate_cv_summary,
                     bg='#4CAF50', fg='white', relief='flat', pady=8).pack(fill='x', pady=3)
            tk.Button(gen_btn_frame, text="✉️ Cover Letter", command=self.generate_cover_letter,
                     bg='#2196F3', fg='white', relief='flat', pady=8).pack(fill='x', pady=3)
        
        # Right panel - Output
        right_panel = tk.Frame(paned, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        paned.add(right_panel)
        
        tk.Label(
            right_panel,
            text="Generated Content",
            font=('Segoe UI', 18, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(10, 20), padx=15)
        
        if BOOTSTRAP_AVAILABLE:
            output_frame = ttk.LabelFrame(right_panel, text="Output", bootstyle="secondary", padding=10)
        else:
            output_frame = tk.LabelFrame(right_panel, text="Output",
                                        font=('Segoe UI', 10, 'bold'), bg='white', padx=10, pady=10)
        output_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.gen_output = scrolledtext.ScrolledText(
            output_frame,
            height=25,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.gen_output.pack(fill='both', expand=True)
        
        # Output buttons
        output_btn_frame = tk.Frame(right_panel, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        output_btn_frame.pack(fill='x', padx=15)
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(output_btn_frame, text="💾 Save", 
                      command=lambda: self.save_results(self.gen_output.get(1.0, tk.END)),
                      bootstyle="success-outline", width=15).pack(side='left', padx=3)
            ttk.Button(output_btn_frame, text="📋 Copy",
                      command=lambda: self.copy_to_clipboard(self.gen_output.get(1.0, tk.END)),
                      bootstyle="info-outline", width=15).pack(side='left', padx=3)
            ttk.Button(output_btn_frame, text="🗑️ Clear",
                      command=lambda: self.gen_output.delete(1.0, tk.END),
                      bootstyle="danger-outline", width=15).pack(side='left', padx=3)
        else:
            tk.Button(output_btn_frame, text="💾 Save",
                     command=lambda: self.save_results(self.gen_output.get(1.0, tk.END)),
                     bg='#4CAF50', fg='white', relief='flat', padx=15, pady=8).pack(side='left', padx=3)
            tk.Button(output_btn_frame, text="📋 Copy",
                     command=lambda: self.copy_to_clipboard(self.gen_output.get(1.0, tk.END)),
                     bg='#2196F3', fg='white', relief='flat', padx=15, pady=8).pack(side='left', padx=3)
        
        return tab
    
    def create_package_tab(self):
        """Create complete package generation tab"""
        if BOOTSTRAP_AVAILABLE:
            tab = ttk.Frame(self.notebook)
        else:
            tab = tk.Frame(self.notebook, bg='#f5f5f5')
        
        container = tk.Frame(tab, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(
            container,
            text="Complete Application Package",
            font=('Segoe UI', 22, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            container,
            text="Generate evaluation + CV summary + cover letter all at once",
            font=('Segoe UI', 11),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None,
            fg='#666'
        ).pack(anchor='w', pady=(0, 25))
        
        # Input section
        if BOOTSTRAP_AVAILABLE:
            input_frame = ttk.LabelFrame(container, text="Input", bootstyle="primary", padding=15)
        else:
            input_frame = tk.LabelFrame(container, text="Input",
                                       font=('Segoe UI', 11, 'bold'), bg='white', padx=15, pady=15)
        input_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        tk.Label(
            input_frame,
            text="Job Description:",
            font=('Segoe UI', 10, 'bold'),
            bg='white' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(0, 8))
        
        self.pkg_job_text = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.pkg_job_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Company and role
        details_frame = tk.Frame(input_frame, bg='white' if not BOOTSTRAP_AVAILABLE else None)
        details_frame.pack(fill='x')
        
        tk.Label(details_frame, text="Company:", bg='white' if not BOOTSTRAP_AVAILABLE else None).grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Entry(details_frame, textvariable=self.company_name, width=35).grid(row=0, column=1, sticky='ew', padx=(0, 25))
        
        tk.Label(details_frame, text="Role:", bg='white' if not BOOTSTRAP_AVAILABLE else None).grid(row=0, column=2, sticky='w', padx=(0, 10))
        ttk.Entry(details_frame, textvariable=self.role_title, width=35).grid(row=0, column=3, sticky='ew')
        
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=1)
        
        # Generate button
        btn_container = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        btn_container.pack(pady=15)
        
        if BOOTSTRAP_AVAILABLE:
            gen_btn = ttk.Button(btn_container, text="🚀 Generate Complete Package",
                               command=self.generate_package, bootstyle="success", width=35)
        else:
            gen_btn = tk.Button(btn_container, text="🚀 Generate Complete Package",
                              command=self.generate_package, bg='#4CAF50', fg='white',
                              font=('Segoe UI', 13, 'bold'), relief='flat', padx=50, pady=15)
        gen_btn.pack()
        
        # Progress bar
        if BOOTSTRAP_AVAILABLE:
            self.progress = ttk.Progressbar(container, mode='indeterminate', bootstyle="success-striped")
        else:
            self.progress = ttk.Progressbar(container, mode='indeterminate', length=500)
        self.progress.pack(pady=10)
        
        # Output
        if BOOTSTRAP_AVAILABLE:
            output_frame = ttk.LabelFrame(container, text="Generated Package", bootstyle="secondary", padding=15)
        else:
            output_frame = tk.LabelFrame(container, text="Generated Package",
                                        font=('Segoe UI', 11, 'bold'), bg='white', padx=15, pady=15)
        output_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.pkg_output = scrolledtext.ScrolledText(
            output_frame,
            height=12,
            font=('Segoe UI', 9),
            wrap=tk.WORD
        )
        self.pkg_output.pack(fill='both', expand=True)
        
        # Action buttons
        action_frame = tk.Frame(container, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        action_frame.pack(fill='x')
        
        if BOOTSTRAP_AVAILABLE:
            ttk.Button(action_frame, text="💾 Save Package",
                      command=lambda: self.save_results(self.pkg_output.get(1.0, tk.END)),
                      bootstyle="primary", width=20).pack(side='left', padx=5)
            ttk.Button(action_frame, text="📋 Copy All",
                      command=lambda: self.copy_to_clipboard(self.pkg_output.get(1.0, tk.END)),
                      bootstyle="info-outline", width=20).pack(side='left', padx=5)
            ttk.Button(action_frame, text="📧 Export to Email",
                      command=self.export_to_email, bootstyle="secondary-outline", width=20).pack(side='left', padx=5)
        else:
            tk.Button(action_frame, text="💾 Save Package",
                     command=lambda: self.save_results(self.pkg_output.get(1.0, tk.END)),
                     bg='#2196F3', fg='white', relief='flat', padx=20, pady=8).pack(side='left', padx=5)
        
        return tab
    
    def create_history_tab(self):
        """Create history/recent applications tab"""
        if BOOTSTRAP_AVAILABLE:
            tab = ttk.Frame(self.notebook)
        else:
            tab = tk.Frame(self.notebook, bg='#f5f5f5')
        
        container = tk.Frame(tab, bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            container,
            text="Application History",
            font=('Segoe UI', 22, 'bold'),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            container,
            text="View and manage your recent job applications",
            font=('Segoe UI', 11),
            bg='#f5f5f5' if not BOOTSTRAP_AVAILABLE else None,
            fg='#666'
        ).pack(anchor='w', pady=(0, 20))
        
        # History display
        if BOOTSTRAP_AVAILABLE:
            history_frame = ttk.LabelFrame(container, text="Recent Applications", bootstyle="secondary", padding=15)
        else:
            history_frame = tk.LabelFrame(container, text="Recent Applications",
                                         font=('Segoe UI', 11, 'bold'), bg='white', padx=15, pady=15)
        history_frame.pack(fill='both', expand=True)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=25,
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.history_text.pack(fill='both', expand=True)
        self.history_text.insert(tk.END, "Application history will appear here...\n\n")
        self.history_text.insert(tk.END, "Each time you generate materials, they'll be logged for easy reference.")
        
        return tab
    
    # Helper methods (continue with implementation)
    def browse_cv(self):
        """Browse for CV file"""
        filename = filedialog.askopenfilename(
            title="Select CV PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.cv_path.set(filename)
    
    def paste_from_clipboard(self):
        """Paste from clipboard into job description"""
        try:
            clipboard_content = self.root.clipboard_get()
            self.eval_job_text.delete(1.0, tk.END)
            self.eval_job_text.insert(1.0, clipboard_content)
            self.update_status("Pasted from clipboard")
        except:
            messagebox.showwarning("Clipboard", "No text in clipboard")
    
    def auto_initialize(self):
        """Try to automatically initialize"""
        if Path(self.cv_path.get()).exists():
            # Check API key silently
            from dotenv import load_dotenv
            load_dotenv()
            if os.getenv('OPENAI_API_KEY'):
                self.initialize_assistant()
    
    def initialize_assistant(self):
        """Initialize the assistant"""
        cv_path = self.cv_path.get()
        
        if not Path(cv_path).exists():
            messagebox.showerror("CV Not Found", f"CV file not found: {cv_path}")
            return
        
        self.update_status("Initializing...")
        self.setup_status.delete(1.0, tk.END)
        self.setup_status.insert(tk.END, "🔄 Initializing Job Application Assistant...\n\n")
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.setup_status.insert(tk.END, "❌ OPENAI_API_KEY not found in .env file\n")
                self.api_status_label.config(text="❌ Not configured", fg="red")
                messagebox.showerror(
                    "API Key Missing",
                    "Please create a .env file with:\nOPENAI_API_KEY=your-key-here"
                )
                return
            
            self.api_status_label.config(text="✅ Connected", fg="#4CAF50")
            self.setup_status.insert(tk.END, "✅ API key found\n")
            
            # Extract model name without description
            model_text = self.model_var.get()
            model = model_text.split()[0]  # Get just "gpt-4o" from "gpt-4o (Recommended)"
            
            self.assistant = JobApplicationAssistant(cv_path=cv_path)
            
            self.setup_status.insert(tk.END, "✅ Assistant initialized\n")
            self.setup_status.insert(tk.END, f"✅ CV loaded: {Path(cv_path).name}\n")
            self.setup_status.insert(tk.END, f"✅ Model: {model}\n\n")
            self.setup_status.insert(tk.END, "🎉 Ready to process applications!\n")
            
            self.update_status("✅ Assistant ready")
            messagebox.showinfo("Success", "Assistant initialized!\n\nYou can now use all features.")
            
        except Exception as e:
            self.setup_status.insert(tk.END, f"\n❌ Error: {str(e)}\n")
            self.update_status("❌ Initialization failed")
            messagebox.showerror("Error", str(e))
    
    def test_configuration(self):
        """Test configuration"""
        if not self.assistant:
            messagebox.showwarning("Not Initialized", "Please initialize first")
            return
        
        self.update_status("Testing...")
        self.setup_status.insert(tk.END, "\n🧪 Running test...\n")
        
        def run_test():
            try:
                test_job = "ML Engineer\nPython, PyTorch, PhD"
                result = self.assistant.evaluate_job_fit(test_job)
                
                self.root.after(0, lambda: self.setup_status.insert(tk.END, "✅ Test passed!\n"))
                self.root.after(0, lambda: self.update_status(f"✅ Test OK - {result['tokens_used']} tokens"))
                self.root.after(0, lambda: messagebox.showinfo("Test Passed", "Configuration is working!"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Test Failed", str(e)))
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def evaluate_job_fit(self):
        """Evaluate job fit"""
        if not self.check_initialized():
            return
        
        job_description = self.eval_job_text.get(1.0, tk.END).strip()
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description")
            return
        
        self.update_status("🔍 Evaluating...")
        self.eval_results.delete(1.0, tk.END)
        self.eval_results.insert(tk.END, "Analyzing job fit...\n\nThis may take 10-30 seconds...")
        
        def run():
            try:
                model = self.model_var.get().split()[0]
                result = self.assistant.evaluate_job_fit(job_description, model=model)
                
                self.root.after(0, lambda: self.eval_results.delete(1.0, tk.END))
                self.root.after(0, lambda: self.eval_results.insert(tk.END, result['evaluation']))
                self.root.after(0, lambda: self.update_token_display(result['tokens_used']))
                self.root.after(0, lambda: self.update_status(f"✅ Evaluation complete"))
            except Exception as e:
                self.root.after(0, lambda: self.eval_results.delete(1.0, tk.END))
                self.root.after(0, lambda: self.eval_results.insert(tk.END, f"Error: {str(e)}"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def generate_cv_summary(self):
        """Generate CV summary"""
        if not self.check_initialized():
            return
        
        job_description = self.gen_job_text.get(1.0, tk.END).strip()
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description")
            return
        
        self.update_status("📝 Generating CV summary...")
        self.gen_output.delete(1.0, tk.END)
        self.gen_output.insert(tk.END, "Generating CV summary...")
        
        def run():
            try:
                model = self.model_var.get().split()[0]
                result = self.assistant.generate_cv_summary(job_description, model=model)
                
                self.root.after(0, lambda: self.gen_output.delete(1.0, tk.END))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, "=== CV SUMMARY ===\n\n"))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, result['summary']))
                self.root.after(0, lambda: self.update_token_display(result['tokens_used']))
                self.root.after(0, lambda: self.update_status("✅ CV summary generated"))
            except Exception as e:
                self.root.after(0, lambda: self.gen_output.delete(1.0, tk.END))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, f"Error: {str(e)}"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def generate_cover_letter(self):
        """Generate cover letter"""
        if not self.check_initialized():
            return
        
        job_description = self.gen_job_text.get(1.0, tk.END).strip()
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description")
            return
        
        company = self.company_name.get().strip() or None
        role = self.role_title.get().strip() or None
        
        self.update_status("✉️ Generating cover letter...")
        self.gen_output.delete(1.0, tk.END)
        self.gen_output.insert(tk.END, "Generating cover letter...")
        
        def run():
            try:
                model = self.model_var.get().split()[0]
                result = self.assistant.generate_cover_letter(job_description, company, role, model=model)
                
                self.root.after(0, lambda: self.gen_output.delete(1.0, tk.END))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, "=== COVER LETTER ===\n\n"))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, result['cover_letter']))
                self.root.after(0, lambda: self.update_token_display(result['tokens_used']))
                self.root.after(0, lambda: self.update_status("✅ Cover letter generated"))
            except Exception as e:
                self.root.after(0, lambda: self.gen_output.delete(1.0, tk.END))
                self.root.after(0, lambda: self.gen_output.insert(tk.END, f"Error: {str(e)}"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def generate_package(self):
        """Generate complete package"""
        if not self.check_initialized():
            return
        
        job_description = self.pkg_job_text.get(1.0, tk.END).strip()
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description")
            return
        
        company = self.company_name.get().strip() or None
        role = self.role_title.get().strip() or None
        
        self.update_status("🚀 Generating package...")
        self.pkg_output.delete(1.0, tk.END)
        self.pkg_output.insert(tk.END, "Generating complete package...\n\nThis will take 30-60 seconds...")
        self.progress.start()
        
        def run():
            try:
                model = self.model_var.get().split()[0]
                result = self.assistant.full_application_package(job_description, company, role, model=model)
                
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.pkg_output.delete(1.0, tk.END))
                
                output = f"{'='*70}\nCOMPLETE APPLICATION PACKAGE\n{'='*70}\n\n"
                if company:
                    output += f"Company: {company}\n"
                if role:
                    output += f"Role: {role}\n"
                output += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                output += f"{'='*70}\n\nEVALUATION\n{'='*70}\n\n{result['evaluation']}\n\n"
                output += f"{'='*70}\n\nCV SUMMARY\n{'='*70}\n\n{result['cv_summary']}\n\n"
                output += f"{'='*70}\n\nCOVER LETTER\n{'='*70}\n\n{result['cover_letter']}\n"
                
                self.root.after(0, lambda: self.pkg_output.insert(tk.END, output))
                self.root.after(0, lambda: self.update_token_display(result['total_tokens_used']))
                self.root.after(0, lambda: self.update_status("✅ Package complete"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Package generated!\n\nTokens: {result['total_tokens_used']}"))
            except Exception as e:
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.pkg_output.delete(1.0, tk.END))
                self.root.after(0, lambda: self.pkg_output.insert(tk.END, f"Error: {str(e)}"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def export_to_email(self):
        """Export package formatted for email"""
        content = self.pkg_output.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Content", "Generate a package first")
            return
        
        # Save with email-friendly formatting
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"email_package_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Email package saved!\n\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def save_results(self, content):
        """Save results"""
        if not content.strip():
            messagebox.showwarning("No Content", "No content to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown", "*.md")],
            initialfile=f"application_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Saved to:\n{filename}")
                self.update_status(f"✅ Saved to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def copy_to_clipboard(self, content):
        """Copy to clipboard"""
        if not content.strip():
            messagebox.showwarning("No Content", "No content to copy")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.update_status("📋 Copied to clipboard")
        messagebox.showinfo("Copied", "Content copied!")
    
    def check_initialized(self):
        """Check if initialized"""
        if not self.assistant:
            messagebox.showwarning("Not Initialized", "Please initialize in Setup tab first")
            self.notebook.select(0)
            return False
        return True
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def update_token_display(self, tokens):
        """Update token display with cost estimate"""
        self.current_tokens = tokens
        # GPT-4o pricing: ~$0.005 per 1K input tokens, ~$0.015 per 1K output tokens
        # Average estimate: ~$0.01 per 1K tokens
        cost = (tokens / 1000) * 0.01
        self.token_label.config(text=f"Tokens: {tokens:,} | Est. Cost: ${cost:.3f}")


def main():
    """Main entry point"""
    if BOOTSTRAP_AVAILABLE:
        root = ttk.Window(themename="cosmo")  # Modern theme
    else:
        root = tk.Tk()
    
    app = ModernJobApplicationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
