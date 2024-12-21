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
        ttk.Button(self.sidebar, text="Add Question", style="Custom.TButton", command=self.add_question_view).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Update Question", style="Custom.TButton", command=self.update_question_view).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Delete Question", style="Custom.TButton", command=self.delete_question_view).pack(fill='x', pady=(20, 0))
        ttk.Button(self.sidebar, text="Logout", style="Custom.TButton", command=self.logout).pack(fill='x', pady=(20, 0))

        # Header section
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(20, 20))

        ttk.Label(header_frame, text="Teacher Dashboard", style="Title.TLabel").pack(anchor='center')

        # Content frame
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(fill='both', expand=True)

        self.show_questions()

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

        self.populate_tree()

    def populate_tree(self):
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, question, (SELECT subject FROM exams WHERE id = questions.exam_id), option_a, option_b, option_c, option_d, correct_answer FROM questions WHERE created_by = (SELECT id FROM users WHERE username = ?)", (self.user_info['username'],))
        questions = cursor.fetchall()

        for question in questions:
            self.tree.insert("", 'end', values=question)

        conn.close()

    def add_question_view(self):
        self.show_questions()

        def add_question():
            question = question_entry.get()
            subject = subject_entry.get()
            option_a = option_a_entry.get()
            option_b = option_b_entry.get()
            option_c = option_c_entry.get()
            option_d = option_d_entry.get()
            correct_answer = correct_answer_entry.get()

            if not all([question, subject, option_a, option_b, option_c, option_d, correct_answer]):
                messagebox.showerror("Error", "Please fill all fields")
                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM exams WHERE subject = ?", (subject,))
            exam = cursor.fetchone()
            if not exam:
                messagebox.showerror("Error", "Subject not found")
                conn.close()
                return

            exam_id = exam[0]

            cursor.execute("INSERT INTO questions (exam_id, question, option_a, option_b, option_c, option_d, correct_answer, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, (SELECT id FROM users WHERE username = ?))",
                           (exam_id, question, option_a, option_b, option_c, option_d, correct_answer, self.user_info['username']))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Question added successfully")
            self.show_questions()

        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Add Question", style="Subtitle.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Question:", style="Text.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        question_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        question_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Subject:", style="Text.TLabel").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        subject_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        subject_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Option A:", style="Text.TLabel").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        option_a_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_a_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Option B:", style="Text.TLabel").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        option_b_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_b_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Option C:", style="Text.TLabel").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        option_c_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_c_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Option D:", style="Text.TLabel").grid(row=5, column=0, padx=10, pady=10, sticky='w')
        option_d_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_d_entry.grid(row=5, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text="Correct Answer:", style="Text.TLabel").grid(row=6, column=0, padx=10, pady=10, sticky='w')
        correct_answer_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        correct_answer_entry.grid(row=6, column=1, padx=10, pady=10)

        ttk.Button(form_frame, text="Add Question", style="Custom.TButton", command=add_question).grid(row=7, columnspan=2, pady=20)

    def update_question_view(self):
        self.show_questions()

        def update_question():
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a question to update")
                return

            question = question_entry.get()
            option_a = option_a_entry.get()
            option_b = option_b_entry.get()
            option_c = option_c_entry.get()
            option_d = option_d_entry.get()
            correct_answer = correct_answer_entry.get()

            if not all([question, option_a, option_b, option_c, option_d, correct_answer]):
                messagebox.showerror("Error", "Please fill all fields")
                return

            conn = connect_db()
            cursor = conn.cursor()

            item = self.tree.item(selected_item)
            question_id = item['values'][0]

            cursor.execute("UPDATE questions SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ? WHERE id = ?",
                           (question, option_a, option_b, option_c, option_d, correct_answer, question_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Question updated successfully")
            self.show_questions()

        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to update")
            return

        item = self.tree.item(selected_item)
        question_values = item['values']

        ttk.Label(self.content_frame, text="Update Question", style="Subtitle.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Question:", style="Text.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        question_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        question_entry.grid(row=0, column=1, padx=10, pady=10)
        question_entry.insert(0, question_values[1])

        ttk.Label(form_frame, text="Option A:", style="Text.TLabel").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        option_a_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_a_entry.grid(row=1, column=1, padx=10, pady=10)
        option_a_entry.insert(0, question_values[3])

        ttk.Label(form_frame, text="Option B:", style="Text.TLabel").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        option_b_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_b_entry.grid(row=2, column=1, padx=10, pady=10)
        option_b_entry.insert(0, question_values[4])

        ttk.Label(form_frame, text="Option C:", style="Text.TLabel").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        option_c_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_c_entry.grid(row=3, column=1, padx=10, pady=10)
        option_c_entry.insert(0, question_values[5])

        ttk.Label(form_frame, text="Option D:", style="Text.TLabel").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        option_d_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        option_d_entry.grid(row=4, column=1, padx=10, pady=10)
        option_d_entry.insert(0, question_values[6])

        ttk.Label(form_frame, text="Correct Answer:", style="Text.TLabel").grid(row=5, column=0, padx=10, pady=10, sticky='w')
        correct_answer_entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
        correct_answer_entry.grid(row=5, column=1, padx=10, pady=10)
        correct_answer_entry.insert(0, question_values[7])

        ttk.Button(form_frame, text="Update Question", style="Custom.TButton", command=update_question).grid(row=6, columnspan=2, pady=20)

    def delete_question_view(self):
        self.show_questions()

        def delete_question():
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a question to delete")
                return

            conn = connect_db()
            cursor = conn.cursor()

            item = self.tree.item(selected_item)
            question_id = item['values'][0]

            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Question deleted successfully")
            self.show_questions()

        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Delete Question", style="Subtitle.TLabel").pack(pady=10)

        delete_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        delete_frame.pack(pady=20)

        ttk.Button(delete_frame, text="Delete Selected Question", style="Custom.TButton", command=delete_question).pack(pady=20)

    def logout(self):
        self.main_container.destroy()
        UserTypeSelection(self.root)


# Example user info for testing
user_info = {
    "username": "teacher1",
    "role": "Teacher"
}

# Function to run the application
def run_app():
    root = tk.Tk()
    root.configure(bg='#0A192F')  # Set root window background to dark

    app = TeacherDashboard(root, user_info)
    root.mainloop()

if __name__ == "__main__":
    run_app()
