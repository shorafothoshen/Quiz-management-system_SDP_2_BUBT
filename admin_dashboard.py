import tkinter as tk
from tkinter import ttk, messagebox,simpledialog
import sqlite3
from datetime import datetime
from tkinter import StringVar


class AdminDashboard:
    def __init__(self, root, admin_info, login_window):
        self.root = root
        self.adminInfo = admin_info
        self.login_window = login_window
        self.root.title("Admin Dashboard")
        
        # Configure the window
        self.root.state('zoomed')  # Maximize window
        
        # Configure colors
        self.colors = {
            'bg_dark': '#0A192F',      # Dark navy background
            'sidebar': '#112240',       # Slightly lighter navy for sidebar
            'content': '#1A2744',       # Content area background
            'accent1': '#64FFDA',       # Teal accent
            'accent2': '#8892B0',       # Muted blue-gray
            'text': '#E6F1FF',          # Light blue-white text
            'text_secondary': '#8892B0', # Secondary text color
            'hover': '#233554'          # Hover state color
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure widget styles
        self.style.configure("Sidebar.TFrame", background=self.colors['sidebar'])
        self.style.configure("Content.TFrame", background=self.colors['content'])
        self.style.configure("NavButton.TButton",
                           background=self.colors['sidebar'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11),
                           borderwidth=0,
                           padding=20)
        self.style.map("NavButton.TButton",
                      background=[('active', self.colors['hover'])],
                      foreground=[('active', self.colors['accent1'])])
                      
        # Configure Treeview style
        self.style.configure("Treeview",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['content'],
                           borderwidth=0)
        self.style.configure("Treeview.Heading",
                           background=self.colors['sidebar'],
                           foreground=self.colors['text'],
                           borderwidth=0)
        
        # Main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill='both', expand=True)
        
        # Create sidebar
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Dashboard title in sidebar
        title_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        title_frame.pack(fill='x', pady=20)
        ttk.Label(title_frame, 
                 text="Admin Dashboard",
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colors['text'],
                 background=self.colors['sidebar']).pack(pady=10)
        
        # Navigation buttons
        self.create_nav_button("👥 Manage Students", self.show_students_page)
        self.create_nav_button("👥 Manage Teacher", self.show_students_page)
        self.create_nav_button("📝 Manage Exams", self.show_exams_page)
        self.create_nav_button("❓ Manage Questions", self.show_questions_page)
        self.create_nav_button("📊 View Results", self.show_results_page)
        
        # Logout button at bottom of sidebar
        ttk.Button(self.sidebar,
                  text="🚪 Logout",
                  style="NavButton.TButton",
                  command=self.logout).pack(side='bottom', fill='x', pady=10)
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(side='left', fill='both', expand=True)
        
        # Initialize with students page
        self.current_page = None
        self.show_students_page()
    
    def create_nav_button(self, text, command):
        btn = ttk.Button(self.sidebar,
                        text=text,
                        style="NavButton.TButton",
                        command=command)
        btn.pack(fill='x', pady=2)
        return btn
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_students_page(self):
        if self.current_page == "students":
            return
        self.current_page = "students"
        self.clear_content()

        # Create students page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Manage Students",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Student list
        self.student_tree = ttk.Treeview(page_frame,
                                        columns=("ID", "Username", "Name", "Class"),
                                        show="headings",
                                        style="Treeview")
        self.student_tree.heading("ID", text="ID")
        self.student_tree.heading("Username", text="Username")
        self.student_tree.heading("Name", text="Name")
        self.student_tree.heading("Class", text="Class")
        self.student_tree.pack(pady=10, expand=True, fill='both')

        # Add buttons for Edit and Delete
        button_frame = ttk.Frame(page_frame)
        button_frame.pack(pady=20)

        edit_button = ttk.Button(button_frame, text="Edit Student", command=self.edit_student)
        edit_button.pack(side='left', padx=10)

        delete_button = ttk.Button(button_frame, text="Delete Student", command=self.delete_student)
        delete_button.pack(side='left', padx=10)

        self.refresh_student_list()


    def refresh_student_list(self):
        # Clear existing data
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        # Fetch students from the database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.username, u.name, s.class
            FROM users u
            JOIN students s ON u.id = s.id
            WHERE u.role = 'Student'
        ''')

        students = cursor.fetchall()

        for student in students:
            self.student_tree.insert("", "end", values=student)

        conn.close()


    def edit_student(self):
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to edit!")
            return

        student_id = self.student_tree.item(selected_item, "values")[0]
        self.show_edit_student_page(student_id)


    def show_edit_student_page(self, student_id):
        # Clear existing content
        self.clear_content()
        self.current_page = "edit_student"

        # Fetch student details
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.name, u.email, s.class
            FROM users u
            JOIN students s ON u.id = s.id
            WHERE u.id = ?
        ''', (student_id,))
        student_data = cursor.fetchone()
        conn.close()

        if not student_data:
            messagebox.showerror("Error", "Student not found!")
            return

        # Extract current details
        current_name, current_email, current_class = student_data

        # Create Edit Frame
        edit_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        edit_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ttk.Label(edit_frame,
                text="Edit Student Details",
                font=("Segoe UI", 24, "bold"),
                foreground=self.colors['text']).pack(pady=(0, 20))

        # Input fields
        ttk.Label(edit_frame, text="Name:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        name_var = StringVar(value=current_name)
        name_entry = ttk.Entry(edit_frame, textvariable=name_var, width=40)
        name_entry.pack(pady=(0, 10))

        ttk.Label(edit_frame, text="Email:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        email_var = StringVar(value=current_email)
        email_entry = ttk.Entry(edit_frame, textvariable=email_var, width=40)
        email_entry.pack(pady=(0, 10))

        ttk.Label(edit_frame, text="Class:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        class_var = StringVar(value=current_class)
        class_entry = ttk.Entry(edit_frame, textvariable=class_var, width=40)
        class_entry.pack(pady=(0, 10))

        # Save Button
        save_button = ttk.Button(edit_frame, text="Save", 
                                command=lambda: self.save_student_data(student_id, name_var, email_var, class_var))
        save_button.pack(pady=20)

        # Back Button
        back_button = ttk.Button(edit_frame, text="Back", command=self.show_students_page)
        back_button.pack(pady=10)

    def save_student_data(self, student_id, name_var, email_var, class_var):
        new_name = name_var.get().strip()
        new_email = email_var.get().strip()
        new_class = class_var.get().strip()

        # Validation
        if not new_name or not new_email or not new_class:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Update data in database
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE users
                SET name = ?, email = ?
                WHERE id = ?
            ''', (new_name, new_email, student_id))

            cursor.execute('''
                UPDATE students
                SET class = ?
                WHERE id = ?
            ''', (new_class, student_id))

            conn.commit()
            messagebox.showinfo("Success", "Student data updated successfully!")
            
            # Return to the student list page
            self.show_students_page()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()


    def delete_student(self):
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a student to delete.")
            return

        student_id = self.student_tree.item(selected_item)["values"][0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?")
        if confirm:
            conn = sqlite3.connect('exam_system.db')
            cursor = conn.cursor()

            # Delete the student from students table and associated user
            cursor.execute('''
                DELETE FROM students WHERE id = ?
            ''', (student_id,))

            cursor.execute('''
                DELETE FROM users WHERE id = ?
            ''', (student_id,))

            conn.commit()
            conn.close()

            self.refresh_student_list()
            messagebox.showinfo("Success", "Student deleted successfully.")
    
    def show_exams_page(self):
        if self.current_page == "exams":
            return
            
        self.clear_content()
        self.current_page = "exams"
        
        # Create exam form
        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(pady=20, padx=20)
        
        # Title
        ttk.Label(form_frame,
                 text="Create New Exam",
                 style="Title.TLabel").pack(anchor='w', pady=(0, 20))
        
        # Exam details frame
        details_frame = ttk.Frame(form_frame, style="Card.TFrame")
        details_frame.pack(fill='x', padx=20, pady=10)
        
        # Title field
        title_frame = ttk.Frame(details_frame, style="Card.TFrame")
        title_frame.pack(fill='x', pady=10)
        ttk.Label(title_frame,
                 text="Exam Title:",
                 style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.exam_title = ttk.Entry(title_frame, width=40)
        self.exam_title.pack(side='left', fill='x', expand=True)
        
        # Subject field
        subject_frame = ttk.Frame(details_frame, style="Card.TFrame")
        subject_frame.pack(fill='x', pady=10)
        ttk.Label(subject_frame,
                 text="Subject:",
                 style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.exam_subject = ttk.Entry(subject_frame, width=40)
        self.exam_subject.pack(side='left', fill='x', expand=True)
        
        # Duration field
        duration_frame = ttk.Frame(details_frame, style="Card.TFrame")
        duration_frame.pack(fill='x', pady=10)
        ttk.Label(duration_frame,
                 text="Duration (minutes):",
                 style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.exam_duration = ttk.Entry(duration_frame, width=10)
        self.exam_duration.pack(side='left')
        
        # Create button
        ttk.Button(details_frame,
                  text="Create Exam",
                  style="Custom.TButton",
                  command=self.create_exam).pack(pady=20)
                  
        # Exam list section
        list_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(list_frame,
                 text="Existing Exams",
                 style="Title.TLabel").pack(anchor='w', pady=(0, 20))
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(list_frame, style="Content.TFrame")
        tree_frame.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create treeview
        self.exam_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Title", "Subject", "Duration", "Created By"),
            show="headings",
            style="Treeview"
        )
        self.exam_tree.pack(fill='both', expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.exam_tree.yview)
        self.exam_tree.config(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.exam_tree.heading("ID", text="ID")
        self.exam_tree.heading("Title", text="Title")
        self.exam_tree.heading("Subject", text="Subject")
        self.exam_tree.heading("Duration", text="Duration (min)")
        self.exam_tree.heading("Created By", text="Created By")
        
        # Column widths
        self.exam_tree.column("ID", width=50)
        self.exam_tree.column("Title", width=200)
        self.exam_tree.column("Subject", width=150)
        self.exam_tree.column("Duration", width=100)
        self.exam_tree.column("Created By", width=150)
        
        # Load exams
        self.refresh_exam_list()
    
    def show_questions_page(self):
        if self.current_page == "questions":
            return
            
        self.clear_content()
        self.current_page = "questions"
        
        # Create questions page
        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(pady=20, padx=20)
        
        # Title
        ttk.Label(form_frame,
                 text="Add New Question",
                 style="Title.TLabel").pack(anchor='w', pady=(0, 20))
        
        # Question form
        details_frame = ttk.Frame(form_frame, style="Card.TFrame")
        details_frame.pack(fill='x', padx=20, pady=10)
        
        # Exam selection
        exam_frame = ttk.Frame(details_frame, style="Card.TFrame")
        exam_frame.pack(fill='x', pady=10)
        ttk.Label(exam_frame,
                 text="Select Exam:",
                 style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.exam_var = tk.StringVar()
        self.exam_dropdown = ttk.Combobox(exam_frame,
                                        textvariable=self.exam_var,
                                        state='readonly',
                                        width=40)
        self.exam_dropdown.pack(side='left', fill='x', expand=True)
        self.refresh_exam_dropdown()
        
        # Question text
        question_frame = ttk.Frame(details_frame, style="Card.TFrame")
        question_frame.pack(fill='x', pady=10)
        ttk.Label(question_frame,
                 text="Question:",
                 style="Card.TLabel").pack(anchor='w', padx=(0, 10))
        self.question_text = tk.Text(question_frame, height=3, width=50)
        self.question_text.pack(fill='x', pady=5)
        
        # Options
        options_frame = ttk.Frame(details_frame, style="Card.TFrame")
        options_frame.pack(fill='x', pady=10)
        
        self.option_entries = []
        option_labels = ['A', 'B', 'C', 'D']
        
        for i, label in enumerate(option_labels):
            option_frame = ttk.Frame(options_frame, style="Card.TFrame")
            option_frame.pack(fill='x', pady=5)
            ttk.Label(option_frame,
                     text=f"Option {label}:",
                     style="Card.TLabel").pack(side='left', padx=(0, 10))
            entry = ttk.Entry(option_frame, width=50)
            entry.pack(side='left', fill='x', expand=True)
            self.option_entries.append(entry)
        
        # Correct answer
        answer_frame = ttk.Frame(details_frame, style="Card.TFrame")
        answer_frame.pack(fill='x', pady=10)
        ttk.Label(answer_frame,
                 text="Correct Answer:",
                 style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.correct_var = tk.StringVar()
        for i, label in enumerate(option_labels):
            ttk.Radiobutton(answer_frame,
                          text=label,
                          variable=self.correct_var,
                          value=str(i+1),
                          style="Custom.TRadiobutton").pack(side='left', padx=10)
        
        # Add button
        ttk.Button(details_frame,
                  text="Add Question",
                  style="Custom.TButton",
                  command=self.add_question).pack(pady=20)
        
        # Questions list
        list_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(list_frame,
                 text="Existing Questions",
                 style="Title.TLabel").pack(anchor='w', pady=(0, 20))
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(list_frame, style="Content.TFrame")
        tree_frame.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create treeview
        self.question_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Exam", "Question", "Correct"),
            show="headings",
            style="Treeview"
        )
        self.question_tree.pack(fill='both', expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.question_tree.yview)
        self.question_tree.config(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.question_tree.heading("ID", text="ID")
        self.question_tree.heading("Exam", text="Exam")
        self.question_tree.heading("Question", text="Question")
        self.question_tree.heading("Correct", text="Correct Answer")
        
        # Column widths
        self.question_tree.column("ID", width=50)
        self.question_tree.column("Exam", width=200)
        self.question_tree.column("Question", width=400)
        self.question_tree.column("Correct", width=100)
        
        # Load questions
        self.refresh_question_list()
        
    def show_results_page(self):
        if self.current_page == "results":
            return
            
        self.clear_content()
        self.current_page = "results"
        
        # Results page
        results_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(results_frame,
                 text="Exam Results",
                 style="Title.TLabel").pack(anchor='w', pady=(0, 20))
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(results_frame, style="Content.TFrame")
        tree_frame.pack(fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Create treeview
        self.results_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Student", "Exam", "Score", "Date"),
            show="headings",
            style="Treeview"
        )
        self.results_tree.pack(fill='both', expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.results_tree.yview)
        self.results_tree.config(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.results_tree.heading("ID", text="ID")
        self.results_tree.heading("Student", text="Student")
        self.results_tree.heading("Exam", text="Exam")
        self.results_tree.heading("Score", text="Score (%)")
        self.results_tree.heading("Date", text="Date")
        
        # Column widths
        self.results_tree.column("ID", width=50)
        self.results_tree.column("Student", width=200)
        self.results_tree.column("Exam", width=200)
        self.results_tree.column("Score", width=100)
        self.results_tree.column("Date", width=150)
        
        # Load results
        self.refresh_results_list()
        

    def create_exam(self):
        title = self.exam_title.get().strip()
        subject = self.exam_subject.get().strip()
        duration = self.exam_duration.get().strip()
        
        if not title or not subject or not duration:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            duration = int(duration)
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return

        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO exams (title, subject, duration, created_by)
                VALUES (?, ?, ?, ?)
            """, (title, subject, duration, self.admin_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Exam created successfully")
            self.refresh_exam_list()
            self.refresh_exam_dropdown()

            # Clear fields
            self.exam_title.delete(0, tk.END)
            self.exam_subject.delete(0, tk.END)
            self.exam_duration.delete(0, tk.END)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            if conn:
                conn.close()


    def refresh_exam_dropdown(self):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM exams")
        exams = cursor.fetchall()
        conn.close()

        self.exam_dropdown['values'] = [f"{exam[0]} - {exam[1]}" for exam in exams]

    def logout(self):
        self.root.destroy()
        self.login_window.deiconify()
        
    def add_question(self):
        exam_id = self.exam_var.get().split(':')[0]
        question = self.question_text.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in self.option_entries]
        correct = self.correct_var.get()
        
        if not exam_id or not question or not all(options) or not correct:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO questions (exam_id, question, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (exam_id, question, options[0], options[1], options[2], options[3], correct))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Question added successfully")
            
            # Clear fields
            self.question_text.delete("1.0", tk.END)
            for entry in self.option_entries:
                entry.delete(0, tk.END)
            self.correct_var.set("")
            
            # Refresh list
            self.refresh_question_list()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            if conn:
                conn.close()
                
    def refresh_question_list(self):
        # Clear existing items
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
            
        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT q.id, e.title, q.question, q.correct_answer
                FROM questions q
                JOIN exams e ON q.exam_id = e.id
                ORDER BY q.id DESC
            """)
            
            questions = cursor.fetchall()
            
            for question in questions:
                self.question_tree.insert("", "end", values=question)
                
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while refreshing question list: {str(e)}")
            if conn:
                conn.close()
                
    def refresh_results_list(self):
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, s.name, e.title, r.score, r.date
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN exams e ON r.exam_id = e.id
                ORDER BY r.date DESC
            """)
            
            results = cursor.fetchall()
            
            for result in results:
                # Format the score to 2 decimal places
                result = list(result)
                result[3] = f"{float(result[3]):.2f}"
                self.results_tree.insert("", "end", values=result)
                
            conn.close()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while refreshing results list: {str(e)}")
            if conn:
                conn.close()