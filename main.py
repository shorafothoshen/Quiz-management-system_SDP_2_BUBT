import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from admin_dashboard import AdminDashboard
from student_dashboard import StudentDashboard
from database import create_database
from datetime import datetime
from hashlib import sha256
from time import time

class UserTypeSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Portal")
        self.failed_attempts = 0
        self.lock_time = None
        
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
        
        # Configure widget styles
        self.style.configure("Content.TFrame", background=self.colors['content'])
        self.style.configure("Card.TFrame",
                             background=self.colors['sidebar'],
                             relief="flat",
                             borderwidth=0,
                             padding=20)
        self.style.configure("Title.TLabel",
                             background=self.colors['content'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 24, 'bold'))
        self.style.configure("Subtitle.TLabel",
                             background=self.colors['content'],
                             foreground=self.colors['text_secondary'],
                             font=('Segoe UI', 18))
        self.style.configure("Card.TLabel",
                             background=self.colors['sidebar'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 12))
        self.style.configure("Custom.TButton",
                             background=self.colors['accent1'],
                             foreground=self.colors['bg_dark'],
                             font=('Segoe UI', 11),
                             relief="flat",
                             borderwidth=0,
                             padding=(10, 5))
        self.style.map("Custom.TButton",
                       background=[('active', self.colors['hover'])],
                       foreground=[('active', self.colors['bg_dark'])])
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)
        
        # Header section
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(50, 30))
        
        ttk.Label(header_frame,
                  text="Welcome to Examination System",
                  style="Title.TLabel").pack(anchor='center')
        
        ttk.Label(header_frame,
                  text="Login to continue",
                  style="Subtitle.TLabel").pack(anchor='center', pady=10)
        
        # Centered User Login Card
        user_card = ttk.Frame(self.main_container, style="Card.TFrame")
        user_card.pack(pady=20, padx=150, ipadx=75, ipady=40)
        
        # Username Field
        ttk.Label(user_card, text="Username:", style="Card.TLabel").pack(pady=(10, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(user_card, textvariable=self.username_var, font=('Segoe UI', 12))
        self.username_entry.pack(pady=5)
        
        # Password Field
        ttk.Label(user_card, text="Password:", style="Card.TLabel").pack(pady=(10, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(user_card, textvariable=self.password_var, show='*', font=('Segoe UI', 12))
        self.password_entry.pack(pady=5)
        
       # Login Button
        ttk.Button(user_card, text="Login", style="Custom.TButton", command=self.verify_login).pack(pady=(10, 5))
        
        # Register Button
        ttk.Button(user_card, text="Register", style="Custom.TButton", command=self.show_student_register).pack(pady=(5, 10))

    def show_student_register(self):
        self.main_container.destroy()
        StudentRegistration(self.root)
    
    def verify_login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        # Check if user is locked out
        if self.lock_time and time() < self.lock_time:
            remaining_time = int(self.lock_time - time())
            messagebox.showerror("Locked", f"Too many failed attempts. Try again in {remaining_time} seconds.")
            return

        # Reset lock if timeout passed
        if self.lock_time and time() >= self.lock_time:
            self.failed_attempts = 0
            self.lock_time = None

        # Encrypt password
        hashed_password = sha256(password.encode()).hexdigest()

        # Connect to database
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            # Query database for user details
            cursor.execute("""
                SELECT id, name, email, role
                FROM users
                WHERE username = ? AND password = ?
            """, (username, hashed_password))
            user = cursor.fetchone()

            if user:
                user_info = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "role": user[3]
                }
                self.failed_attempts = 0  # Reset failed attempts
                self.redirect_dashboard(user_info)
            else:
                self.failed_attempts += 1
                self.handle_failed_attempts()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    
    def handle_failed_attempts(self):
        if self.failed_attempts >= 3:
            self.lock_time = time() + 30  # Lock for 30 seconds
            messagebox.showerror("Too Many Attempts", "You have been locked out. Try again in 30 seconds.")
        else:
            remaining_attempts = 3 - self.failed_attempts
            messagebox.showerror("Error", f"Invalid username or password. {remaining_attempts} attempts remaining.")

    def redirect_dashboard(self, user_info):
        if user_info['role'] == "Admin":
            self.main_container.destroy()
            AdminDashboard(self.root, user_info, self)
            messagebox.showinfo("Admin", f"Welcome to the Admin Dashboard, {user_info['name']}!")
        elif user_info['role'] == "Teacher":
            messagebox.showinfo("Teacher", f"Welcome to the Teacher Dashboard, {user_info['name']}!")
        elif user_info['role'] == "Student":
            self.main_container.destroy()
            StudentDashboard(self.root, user_info, self)
            messagebox.showinfo("Student", f"Welcome to the Student Dashboard, {user_info['name']}!")

class StudentOptions:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Access")
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Header
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(50, 30))
        
        ttk.Label(header_frame,
                 text="Student Access",
                 style="Title.TLabel").pack()

        # Content frame
        content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        content_frame.pack(expand=True)

        ttk.Label(content_frame,
                 text="Choose an option",
                 style="Subtitle.TLabel").pack(pady=(0, 30))

        # Options frame
        options_frame = ttk.Frame(content_frame, style="Content.TFrame")
        options_frame.pack()

        # Login option
        login_frame = ttk.Frame(options_frame, style="Card.TFrame")
        login_frame.pack(side='left', padx=20)
        
        ttk.Label(login_frame,
                 text="Existing Student?",
                 style="Card.TLabel").pack(pady=(0, 10))
        
        ttk.Button(login_frame,
                  text="Login",
                  style="Custom.TButton",
                  command=self.show_login).pack()

        # Registration option
        register_frame = ttk.Frame(options_frame, style="Card.TFrame")
        register_frame.pack(side='left', padx=20)
        
        ttk.Label(register_frame,
                 text="New Student?",
                 style="Card.TLabel").pack(pady=(0, 10))
        
        # Use lambda to call show_registration explicitly
        ttk.Button(register_frame,
                  text="Register",
                  style="Custom.TButton",
                  command=lambda: self.show_registration()).pack()

        # Back button
        back_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        back_frame.pack(pady=30)
        
        ttk.Button(back_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack()

    def show_registration(self):
        self.main_container.destroy()
        StudentRegistration(self.root)

    def go_back(self):
        self.main_container.destroy()
        UserTypeSelection(self.root)


class StudentRegistration:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Registration")

        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Header
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(50, 30))

        ttk.Label(header_frame,
                 text="Student Registration",
                 style="Title.TLabel").pack()

        # Content frame
        content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        content_frame.pack(expand=True)

        # Registration fields
        fields = [
            ("Username:", 0),
            ("Password:", 1),
            ("Email:", 2),
            ("Full Name:", 3),
            ("Class:", 4)
        ]

        self.entries = {}

        for label_text, row in fields:
            ttk.Label(content_frame,
                     text=label_text,
                     style="Subtitle.TLabel").grid(row=row, column=0, padx=10, pady=10, sticky='w')
            if label_text == "Password:":
                entry = ttk.Entry(content_frame, show="*")
            else:
                entry = ttk.Entry(content_frame)
            entry.grid(row=row, column=1, padx=10, pady=10)
            self.entries[label_text] = entry

        # Button frame
        button_frame = ttk.Frame(content_frame, style="Content.TFrame")
        button_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=20)

        # Register button
        ttk.Button(button_frame,
                  text="Register",
                  style="Custom.TButton",
                  command=self.register).pack(side='left', padx=10)

        # Back button
        ttk.Button(button_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack(side='left', padx=10)

    def register(self):
        username = self.entries["Username:"].get()
        password = self.entries["Password:"].get()
        email = self.entries["Email:"].get()
        name = self.entries["Full Name:"].get()
        class_name = self.entries["Class:"].get()

        if not all([username, password, email, name, class_name]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            # Insert into users table
            cursor.execute("""
                INSERT INTO users (username, password, email, name, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed_password, email, name, 'Student'))

            # Commit the user insertion to get the user_id
            conn.commit()

            # Get the user_id of the newly created user
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]

            # Insert into students table
            cursor.execute("""
                INSERT INTO students (id, class)
                VALUES (?, ?)
            """, (user_id, class_name))

            # Commit the student insertion
            conn.commit()

            messagebox.showinfo("Success", "Registration successful! You can now login.")
            self.main_container.destroy()
            UserTypeSelection(self.root)

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or Email already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def go_back(self):
        self.main_container.destroy()
        UserTypeSelection(self.root)


class ExamInterface:
    def __init__(self, root, student_id, exam_id):
        from exam_interface import ExamInterface
        return ExamInterface(root, student_id, exam_id)


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#121212')  # Set root window background to dark
    
    app = UserTypeSelection(root)
    root.mainloop()