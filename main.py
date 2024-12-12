import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from admin_dashboard import AdminDashboard
from student_dashboard import StudentDashboard
from database import create_database
from datetime import datetime

class UserTypeSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Portal")
        
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
        self.style.configure("Card.TFrame",
                           background=self.colors['sidebar'],
                           relief="flat",
                           borderwidth=0)
        
        self.style.configure("Title.TLabel",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 24, 'bold'))
        
        self.style.configure("Subtitle.TLabel",
                           background=self.colors['content'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 14))
                           
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
                           padding=(20, 10))
                           
        self.style.map("Custom.TButton",
                      background=[('active', self.colors['accent1'])],
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
                 text="Choose your role to get started",
                 style="Subtitle.TLabel").pack(anchor='center', pady=10)
        
        # Cards container
        cards_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        cards_frame.pack(expand=True, fill='both', padx=100)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
        # Teacher card
        teacher_card = ttk.Frame(cards_frame, style="Card.TFrame")
        teacher_card.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        ttk.Label(teacher_card,
                 text="👨‍🏫 Teacher Access",
                 style="Card.TLabel").pack(pady=(20, 10))
        
        ttk.Label(teacher_card,
                 text="Create and manage exams",
                 style="Card.TLabel",
                 foreground=self.colors['text_secondary']).pack(pady=(0, 20))
        
        ttk.Button(teacher_card,
                  text="Login as Teacher",
                  style="Custom.TButton",
                  command=self.show_teacher_login).pack(pady=(0, 20))
        
        # Student card
        student_card = ttk.Frame(cards_frame, style="Card.TFrame")
        student_card.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        ttk.Label(student_card,
                 text="👨‍🎓 Student Access",
                 style="Card.TLabel").pack(pady=(20, 10))
        
        ttk.Label(student_card,
                 text="Take exams and view results",
                 style="Card.TLabel",
                 foreground=self.colors['text_secondary']).pack(pady=(0, 20))
        
        button_frame = ttk.Frame(student_card, style="Card.TFrame")
        button_frame.pack(pady=(0, 20))
        
        ttk.Button(button_frame,
                  text="Login",
                  style="Custom.TButton",
                  command=self.show_student_login).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                  text="Register",
                  style="Custom.TButton",
                  command=self.show_student_register).pack(side='left', padx=5)

    def show_teacher_login(self):
        self.main_container.destroy()
        TeacherLogin(self.root)
    
    def show_student_login(self):
        self.main_container.destroy()
        StudentLogin(self.root)
    
    def show_student_register(self):
        self.main_container.destroy()
        StudentRegistration(self.root)

    def show_student_options(self):
        self.main_container.destroy()
        StudentOptions(self.root)


