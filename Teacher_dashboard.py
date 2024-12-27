import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
from PIL import Image, ImageTk

class TeacherDashboard:
    def __init__(self, root, user_info):
        self.root = root
        self.user_info = user_info
        self.root.title("Modern Teacher Dashboard")
        
        # Configure the window
        self.root.state('zoomed')
        
        # Color scheme matching the image
        self.colors = {
            'bg_dark': '#1B2838',      # Dark blue background
            'sidebar': '#1B2838',      # Same dark blue for sidebar
            'content': '#1B2838',      # Content area background
            'text': '#FFFFFF',         # White text
            'hover': '#a0a0a0',        # Hover color
            'button': '#2A3F5F',       # Button color
            'button_hover': '#34495E'   # Button hover color
        }

        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(root, style="Main.TFrame")
        self.main_container.pack(fill='both', expand=True)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.content_area = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_area.pack(side='left', fill='both', expand=True)
        
        # Create header
        self.create_header()
        
        # Create main content frame
        self.content_frame = ttk.Frame(self.content_area, style="Content.TFrame")
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Initialize with dashboard view
        self.show_profile()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame styles
        self.style.configure("Main.TFrame", background=self.colors['bg_dark'])
        self.style.configure("Content.TFrame", background=self.colors['content'])
        self.style.configure("Sidebar.TFrame", background=self.colors['sidebar'])
        
        # Label styles
        self.style.configure("Header.TLabel",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 24, 'bold'))
        
        self.style.configure("SidebarBtn.TLabel",
                           background=self.colors['sidebar'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 12),
                           padding=10)
        
        # Menu label style
        self.style.configure("Menu.TLabel",
                           background=self.colors['sidebar'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 12),
                           padding=0)
        
        # Button styles
        self.style.configure("Action.TButton",
                           background=self.colors['button'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11),
                           padding=(20, 10))
        
        # Treeview styles
        self.style.configure("Treeview",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['content'],
                           font=('Segoe UI', 11))
        
        self.style.configure("Treeview.Heading",
                           background=self.colors['button'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.map("Treeview",
                      background=[('selected', self.colors['button_hover'])],
                      foreground=[('selected', self.colors['text'])])

    def create_sidebar(self):
        sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Add spacing at top
        ttk.Frame(sidebar, style="Sidebar.TFrame", height=50).pack(fill='x')
        
        # Menu items with exact styling from image
        menu_items = [
            ("📝 Manage Exams", self.show_exams),
            ("❓ Manage Questions", self.show_questions),
            ("📊 View Results", self.show_results),
            ("👤 My Profile", self.show_profile)
        ]
        
        # Add menu items with more spacing
        for text, command in menu_items:
            menu_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
            menu_frame.pack(fill='x', pady=15)  # Increased spacing between items
            
            label = ttk.Label(menu_frame, 
                            text=text,
                            style="Menu.TLabel",
                            cursor="hand2")
            label.pack(fill='x', padx=20, pady=8, anchor='w')
            label.bind('<Button-1>', lambda e, cmd=command: cmd())
            
            # Add hover effect
            label.bind('<Enter>', lambda e, lbl=label: self.on_menu_hover(lbl, True))
            label.bind('<Leave>', lambda e, lbl=label: self.on_menu_hover(lbl, False))
        
        # Add logout at bottom with spacing
        ttk.Frame(sidebar, style="Sidebar.TFrame", height=50).pack(fill='x', expand=True)
        logout_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        logout_frame.pack(fill='x', pady=20, side='bottom')
        
        logout_label = ttk.Label(logout_frame,
                               text="🚪 Logout",
                               style="Menu.TLabel",
                               cursor="hand2")
        logout_label.pack(fill='x', padx=20, pady=8, anchor='w')
        logout_label.bind('<Button-1>', lambda e: self.logout())
        logout_label.bind('<Enter>', lambda e: self.on_menu_hover(logout_label, True))
        logout_label.bind('<Leave>', lambda e: self.on_menu_hover(logout_label, False))

    def on_menu_hover(self, label, entering):
        if entering:
            label.configure(foreground='#a0a0a0')  # Light gray on hover
        else:
            label.configure(foreground=self.colors['text'])  # Back to white

    def create_header(self):
        header = ttk.Frame(self.content_area, style="Content.TFrame")
        header.pack(fill='x', padx=20, pady=(20, 0))
        
        ttk.Label(header,
                 text="Teacher Dashboard",
                 style="Header.TLabel").pack(side='left')
        
        # Add current date/time
        current_time = datetime.now().strftime("%B %d, %Y")
        ttk.Label(header,
                 text=current_time,
                 style="SidebarBtn.TLabel").pack(side='right', padx=20)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_exams(self):
        self.clear_content()
        
        # Header and action buttons
        header_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Manage Exams", style="Title.TLabel").pack(side='left')
        
        button_frame = ttk.Frame(header_frame, style="Content.TFrame")
        button_frame.pack(side='right')
        
        ttk.Button(button_frame, text="Add Exam", style="Action.TButton",
                command=self.show_add_exam_frame).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Exam", style="Action.TButton",
                command=self.show_edit_exam_frame).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Exam", style="Action.TButton",
                command=self.delete_exam).pack(side='left', padx=5)
        
        # Create Treeview
        columns = ("ID", "Title", "Duration", "Total Marks")
        self.exam_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.exam_tree.heading(col, text=col)
            self.exam_tree.column(col, width=150)
        
        self.exam_tree.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical',
                                command=self.exam_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.exam_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate exams
        self.populate_exams()


    def populate_exams(self):
        # Clear existing items
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
            
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Get exams for the teacher's subject
            cursor.execute("""
                SELECT e.id, e.title, e.duration, e.total_marks
                FROM exams e
                JOIN teachers t ON e.subject_id = t.subject_id
                WHERE t.id = ?
            """, (self.user_info['id'],))
            
            for row in cursor.fetchall():
                self.exam_tree.insert("", 'end', values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            conn.close()

    def show_add_exam_frame(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Add New Exam", style="Title.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        fields = [("Title", tk.StringVar()), ("Duration (minutes)", tk.StringVar()), ("Total Marks", tk.StringVar())]
        entries = {}

        for idx, (label, var) in enumerate(fields):
            row = ttk.Frame(form_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            ttk.Label(row, text=label, style="Text.TLabel").pack(side='left', padx=5)
            entry = ttk.Entry(row, textvariable=var, style="Content.TEntry")
            entry.pack(side='left', fill='x', expand=True, padx=5)
            entries[label] = var

        # Subject for the exam (fixed based on teacher's subject)
        subject_row = ttk.Frame(form_frame, style="Content.TFrame")
        subject_row.pack(fill='x', pady=5)

        ttk.Label(subject_row, text="Subject", style="Text.TLabel").pack(side='left', padx=5)
        subject = self.user_info.get('subject', 'N/A')
        ttk.Label(subject_row, text=subject, style="Text.TLabel").pack(side='left', padx=5)

        submit_button = ttk.Button(form_frame, text="Add Exam", style="Action.TButton", 
                                command=lambda: self.add_exam(entries))
        submit_button.pack(pady=20)

        back_button = ttk.Button(form_frame, text="Back", style="Action.TButton", 
                                command=self.show_exams)
        back_button.pack(pady=10)

    def add_exam(self, entries):
        title = entries["Title"].get()
        duration = entries["Duration (minutes)"].get()
        total_marks = entries["Total Marks"].get()

        if not title or not duration or not total_marks:
            messagebox.showerror("Error", "All fields are required!")
            return

        subject_id = self.user_info.get('subject_id')
        
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO exams (title, subject_id, duration, total_marks, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (title, subject_id, duration, total_marks, self.user_info['id']))
            
            conn.commit()
            messagebox.showinfo("Success", "Exam added successfully!")
            self.show_exams()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            
        finally:
            conn.close()

    def show_edit_exam_frame(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an exam to edit!")
            return

        exam_id = self.exam_tree.item(selected_item)['values'][0]
        self.clear_content()
        
        ttk.Label(self.content_frame, text="Edit Exam", style="Title.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        fields = [("Title", tk.StringVar()), ("Duration (minutes)", tk.StringVar()), ("Total Marks", tk.StringVar())]
        entries = {}

        for idx, (label, var) in enumerate(fields):
            row = ttk.Frame(form_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            ttk.Label(row, text=label, style="Text.TLabel").pack(side='left', padx=5)
            entry = ttk.Entry(row, textvariable=var, style="Content.TEntry")
            entry.pack(side='left', fill='x', expand=True, padx=5)
            entries[label] = var

        # Fetch exam details from the database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT title, duration, total_marks 
                FROM exams 
                WHERE id = ?
            """, (exam_id,))
            exam = cursor.fetchone()
            
            entries["Title"].set(exam[0])
            entries["Duration (minutes)"].set(exam[1])
            entries["Total Marks"].set(exam[2])
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            
        finally:
            conn.close()

        submit_button = ttk.Button(form_frame, text="Save Changes", style="Action.TButton",
                                command=lambda: self.edit_exam(entries, exam_id))
        submit_button.pack(pady=20)

        back_button = ttk.Button(form_frame, text="Back", style="Action.TButton",
                                command=self.show_exams)
        back_button.pack(pady=10)

    def edit_exam(self, entries, exam_id):
        title = entries["Title"].get()
        duration = entries["Duration (minutes)"].get()
        total_marks = entries["Total Marks"].get()

        if not title or not duration or not total_marks:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE exams
                SET title = ?, duration = ?, total_marks = ?
                WHERE id = ?
            """, (title, duration, total_marks, exam_id))
            
            conn.commit()
            messagebox.showinfo("Success", "Exam updated successfully!")
            self.show_exams()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
            
        finally:
            conn.close()


    def delete_exam(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an exam to delete!")
            return

        exam_id = self.exam_tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this exam?")

        if not confirm:
            return

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
            conn.commit()
            messagebox.showinfo("Success", "Exam deleted successfully!")
            self.populate_exams()
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        
        finally:
            conn.close()


    def show_questions(self):
        self.clear_content()
        
        # Header and action buttons
        header_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Manage Questions", style="Title.TLabel").pack(side='left')
        
        button_frame = ttk.Frame(header_frame, style="Content.TFrame")
        button_frame.pack(side='right')
        
        ttk.Button(button_frame, text="Add Question", style="Action.TButton",
                command=self.show_add_question_frame).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Question", style="Action.TButton",
                command=self.show_edit_question_frame).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Question", style="Action.TButton",
                command=self.delete_question).pack(side='left', padx=5)
        
        # Create Treeview
        columns = ("ID", "Exam", "Question", "Correct Answer", "Marks")
        self.question_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        
        # Configure columns
        widths = {"ID": 50, "Exam": 200, "Question": 400, "Correct Answer": 100, "Marks": 100}
        for col, width in widths.items():
            self.question_tree.heading(col, text=col)
            self.question_tree.column(col, width=width)
        
        self.question_tree.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical',
                                command=self.question_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.question_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate questions
        self.populate_questions()



    def populate_questions(self):
        # Clear existing items
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
            
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT q.id, e.title, q.question, q.correct_answer, q.marks
                FROM questions q
                JOIN exams e ON q.exam_id = e.id
                JOIN teachers t ON e.subject_id = t.subject_id
                WHERE t.id = ?
            """, (self.user_info['id'],))
            
            for row in cursor.fetchall():
                self.question_tree.insert("", 'end', values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            conn.close()


    def show_add_question_frame(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Add New Question", style="Title.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Get available exams
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.title
            FROM exams e
            JOIN teachers t ON e.subject_id = t.subject_id
            WHERE t.id = ?
        """, (self.user_info['id'],))
        exams = cursor.fetchall()
        conn.close()
        
        # Select Exam
        ttk.Label(form_frame, text="Select Exam:", style="Text.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        exam_var = tk.StringVar()
        exam_combo = ttk.Combobox(form_frame, textvariable=exam_var, state="readonly")
        exam_combo['values'] = [exam[1] for exam in exams]
        exam_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Question
        ttk.Label(form_frame, text="Question:", style="Text.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        question_entry = tk.Text(form_frame, height=4, width=50)
        question_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Options A, B, C, D
        ttk.Label(form_frame, text="Option A:", style="Text.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        option_a_entry = ttk.Entry(form_frame)
        option_a_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option B:", style="Text.TLabel").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        option_b_entry = ttk.Entry(form_frame)
        option_b_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option C:", style="Text.TLabel").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        option_c_entry = ttk.Entry(form_frame)
        option_c_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option D:", style="Text.TLabel").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        option_d_entry = ttk.Entry(form_frame)
        option_d_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
        
        # Correct Answer
        ttk.Label(form_frame, text="Correct Answer:", style="Text.TLabel").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        correct_var = tk.StringVar()
        correct_combo = ttk.Combobox(form_frame, textvariable=correct_var, state="readonly")
        correct_combo['values'] = ['A', 'B', 'C', 'D']
        correct_combo.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        
        def save_question():
            exam_title = exam_var.get()
            question = question_entry.get("1.0", "end-1c")
            option_a = option_a_entry.get()
            option_b = option_b_entry.get()
            option_c = option_c_entry.get()
            option_d = option_d_entry.get()
            correct = correct_var.get()
            
            if not all([exam_title, question, option_a, option_b, option_c, option_d, correct]):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            # Get exam_id from title
            exam_id = next(exam[0] for exam in exams if exam[1] == exam_title)
            
            conn = sqlite3.connect('exam_system.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO questions (exam_id, question, option_a, option_b, option_c, option_d, 
                                        correct_answer, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (exam_id, question, option_a, option_b, option_c, option_d, correct, self.user_info['id']))
                
                conn.commit()
                messagebox.showinfo("Success", "Question added successfully!")
                self.show_questions()
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
            finally:
                conn.close()
        
        ttk.Button(form_frame, text="Save", style="Action.TButton",
                command=save_question).grid(row=7, column=1, padx=5, pady=20, sticky='ew')
                
        back_button = ttk.Button(form_frame, text="Back", style="Action.TButton", 
                                command=self.show_questions)
        back_button.grid(row=8, column=1, padx=5, pady=10, sticky='ew')

    def show_edit_question_frame(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to edit!")
            return

        question_id = self.question_tree.item(selected_item)['values'][0]
        self.clear_content()
        
        ttk.Label(self.content_frame, text="Edit Question", style="Title.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Get available exams
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.title
            FROM exams e
            JOIN teachers t ON e.subject_id = t.subject_id
            WHERE t.id = ?
        """, (self.user_info['id'],))
        exams = cursor.fetchall()
        
        cursor.execute("""
            SELECT exam_id, question, option_a, option_b, option_c, option_d, correct_answer
            FROM questions 
            WHERE id = ?
        """, (question_id,))
        question_data = cursor.fetchone()
        conn.close()
        
        exam_var = tk.StringVar(value=next(exam[1] for exam in exams if exam[0] == question_data[0]))
        question_var = tk.StringVar(value=question_data[1])
        option_a_var = tk.StringVar(value=question_data[2])
        option_b_var = tk.StringVar(value=question_data[3])
        option_c_var = tk.StringVar(value=question_data[4])
        option_d_var = tk.StringVar(value=question_data[5])
        correct_var = tk.StringVar(value=question_data[6])
        
        ttk.Label(form_frame, text="Select Exam:", style="Text.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        exam_combo = ttk.Combobox(form_frame, textvariable=exam_var, state="readonly")
        exam_combo['values'] = [exam[1] for exam in exams]
        exam_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Question:", style="Text.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        question_entry = tk.Text(form_frame, height=4, width=50)
        question_entry.insert(tk.END, question_var.get())
        question_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option A:", style="Text.TLabel").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        option_a_entry = ttk.Entry(form_frame, textvariable=option_a_var)
        option_a_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option B:", style="Text.TLabel").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        option_b_entry = ttk.Entry(form_frame, textvariable=option_b_var)
        option_b_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option C:", style="Text.TLabel").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        option_c_entry = ttk.Entry(form_frame, textvariable=option_c_var)
        option_c_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Option D:", style="Text.TLabel").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        option_d_entry = ttk.Entry(form_frame, textvariable=option_d_var)
        option_d_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Correct Answer:", style="Text.TLabel").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        correct_combo = ttk.Combobox(form_frame, textvariable=correct_var, state="readonly")
        correct_combo['values'] = ['A', 'B', 'C', 'D']
        correct_combo.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        
        def update_question():
            exam_title = exam_var.get()
            question = question_entry.get("1.0", "end-1c")
            option_a = option_a_var.get()
            option_b = option_b_var.get()
            option_c = option_c_var.get()
            option_d = option_d_var.get()
            correct = correct_var.get()
            
            if not all([exam_title, question, option_a, option_b, option_c, option_d, correct]):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            # Get exam_id from title
            exam_id = next(exam[0] for exam in exams if exam[1] == exam_title)
            
            conn = sqlite3.connect('exam_system.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE questions
                    SET exam_id = ?, question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, 
                        correct_answer = ?
                    WHERE id = ?
                """, (exam_id, question, option_a, option_b, option_c, option_d, correct, question_id))
                
                conn.commit()
                messagebox.showinfo("Success", "Question updated successfully!")
                self.show_questions()
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
            finally:
                conn.close()
        
        ttk.Button(form_frame, text="Save Changes", style="Action.TButton",
                command=update_question).grid(row=7, column=1, padx=5, pady=20, sticky='ew')
                
        back_button = ttk.Button(form_frame, text="Back", style="Action.TButton", 
                                command=self.show_questions)
        back_button.grid(row=8, column=1, padx=5, pady=10, sticky='ew')

    def delete_question(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to delete!")
            return

        question_id = self.question_tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?")

        if not confirm:
            return

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            messagebox.showinfo("Success", "Question deleted successfully!")
            self.populate_questions()
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        
        finally:
            conn.close()


    def show_results(self):
        self.clear_content()
        
        # Header
        ttk.Label(self.content_frame, text="View Results", style="Title.TLabel").pack(pady=(0, 20))
        
        # Create Treeview
        columns = ("ID", "Student", "Exam", "Score", "Date")
        self.results_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        
        # Configure columns
        widths = {"ID": 50, "Student": 200, "Exam": 200, "Score": 100, "Date": 150}
        for col, width in widths.items():
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=width)
        
        self.results_tree.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical',
                                command=self.results_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate results
        self.populate_results()

    def populate_results(self):
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT r.id, u.name, e.title, r.score, r.date
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN users u ON s.id = u.id
                JOIN exams e ON r.exam_id = e.id
                JOIN teachers t ON e.subject_id = t.subject_id
                WHERE t.id = ?
            """, (self.user_info['id'],))
            
            for row in cursor.fetchall():
                self.results_tree.insert("", 'end', values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")
        finally:
            conn.close()

    def show_profile(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Teacher Profile", style="Title.TLabel").pack(pady=10)

        profile_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        profile_frame.pack(fill='both', expand=True, padx=20, pady=20)

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.username, u.name, u.email, t.phone, s.subject_name
            FROM users u
            JOIN teachers t ON u.id = t.id
            JOIN subjects s ON t.subject_id= s.id
            WHERE u.id = ?
        """, (self.user_info['id'],))
        profile_data = cursor.fetchone()

        conn.close()

        if not profile_data:
            messagebox.showerror("Error", "Unable to fetch profile information.")
            return

        labels = ["Username", "Name", "Email", "Phone", "Subject"]
        values = list(profile_data)

        for label, value in zip(labels, values):
            row = ttk.Frame(profile_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            ttk.Label(row, text=f"{label}:", style="Text.TLabel").pack(side='left', padx=5)
            ttk.Label(row, text=value or "Not provided", style="Text.TLabel").pack(side='left', padx=5)

        edit_button = ttk.Button(profile_frame, text="Edit Profile", style="Action.TButton", command=lambda: self.show_edit_profile(profile_data))
        edit_button.pack(pady=20)


    def show_edit_profile(self, profile_data):
        self.clear_content()

        ttk.Label(self.content_frame, text="Edit Profile", style="Title.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        labels = ["Username", "Name", "Email", "Phone", "Subject"]
        updated_entries = {}

        for idx, label in enumerate(labels):
            row = ttk.Frame(form_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            ttk.Label(row, text=f"{label}:", style="Text.TLabel").pack(side='left', padx=5)
            entry_var = tk.StringVar(value=profile_data[idx])
            if label == "Subject":
                entry = ttk.Entry(row, textvariable=entry_var, style="Content.TEntry", state="readonly")
            else:
                entry = ttk.Entry(row, textvariable=entry_var, style="Content.TEntry")
            entry.pack(side='left', fill='x', expand=True, padx=5)
            updated_entries[label] = entry_var

        def save_profile():
            username = updated_entries["Username"].get()
            name = updated_entries["Name"].get()
            email = updated_entries["Email"].get()
            phone = updated_entries["Phone"].get()

            if not all([username, name, email, phone]):
                messagebox.showerror("Error", "All fields are required!")
                return

            conn = sqlite3.connect('exam_system.db')
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    UPDATE users
                    SET username = ?, name = ?, email = ?
                    WHERE id = ?
                """, (username, name, email, self.user_info['id']))

                cursor.execute("""
                    UPDATE teachers
                    SET phone = ?
                    WHERE id = ?
                """, (phone, self.user_info['id']))

                conn.commit()
                messagebox.showinfo("Success", "Profile updated successfully!")
                self.show_profile()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
            
            finally:
                conn.close()

        save_button = ttk.Button(form_frame, text="Save Changes", style="Action.TButton", command=save_profile)
        save_button.pack(pady=20)

        back_button = ttk.Button(form_frame, text="Back", style="Action.TButton", command=self.show_profile)
        back_button.pack(pady=10)

    # Database helper methods
    def populate_results_tree(self, tree):
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT r.id, u.name, e.title, r.score, r.date
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN exams e ON r.exam_id = e.id
                JOIN users u ON s.id = u.id
                WHERE e.subject = ?
            """, (self.user_info['subject'],))
            
            for row in cursor.fetchall():
                tree.insert("", 'end', values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Create new main window and show login screen
            root = tk.Tk()
            from main import UserTypeSelection
            UserTypeSelection(root)
            root.mainloop()

def connect_db():
    return sqlite3.connect('exam_system.db')
