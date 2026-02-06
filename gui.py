#!/usr/bin/env python3
"""
Job Application Assistant - Graphical User Interface
A modern, user-friendly GUI for the job application assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from pathlib import Path
from job_application_assistant import JobApplicationAssistant
import os
from datetime import datetime


class JobApplicationGUI:
    """Main GUI application for Job Application Assistant"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Job Application Assistant for Reza")
        self.root.geometry("1200x800")
        
        # Set theme colors
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2196F3"
        self.secondary_color = "#1976D2"
        self.text_color = "#333333"
        self.success_color = "#4CAF50"
        self.warning_color = "#FF9800"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Initialize variables
        self.assistant = None
        self.cv_path = tk.StringVar(value="reza_cv.pdf")
        self.model_var = tk.StringVar(value="gpt-4o")
        self.company_name = tk.StringVar()
        self.role_title = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Create UI
        self.create_ui()
        
        # Try to auto-initialize assistant
        self.auto_initialize()
    
    def create_ui(self):
        """Create the main user interface"""
        
        # Create notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.evaluate_tab = ttk.Frame(self.notebook)
        self.generate_tab = ttk.Frame(self.notebook)
        self.package_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text="⚙️ Setup")
        self.notebook.add(self.evaluate_tab, text="📊 Evaluate Fit")
        self.notebook.add(self.generate_tab, text="✍️ Generate Materials")
        self.notebook.add(self.package_tab, text="📦 Complete Package")
        
        # Build each tab
        self.build_setup_tab()
        self.build_evaluate_tab()
        self.build_generate_tab()
        self.build_package_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.root, bg=self.secondary_color, height=30)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.secondary_color,
            fg="white",
            anchor='w',
            padx=10
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        self.token_label = tk.Label(
            status_frame,
            text="Tokens: 0",
            bg=self.secondary_color,
            fg="white",
            anchor='e',
            padx=10
        )
        self.token_label.pack(side='right')
    
    def build_setup_tab(self):
        """Build the setup/configuration tab"""
        main_frame = tk.Frame(self.setup_tab, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="Setup & Configuration",
            font=('Arial', 20, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(0, 20))
        
        # CV Path section
        cv_frame = tk.LabelFrame(
            main_frame,
            text="CV Configuration",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        cv_frame.pack(fill='x', pady=10)
        
        tk.Label(
            cv_frame,
            text="CV PDF Path:",
            font=('Arial', 10),
            bg=self.bg_color
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        cv_entry = tk.Entry(
            cv_frame,
            textvariable=self.cv_path,
            font=('Arial', 10),
            width=50
        )
        cv_entry.grid(row=0, column=1, padx=10, pady=5)
        
        browse_btn = tk.Button(
            cv_frame,
            text="Browse",
            command=self.browse_cv,
            bg=self.primary_color,
            fg="white",
            font=('Arial', 9),
            cursor='hand2',
            relief='flat',
            padx=15,
            pady=5
        )
        browse_btn.grid(row=0, column=2, pady=5)
        
        # API Configuration
        api_frame = tk.LabelFrame(
            main_frame,
            text="API Configuration",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        api_frame.pack(fill='x', pady=10)
        
        tk.Label(
            api_frame,
            text="OpenAI Model:",
            font=('Arial', 10),
            bg=self.bg_color
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        model_combo = ttk.Combobox(
            api_frame,
            textvariable=self.model_var,
            values=["gpt-5.2", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            state='readonly',
            font=('Arial', 10),
            width=25
        )
        model_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(
            api_frame,
            text="API Key Status:",
            font=('Arial', 10),
            bg=self.bg_color
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.api_status_label = tk.Label(
            api_frame,
            text="Checking...",
            font=('Arial', 10),
            bg=self.bg_color,
            fg=self.warning_color
        )
        self.api_status_label.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Initialize button
        init_btn = tk.Button(
            main_frame,
            text="Initialize Assistant",
            command=self.initialize_assistant,
            bg=self.success_color,
            fg="white",
            font=('Arial', 12, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=30,
            pady=10
        )
        init_btn.pack(pady=20)
        
        # Status display
        self.setup_status = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            font=('Courier', 9),
            bg="white",
            wrap=tk.WORD
        )
        self.setup_status.pack(fill='both', expand=True, pady=10)
        
        # Test button
        test_btn = tk.Button(
            main_frame,
            text="Test Configuration",
            command=self.test_configuration,
            bg=self.primary_color,
            fg="white",
            font=('Arial', 10),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        )
        test_btn.pack(pady=5)
    
    def build_evaluate_tab(self):
        """Build the job evaluation tab"""
        main_frame = tk.Frame(self.evaluate_tab, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="Evaluate Job Fit",
            font=('Arial', 20, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(0, 20))
        
        # Job description input
        tk.Label(
            main_frame,
            text="Job Description:",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color
        ).pack(anchor='w', pady=(0, 5))
        
        self.eval_job_text = scrolledtext.ScrolledText(
            main_frame,
            height=12,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.eval_job_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill='x', pady=10)
        
        evaluate_btn = tk.Button(
            btn_frame,
            text="🔍 Evaluate Fit",
            command=self.evaluate_job_fit,
            bg=self.primary_color,
            fg="white",
            font=('Arial', 11, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=25,
            pady=10
        )
        evaluate_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="Clear",
            command=lambda: self.eval_job_text.delete(1.0, tk.END),
            bg=self.warning_color,
            fg="white",
            font=('Arial', 10),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=10
        )
        clear_btn.pack(side='left', padx=5)
        
        # Results display
        tk.Label(
            main_frame,
            text="Evaluation Results:",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color
        ).pack(anchor='w', pady=(10, 5))
        
        self.eval_results = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.eval_results.pack(fill='both', expand=True, pady=(0, 10))
        
        # Save button
        save_eval_btn = tk.Button(
            main_frame,
            text="💾 Save Results",
            command=lambda: self.save_results(self.eval_results.get(1.0, tk.END)),
            bg=self.success_color,
            fg="white",
            font=('Arial', 10),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        )
        save_eval_btn.pack(pady=5)
    
    def build_generate_tab(self):
        """Build the generate materials tab"""
        main_frame = tk.Frame(self.generate_tab, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="Generate Application Materials",
            font=('Arial', 20, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(0, 20))
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill='both', expand=True)
        
        # Left side - inputs
        left_frame = tk.Frame(input_frame, bg=self.bg_color)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="Job Description:",
            font=('Arial', 11, 'bold'),
            bg=self.bg_color
        ).pack(anchor='w', pady=(0, 5))
        
        self.gen_job_text = scrolledtext.ScrolledText(
            left_frame,
            height=20,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.gen_job_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Optional info
        info_frame = tk.LabelFrame(
            left_frame,
            text="Optional Information",
            font=('Arial', 10, 'bold'),
            bg=self.bg_color,
            padx=10,
            pady=10
        )
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(
            info_frame,
            text="Company Name:",
            font=('Arial', 9),
            bg=self.bg_color
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        tk.Entry(
            info_frame,
            textvariable=self.company_name,
            font=('Arial', 9),
            width=30
        ).grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        tk.Label(
            info_frame,
            text="Role Title:",
            font=('Arial', 9),
            bg=self.bg_color
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        tk.Entry(
            info_frame,
            textvariable=self.role_title,
            font=('Arial', 9),
            width=30
        ).grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        info_frame.columnconfigure(1, weight=1)
        
        # Generation buttons
        gen_btn_frame = tk.Frame(left_frame, bg=self.bg_color)
        gen_btn_frame.pack(fill='x', pady=10)
        
        tk.Button(
            gen_btn_frame,
            text="📝 CV Summary",
            command=self.generate_cv_summary,
            bg=self.primary_color,
            fg="white",
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='left', padx=3)
        
        tk.Button(
            gen_btn_frame,
            text="✉️ Cover Letter",
            command=self.generate_cover_letter,
            bg=self.primary_color,
            fg="white",
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='left', padx=3)
        
        # Right side - output
        right_frame = tk.Frame(input_frame, bg=self.bg_color)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="Generated Content:",
            font=('Arial', 11, 'bold'),
            bg=self.bg_color
        ).pack(anchor='w', pady=(0, 5))
        
        self.gen_output = scrolledtext.ScrolledText(
            right_frame,
            height=25,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.gen_output.pack(fill='both', expand=True, pady=(0, 10))
        
        # Output buttons
        output_btn_frame = tk.Frame(right_frame, bg=self.bg_color)
        output_btn_frame.pack(fill='x', pady=10)
        
        tk.Button(
            output_btn_frame,
            text="💾 Save",
            command=lambda: self.save_results(self.gen_output.get(1.0, tk.END)),
            bg=self.success_color,
            fg="white",
            font=('Arial', 9, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left', padx=3)
        
        tk.Button(
            output_btn_frame,
            text="📋 Copy",
            command=lambda: self.copy_to_clipboard(self.gen_output.get(1.0, tk.END)),
            bg=self.secondary_color,
            fg="white",
            font=('Arial', 9),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left', padx=3)
        
        tk.Button(
            output_btn_frame,
            text="🗑️ Clear",
            command=lambda: self.gen_output.delete(1.0, tk.END),
            bg=self.warning_color,
            fg="white",
            font=('Arial', 9),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left', padx=3)
    
    def build_package_tab(self):
        """Build the complete package generation tab"""
        main_frame = tk.Frame(self.package_tab, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="Generate Complete Application Package",
            font=('Arial', 20, 'bold'),
            bg=self.bg_color,
            fg=self.text_color
        )
        title.pack(pady=(0, 20))
        
        # Description
        desc = tk.Label(
            main_frame,
            text="Generate evaluation + CV summary + cover letter all at once",
            font=('Arial', 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        desc.pack(pady=(0, 15))
        
        # Input section
        input_frame = tk.LabelFrame(
            main_frame,
            text="Input",
            font=('Arial', 11, 'bold'),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        input_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(
            input_frame,
            text="Job Description:",
            font=('Arial', 10, 'bold'),
            bg=self.bg_color
        ).pack(anchor='w', pady=(0, 5))
        
        self.pkg_job_text = scrolledtext.ScrolledText(
            input_frame,
            height=10,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        self.pkg_job_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Company and role info
        info_grid = tk.Frame(input_frame, bg=self.bg_color)
        info_grid.pack(fill='x', pady=5)
        
        tk.Label(
            info_grid,
            text="Company:",
            font=('Arial', 10),
            bg=self.bg_color
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        tk.Entry(
            info_grid,
            textvariable=self.company_name,
            font=('Arial', 10),
            width=30
        ).grid(row=0, column=1, sticky='ew', padx=(0, 20))
        
        tk.Label(
            info_grid,
            text="Role:",
            font=('Arial', 10),
            bg=self.bg_color
        ).grid(row=0, column=2, sticky='w', padx=(0, 10))
        
        tk.Entry(
            info_grid,
            textvariable=self.role_title,
            font=('Arial', 10),
            width=30
        ).grid(row=0, column=3, sticky='ew')
        
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
        # Generate button
        generate_pkg_btn = tk.Button(
            main_frame,
            text="🚀 Generate Complete Package",
            command=self.generate_package,
            bg=self.success_color,
            fg="white",
            font=('Arial', 13, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=40,
            pady=15
        )
        generate_pkg_btn.pack(pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # Output section
        output_frame = tk.LabelFrame(
            main_frame,
            text="Generated Package",
            font=('Arial', 11, 'bold'),
            bg=self.bg_color,
            padx=15,
            pady=15
        )
        output_frame.pack(fill='both', expand=True, pady=10)
        
        self.pkg_output = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            font=('Arial', 9),
            wrap=tk.WORD
        )
        self.pkg_output.pack(fill='both', expand=True)
        
        # Action buttons
        action_frame = tk.Frame(main_frame, bg=self.bg_color)
        action_frame.pack(fill='x', pady=10)
        
        tk.Button(
            action_frame,
            text="💾 Save Package",
            command=lambda: self.save_results(self.pkg_output.get(1.0, tk.END)),
            bg=self.success_color,
            fg="white",
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=25,
            pady=10
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="📋 Copy All",
            command=lambda: self.copy_to_clipboard(self.pkg_output.get(1.0, tk.END)),
            bg=self.secondary_color,
            fg="white",
            font=('Arial', 10),
            cursor='hand2',
            relief='flat',
            padx=25,
            pady=10
        ).pack(side='left', padx=5)
    
    def browse_cv(self):
        """Browse for CV file"""
        filename = filedialog.askopenfilename(
            title="Select CV PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.cv_path.set(filename)
    
    def auto_initialize(self):
        """Try to automatically initialize the assistant"""
        if Path(self.cv_path.get()).exists():
            self.initialize_assistant()
    
    def initialize_assistant(self):
        """Initialize the job application assistant"""
        cv_path = self.cv_path.get()
        
        if not Path(cv_path).exists():
            messagebox.showerror(
                "CV Not Found",
                f"CV file not found: {cv_path}\n\nPlease select a valid CV PDF file."
            )
            return
        
        self.update_status("Initializing assistant...")
        self.setup_status.delete(1.0, tk.END)
        self.setup_status.insert(tk.END, "Initializing Job Application Assistant...\n\n")
        
        try:
            # Check API key
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.setup_status.insert(tk.END, "❌ OPENAI_API_KEY not found in .env file\n")
                self.api_status_label.config(text="❌ Not configured", fg="red")
                messagebox.showerror(
                    "API Key Missing",
                    "OPENAI_API_KEY not found in .env file.\n\n"
                    "Please create a .env file with:\n"
                    "OPENAI_API_KEY=your-key-here"
                )
                return
            
            self.api_status_label.config(text="✓ Found", fg=self.success_color)
            self.setup_status.insert(tk.END, "✓ API key found\n")
            
            # Initialize assistant
            self.assistant = JobApplicationAssistant(cv_path=cv_path)
            
            self.setup_status.insert(tk.END, "✓ Assistant initialized successfully\n")
            self.setup_status.insert(tk.END, f"✓ CV loaded: {cv_path}\n")
            self.setup_status.insert(tk.END, f"✓ Model: {self.model_var.get()}\n\n")
            self.setup_status.insert(tk.END, "Ready to process job applications!\n")
            
            self.update_status("Assistant initialized successfully")
            messagebox.showinfo(
                "Success",
                "Job Application Assistant initialized successfully!\n\n"
                "You can now use the other tabs to evaluate jobs and generate materials."
            )
            
        except Exception as e:
            self.setup_status.insert(tk.END, f"\n❌ Error: {str(e)}\n")
            self.update_status("Initialization failed")
            messagebox.showerror("Initialization Error", str(e))
    
    def test_configuration(self):
        """Test the configuration with a simple query"""
        if not self.assistant:
            messagebox.showwarning(
                "Not Initialized",
                "Please initialize the assistant first."
            )
            return
        
        self.update_status("Testing configuration...")
        self.setup_status.insert(tk.END, "\nRunning test query...\n")
        
        def run_test():
            try:
                test_job = "Machine Learning Engineer\nRequirements: Python, PyTorch, PhD"
                result = self.assistant.evaluate_job_fit(test_job)
                
                if 'error' in result:
                    self.setup_status.insert(tk.END, f"❌ Test failed: {result['error']}\n")
                else:
                    self.setup_status.insert(tk.END, "✓ Test successful!\n")
                    self.setup_status.insert(tk.END, f"Tokens used: {result['tokens_used']}\n")
                    self.update_status("Test successful")
                    
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Test Successful",
                        "Configuration test passed!\n\n"
                        f"Tokens used: {result['tokens_used']}\n"
                        "The assistant is working correctly."
                    ))
            except Exception as e:
                self.setup_status.insert(tk.END, f"❌ Test failed: {str(e)}\n")
                self.root.after(0, lambda: messagebox.showerror("Test Failed", str(e)))
        
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def evaluate_job_fit(self):
        """Evaluate job fit"""
        if not self.check_initialized():
            return
        
        job_description = self.eval_job_text.get(1.0, tk.END).strip()
        
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description.")
            return
        
        self.update_status("Evaluating job fit...")
        self.eval_results.delete(1.0, tk.END)
        self.eval_results.insert(tk.END, "Analyzing job fit...\n\nThis may take 10-30 seconds...\n")
        
        def run_evaluation():
            try:
                result = self.assistant.evaluate_job_fit(
                    job_description,
                    model=self.model_var.get()
                )
                
                if 'error' in result:
                    self.eval_results.delete(1.0, tk.END)
                    self.eval_results.insert(tk.END, f"Error: {result['error']}")
                    self.update_status("Evaluation failed")
                else:
                    self.eval_results.delete(1.0, tk.END)
                    self.eval_results.insert(tk.END, result['evaluation'])
                    self.update_status(f"Evaluation complete - {result['tokens_used']} tokens")
                    self.token_label.config(text=f"Tokens: {result['tokens_used']}")
            except Exception as e:
                self.eval_results.delete(1.0, tk.END)
                self.eval_results.insert(tk.END, f"Error: {str(e)}")
                self.update_status("Error occurred")
        
        thread = threading.Thread(target=run_evaluation, daemon=True)
        thread.start()
    
    def generate_cv_summary(self):
        """Generate CV summary"""
        if not self.check_initialized():
            return
        
        job_description = self.gen_job_text.get(1.0, tk.END).strip()
        
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description.")
            return
        
        self.update_status("Generating CV summary...")
        self.gen_output.delete(1.0, tk.END)
        self.gen_output.insert(tk.END, "Generating CV summary...\n\n")
        
        def run_generation():
            try:
                result = self.assistant.generate_cv_summary(
                    job_description,
                    model=self.model_var.get()
                )
                
                if 'error' in result:
                    self.gen_output.delete(1.0, tk.END)
                    self.gen_output.insert(tk.END, f"Error: {result['error']}")
                else:
                    self.gen_output.delete(1.0, tk.END)
                    self.gen_output.insert(tk.END, "=== CV SUMMARY ===\n\n")
                    self.gen_output.insert(tk.END, result['summary'])
                    self.update_status(f"CV summary generated - {result['tokens_used']} tokens")
                    self.token_label.config(text=f"Tokens: {result['tokens_used']}")
            except Exception as e:
                self.gen_output.delete(1.0, tk.END)
                self.gen_output.insert(tk.END, f"Error: {str(e)}")
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
    
    def generate_cover_letter(self):
        """Generate cover letter"""
        if not self.check_initialized():
            return
        
        job_description = self.gen_job_text.get(1.0, tk.END).strip()
        
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description.")
            return
        
        company = self.company_name.get().strip() or None
        role = self.role_title.get().strip() or None
        
        self.update_status("Generating cover letter...")
        self.gen_output.delete(1.0, tk.END)
        self.gen_output.insert(tk.END, "Generating cover letter...\n\n")
        
        def run_generation():
            try:
                result = self.assistant.generate_cover_letter(
                    job_description,
                    company_name=company,
                    role_title=role,
                    model=self.model_var.get()
                )
                
                if 'error' in result:
                    self.gen_output.delete(1.0, tk.END)
                    self.gen_output.insert(tk.END, f"Error: {result['error']}")
                else:
                    self.gen_output.delete(1.0, tk.END)
                    self.gen_output.insert(tk.END, "=== COVER LETTER ===\n\n")
                    self.gen_output.insert(tk.END, result['cover_letter'])
                    self.update_status(f"Cover letter generated - {result['tokens_used']} tokens")
                    self.token_label.config(text=f"Tokens: {result['tokens_used']}")
            except Exception as e:
                self.gen_output.delete(1.0, tk.END)
                self.gen_output.insert(tk.END, f"Error: {str(e)}")
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
    
    def generate_package(self):
        """Generate complete application package"""
        if not self.check_initialized():
            return
        
        job_description = self.pkg_job_text.get(1.0, tk.END).strip()
        
        if not job_description:
            messagebox.showwarning("Input Required", "Please enter a job description.")
            return
        
        company = self.company_name.get().strip() or None
        role = self.role_title.get().strip() or None
        
        self.update_status("Generating complete package...")
        self.pkg_output.delete(1.0, tk.END)
        self.pkg_output.insert(tk.END, "Generating complete application package...\n\n")
        self.pkg_output.insert(tk.END, "This will take 30-60 seconds...\n\n")
        
        self.progress.start()
        
        def run_generation():
            try:
                result = self.assistant.full_application_package(
                    job_description,
                    company_name=company,
                    role_title=role,
                    model=self.model_var.get()
                )
                
                self.progress.stop()
                
                if 'error' in result:
                    self.pkg_output.delete(1.0, tk.END)
                    self.pkg_output.insert(tk.END, f"Error: {result['error']}")
                else:
                    self.pkg_output.delete(1.0, tk.END)
                    
                    # Format the complete package
                    self.pkg_output.insert(tk.END, "="*70 + "\n")
                    self.pkg_output.insert(tk.END, "COMPLETE APPLICATION PACKAGE\n")
                    self.pkg_output.insert(tk.END, "="*70 + "\n\n")
                    
                    if company:
                        self.pkg_output.insert(tk.END, f"Company: {company}\n")
                    if role:
                        self.pkg_output.insert(tk.END, f"Role: {role}\n")
                    self.pkg_output.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    self.pkg_output.insert(tk.END, "\n" + "="*70 + "\n\n")
                    
                    self.pkg_output.insert(tk.END, "JOB FIT EVALUATION\n")
                    self.pkg_output.insert(tk.END, "="*70 + "\n\n")
                    self.pkg_output.insert(tk.END, result['evaluation'])
                    self.pkg_output.insert(tk.END, "\n\n" + "="*70 + "\n\n")
                    
                    self.pkg_output.insert(tk.END, "CV SUMMARY\n")
                    self.pkg_output.insert(tk.END, "="*70 + "\n\n")
                    self.pkg_output.insert(tk.END, result['cv_summary'])
                    self.pkg_output.insert(tk.END, "\n\n" + "="*70 + "\n\n")
                    
                    self.pkg_output.insert(tk.END, "COVER LETTER\n")
                    self.pkg_output.insert(tk.END, "="*70 + "\n\n")
                    self.pkg_output.insert(tk.END, result['cover_letter'])
                    self.pkg_output.insert(tk.END, "\n\n" + "="*70 + "\n")
                    
                    self.update_status(f"Package complete - {result['total_tokens_used']} tokens")
                    self.token_label.config(text=f"Tokens: {result['total_tokens_used']}")
                    
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success",
                        f"Complete application package generated!\n\n"
                        f"Total tokens used: {result['total_tokens_used']}\n\n"
                        "You can now save or copy the results."
                    ))
            except Exception as e:
                self.progress.stop()
                self.pkg_output.delete(1.0, tk.END)
                self.pkg_output.insert(tk.END, f"Error: {str(e)}")
                self.update_status("Error occurred")
        
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()
    
    def save_results(self, content):
        """Save results to file"""
        if not content or content.strip() == "":
            messagebox.showwarning("No Content", "No content to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ],
            initialfile=f"application_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Results saved to:\n{filename}")
                self.update_status(f"Saved to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")
    
    def copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        if not content or content.strip() == "":
            messagebox.showwarning("No Content", "No content to copy.")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.update_status("Copied to clipboard")
        messagebox.showinfo("Copied", "Content copied to clipboard!")
    
    def check_initialized(self):
        """Check if assistant is initialized"""
        if not self.assistant:
            messagebox.showwarning(
                "Not Initialized",
                "Please initialize the assistant first in the Setup tab."
            )
            self.notebook.select(0)  # Switch to setup tab
            return False
        return True
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set app icon if available
    try:
        # You can add an icon file later
        pass
    except:
        pass
    
    app = JobApplicationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