class StudentOptions:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Access")
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Header
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(50,30))
        
        ttk.Label(header_frame,
                 text="Student Access",
                 style="Title.TLabel").pack()

        # Content frame
        content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        content_frame.pack(expand=True)

        ttk.Label(content_frame,
                 text="Choose an option",
                 style="Subtitle.TLabel").pack(pady=(0,30))

        # Options frame
        options_frame = ttk.Frame(content_frame, style="Content.TFrame")
        options_frame.pack()

        # Login option
        login_frame = ttk.Frame(options_frame, style="Card.TFrame")
        login_frame.pack(side='left', padx=20)
        
        ttk.Label(login_frame,
                 text="Existing Student?",
                 style="Card.TLabel").pack(pady=(0,10))
        
        ttk.Button(login_frame,
                  text="Login",
                  style="Custom.TButton",
                  command=self.show_login).pack()

        # Registration option
        register_frame = ttk.Frame(options_frame, style="Card.TFrame")
        register_frame.pack(side='left', padx=20)
        
        ttk.Label(register_frame,
                 text="New Student?",
                 style="Card.TLabel").pack(pady=(0,10))
        
        ttk.Button(register_frame,
                  text="Register",
                  style="Custom.TButton",
                  command=self.show_registration).pack()

        # Back button
        back_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        back_frame.pack(pady=30)
        
        ttk.Button(back_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack()

    def show_login(self):
        self.main_container.destroy()
        StudentLogin(self.root)

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
        header_frame.pack(fill='x', pady=(50,30))
        
        ttk.Label(header_frame,
                 text="Student Registration",
                 style="Title.TLabel").pack()

        # Content frame
        content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        content_frame.pack(expand=True)

        # Registration fields
        ttk.Label(content_frame,
                 text="Username:",
                 style="Subtitle.TLabel").grid(row=0, column=0, padx=10, pady=10)
        self.username = ttk.Entry(content_frame)
        self.username.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(content_frame,
                 text="Password:",
                 style="Subtitle.TLabel").grid(row=1, column=0, padx=10, pady=10)
        self.password = ttk.Entry(content_frame, show="*")
        self.password.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(content_frame,
                 text="Full Name:",
                 style="Subtitle.TLabel").grid(row=2, column=0, padx=10, pady=10)
        self.name = ttk.Entry(content_frame)
        self.name.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(content_frame,
                 text="Class:",
                 style="Subtitle.TLabel").grid(row=3, column=0, padx=10, pady=10)
        self.class_name = ttk.Entry(content_frame)
        self.class_name.grid(row=3, column=1, padx=10, pady=10)

        # Button frame
        button_frame = ttk.Frame(content_frame, style="Content.TFrame")
        button_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Register button with icon
        register_frame = ttk.Frame(button_frame, style="Card.TFrame")
        register_frame.pack(side='left', padx=20)
        
        ttk.Button(register_frame,
                  text="Register",
                  style="Custom.TButton",
                  command=self.register).pack(pady=10)

        # Back button with icon
        back_frame = ttk.Frame(button_frame, style="Card.TFrame")
        back_frame.pack(side='left', padx=20)
        
        ttk.Button(back_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack(pady=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()
        name = self.name.get()
        class_name = self.class_name.get()

        if not all([username, password, name, class_name]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO students (username, password, name, class)
                VALUES (?, ?, ?, ?)
            """, (username, hashed_password, name, class_name))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now login.")
            self.main_container.destroy()
            StudentLogin(self.root)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()

    def go_back(self):
        self.main_container.destroy()
        StudentOptions(self.root)


class StudentLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Login")
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Center container
        center_container = ttk.Frame(self.main_container, style="Content.TFrame")
        center_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create a frame for the content that will be centered
        content_frame = ttk.Frame(center_container, style="Card.TFrame")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(content_frame,
                 text="Student Login",
                 style="Title.TLabel").pack(pady=30)

        # Login form
        form_frame = ttk.Frame(content_frame, style="Content.TFrame")
        form_frame.pack(padx=50, pady=20)

        # Username
        ttk.Label(form_frame,
                 text="Username",
                 style="Subtitle.TLabel").pack(anchor='w')
        self.username = ttk.Entry(form_frame, width=40)
        self.username.pack(fill='x', pady=(0, 15))

        # Password
        ttk.Label(form_frame,
                 text="Password",
                 style="Subtitle.TLabel").pack(anchor='w')
        self.password = ttk.Entry(form_frame, show="*", width=40)
        self.password.pack(fill='x', pady=(0, 30))

        # Buttons frame
        button_frame = ttk.Frame(content_frame, style="Content.TFrame")
        button_frame.pack(pady=20)

        ttk.Button(button_frame,
                  text="Login",
                  style="Custom.TButton",
                  command=self.login).pack(side='left', padx=10)

        ttk.Button(button_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack(side='left', padx=10)

    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Both fields are required!")
            return

        # Hash the password using SHA-256 to match registration
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check credentials
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name FROM students
            WHERE username = ? AND password = ?
        """, (username, hashed_password))
        
        student = cursor.fetchone()
        conn.close()

        if student:
            messagebox.showinfo("Success", f"Welcome {student[1]}!")
            self.main_container.destroy()
            StudentDashboard(self.root, student[0], self)
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def go_back(self):
        self.main_container.destroy()
        StudentOptions(self.root)


class TeacherLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Teacher Login")
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Center container
        center_container = ttk.Frame(self.main_container, style="Content.TFrame")
        center_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create a frame for the content that will be centered
        content_frame = ttk.Frame(center_container, style="Card.TFrame")
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(content_frame,
                 text="Teacher Login",
                 style="Title.TLabel").pack(pady=30)

        # Login form
        form_frame = ttk.Frame(content_frame, style="Content.TFrame")
        form_frame.pack(padx=50, pady=20)

        # Username
        ttk.Label(form_frame,
                 text="Username",
                 style="Subtitle.TLabel").pack(anchor='w')
        self.username = ttk.Entry(form_frame, width=40)
        self.username.pack(fill='x', pady=(0, 15))

        # Password
        ttk.Label(form_frame,
                 text="Password",
                 style="Subtitle.TLabel").pack(anchor='w')
        self.password = ttk.Entry(form_frame, show="*", width=40)
        self.password.pack(fill='x', pady=(0, 30))

        # Buttons frame
        button_frame = ttk.Frame(content_frame, style="Content.TFrame")
        button_frame.pack(pady=20)

        ttk.Button(button_frame,
                  text="Login",
                  style="Custom.TButton",
                  command=self.login).pack(side='left', padx=10)

        ttk.Button(button_frame,
                  text="Back",
                  style="Custom.TButton",
                  command=self.go_back).pack(side='left', padx=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username=? AND password=?",
                       (username, hashed_password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            self.root.withdraw()
            admin_window = tk.Toplevel()
            AdminDashboard(admin_window, admin[0], self.root)
        else:
            messagebox.showerror("Error", "Invalid credentials")

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