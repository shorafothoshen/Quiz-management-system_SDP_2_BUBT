import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from hashlib import sha256
from time import time

# Function to connect to the database
def connect_db():
    return sqlite3.connect('exam_system.db')

class TeacherDashboard:
    def __init__(self, root, user_info):
        self.root = root
        self.user_info = user_info
        self.root.title("Teacher Dashboard")
        
        # Configure the window
        self.root.state('zoomed')  # Maximize window

        # Configure colors
        self.colors = {
            'bg_dark': '#0A192F',
            'sidebar': '#112240',
            'content': '#1A2744',
            'accent1': '#64FFDA',
            'accent2': '#8892B0',
            'text': '#E6F1FF',
            'text_secondary': '#8892B0',
            'hover': '#233554'
        }

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("Content.TFrame", background=self.colors['content'])
        self.style.configure("Sidebar.TFrame", background=self.colors['sidebar'])
        self.style.configure("Title.TLabel", background=self.colors['content'], foreground=self.colors['text'], font=('Segoe UI', 24, 'bold'))
        self.style.configure("Subtitle.TLabel", background=self.colors['content'], foreground=self.colors['text_secondary'], font=('Segoe UI', 18))
        self.style.configure("Text.TLabel", background=self.colors['content'], foreground=self.colors['text'], font=('Segoe UI', 12))
        self.style.configure("Custom.TButton", background=self.colors['accent1'], foreground=self.colors['bg_dark'], font=('Segoe UI', 11), relief="flat", borderwidth=0, padding=(10, 5))
        self.style.map("Custom.TButton", background=[('active', self.colors['hover'])], foreground=[('active', self.colors['bg_dark'])])
        self.style.configure("Treeview", background=self.colors['content'], foreground=self.colors['text'], fieldbackground=self.colors['content'], font=('Segoe UI', 12))
        self.style.map("Treeview", background=[('selected', self.colors['hover'])], foreground=[('selected', self.colors['text'])])
        self.style.configure("Treeview.Heading", background=self.colors['sidebar'], foreground=self.colors['text'], font=('Segoe UI', 12, 'bold'))

        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame")
        self.sidebar.pack(side='left', fill='y')

        # Sidebar buttons
        ttk.Button(self.sidebar, text="Show Results", style="Custom.TButton", command=self.show_results).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Manage Exams", style="Custom.TButton", command=self.show_exams).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Manage Questions", style="Custom.TButton", command=self.show_questions).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Profile", style="Custom.TButton", command=self.show_profile).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Logout", style="Custom.TButton", command=self.logout).pack(fill='x', pady=(20, 0))

        # Header section
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(20, 20))

        ttk.Label(header_frame, text="Teacher Dashboard", style="Title.TLabel").pack(anchor='center')

        # Content frame
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(fill='both', expand=True)

        self.show_results()
    def show_results(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Student Results", style="Subtitle.TLabel").pack(pady=10)

        self.tree = ttk.Treeview(self.content_frame, columns=("ID", "Student", "Exam", "Score", "Date"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Student", text="Student")
        self.tree.heading("Exam", text="Exam")
        self.tree.heading("Score", text="Score")
        self.tree.heading("Date", text="Date")

        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        self.populate_results_tree()

    def populate_results_tree(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.id, u.name, e.title, r.score, r.date
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN exams e ON r.exam_id = e.id
            JOIN users u ON s.id = u.id
            WHERE e.subject = ? AND u.id = ? AND u.role = 'Student'
        """, (self.user_info['subject'], self.user_info['id']))
        
        results = cursor.fetchall()

        for result in results:
            self.tree.insert("", 'end', values=result)

        conn.close()


    def show_exams(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Manage Exams", style="Subtitle.TLabel").pack(pady=10)

        self.tree = ttk.Treeview(self.content_frame, columns=("ID", "Title", "Subject", "Duration"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Duration", text="Duration")

        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        # Add buttons for Add, Edit, and Delete
        button_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text="Add Exam", command=self.add_exam)
        add_button.pack(side='left', padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Exam", command=self.edit_exam)
        edit_button.pack(side='left', padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Exam", command=self.delete_exam)
        delete_button.pack(side='left', padx=5)

        self.populate_exams_tree()

    def populate_exams_tree(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, subject, duration FROM exams WHERE subject = ?", (self.user_info['subject'],))
        exams = cursor.fetchall()

        for exam in exams:
            self.tree.insert("", 'end', values=exam)

        conn.close()

    def show_questions(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Manage Questions", style="Subtitle.TLabel").pack(pady=10)

        self.tree = ttk.Treeview(self.content_frame, columns=("ID", "Question", "Subject", "Option A", "Option B", "Option C", "Option D", "Correct Answer"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Question", text="Question")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Option A", text="Option A")
        self.tree.heading("Option B", text="Option B")
        self.tree.heading("Option C", text="Option C")
        self.tree.heading("Option D", text="Option D")
        self.tree.heading("Correct Answer", text="Correct Answer")

        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        # Add buttons for Add, Edit, and Delete
        button_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text="Add Question", command=self.add_question)
        add_button.pack(side='left', padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Question", command=self.edit_question)
        edit_button.pack(side='left', padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Question", command=self.delete_question)
        delete_button.pack(side='left', padx=5)

        self.populate_questions_tree()

    def populate_questions_tree(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT q.id, q.question, e.subject, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_answer 
            FROM questions q
            JOIN exams e ON q.exam_id = e.id
            WHERE e.subject = ?
        """, (self.user_info['subject'],))
        
        questions = cursor.fetchall()

        for question in questions:
            self.tree.insert("", 'end', values=question)

        conn.close()

    def show_profile(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Profile Information", style="Subtitle.TLabel").pack(pady=10)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT username, name, email, role FROM users WHERE username = ?", (self.user_info['username'],))
        profile_info = cursor.fetchone()

        profile_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        profile_frame.pack(fill='both', expand=True, padx=20, pady=20)

        if profile_info:
            fields = ["Username", "Name", "Email", "Role"]
            for i, field in enumerate(fields):
                ttk.Label(profile_frame, text=f"{field}:", style="Text.TLabel").grid(row=i, column=0, padx=10, pady=10, sticky='e')
                ttk.Label(profile_frame, text=profile_info[i], style="Text.TLabel").grid(row=i, column=1, padx=10, pady=10, sticky='w')

        conn.close()

    def add_question(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Add New Question", style="Subtitle.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        fields = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
        entries = {}

        for field in fields:
            row = ttk.Frame(form_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            label = ttk.Label(row, text=f"{field}:", style="Text.TLabel")
            label.pack(side='left', padx=5)

            entry = ttk.Entry(row, style="Content.TEntry")
            entry.pack(side='left', fill='x', expand=True, padx=5)
            entries[field] = entry

        exam_id_entry = ttk.Entry(form_frame, style="Content.TEntry")
        exam_id_entry.pack(pady=10)

        submit_button = ttk.Button(form_frame, text="Add Question", style="Custom.TButton", command=lambda: self.submit_question(entries, exam_id_entry.get()))
        submit_button.pack(pady=20)

    def submit_question(self, entries, exam_id):
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO questions (exam_id, question, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (exam_id, entries["Question"].get(), entries["Option A"].get(), entries["Option B"].get(), entries["Option C"].get(), entries["Option D"].get(), entries["Correct Answer"].get()))

            conn.commit()
            messagebox.showinfo("Success", "Question added successfully!")
            self.show_questions()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        finally:
            conn.close()

    def edit_question(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to edit!")
            return

        question_id = self.tree.item(selected_item, 'values')[0]
        self.show_edit_question_page(question_id)

    def show_edit_question_page(self, question_id):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Edit Question", style="Subtitle.TLabel").pack(pady=10)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT question, option_a, option_b, option_c, option_d, correct_answer FROM questions WHERE id = ?", (question_id,))
        question_data = cursor.fetchone()
        conn.close()

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        fields = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]
        entries = {}

        for i, field in enumerate(fields):
            row = ttk.Frame(form_frame, style="Content.TFrame")
            row.pack(fill='x', pady=5)

            label = ttk.Label(row, text=f"{field}:", style="Text.TLabel")
            label.pack(side='left', padx=5)

            entry = ttk.Entry(row, style="Content.TEntry")
            entry.insert(0, question_data[i])
            entry.pack(side='left', fill='x', expand=True, padx=5)
            entries[field] = entry

        submit_button = ttk.Button(form_frame, text="Save Changes", style="Custom.TButton", command=lambda: self.update_question(entries, question_id))
        submit_button.pack(pady=20)

    def update_question(self, entries, question_id):
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE questions
                SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?
                WHERE id = ?
            """, (entries["Question"].get(), entries["Option A"].get(), entries["Option B"].get(), entries["Option C"].get(), entries["Option D"].get(), entries["Correct Answer"].get(), question_id))

            conn.commit()
            messagebox.showinfo("Success", "Question updated successfully!")
            self.show_questions()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        finally:
            conn.close()

    def delete_question(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to delete!")
            return

        question_id = self.tree.item(selected_item, 'values')[0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?")
        if not confirm:
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            messagebox.showinfo("Success", "Question deleted successfully!")
            self.show_questions()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        finally:
            conn.close()

    def logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Create new main window
            root = tk.Tk()
            from main import UserTypeSelection
            UserTypeSelection(root)
            root.mainloop()
