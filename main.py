import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from admin_dashboard import AdminDashboard
from student_dashboard import StudentDashboard
from Teacher_dashboard import TeacherDashboard
from hashlib import sha256 
from time import time

class UserTypeSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Portal")
        self.failed_attempts = 0
        self.lock_time = None

        # Configure the window
        self.root.state('zoomed')

        # Colors
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

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Content.TFrame", background=self.colors['content'])
        self.style.configure("Card.TFrame", background=self.colors['sidebar'], relief="flat", padding=30)
        self.style.configure("Title.TLabel", background=self.colors['content'], foreground=self.colors['text'], font=('Segoe UI', 30, 'bold'))
        self.style.configure("Subtitle.TLabel", background=self.colors['content'], foreground=self.colors['text_secondary'], font=('Segoe UI', 18))
        self.style.configure("Card.TLabel", background=self.colors['sidebar'], foreground=self.colors['text'], font=('Segoe UI', 12))
        self.style.configure("Custom.TButton", background=self.colors['accent1'], foreground=self.colors['bg_dark'], font=('Segoe UI', 14), padding=(10, 5))
        self.style.map("Custom.TButton", background=[('active', self.colors['hover'])], foreground=[('active', self.colors['bg_dark'])])

        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        # Header
        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(30, 20))
        ttk.Label(header_frame, text="Welcome to Examination System", style="Title.TLabel").pack(anchor='center')
        ttk.Label(header_frame, text="Login to continue", style="Subtitle.TLabel").pack(anchor='center', pady=10)

        # Login Card
        user_card = ttk.Frame(self.main_container, style="Card.TFrame")
        user_card.pack(pady=40, padx=200, ipadx=100, ipady=50)

        ttk.Label(user_card, text="Username:", style="Card.TLabel").pack(pady=(10, 5), anchor='w')
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(user_card, textvariable=self.username_var, font=('Segoe UI', 14))
        self.username_entry.pack(pady=5, fill='x', expand=True)

        ttk.Label(user_card, text="Password:", style="Card.TLabel").pack(pady=(10, 5), anchor='w')
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(user_card, textvariable=self.password_var, show='*', font=('Segoe UI', 14))
        self.password_entry.pack(pady=5, fill='x', expand=True)

        ttk.Button(user_card, text="Login", style="Custom.TButton", command=self.verify_login).pack(pady=(20, 10), fill='x')
        ttk.Button(user_card, text="Register", style="Custom.TButton", command=self.show_student_register).pack(pady=(10, 20), fill='x')

    def show_student_register(self):
        self.main_container.destroy()
        StudentRegistration(self.root)

    def verify_login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if self.lock_time and time() < self.lock_time:
            remaining_time = int(self.lock_time - time())
            messagebox.showerror("Locked", f"Too many failed attempts. Try again in {remaining_time} seconds.")
            return 

        if self.lock_time and time() >= self.lock_time:
            self.failed_attempts = 0
            self.lock_time = None

        hashed_password = sha256(password.encode()).hexdigest()

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT u.id, u.name, u.email, u.role, s.id, t.id
                FROM users u
                LEFT JOIN teachers t ON u.id = t.id
                LEFT JOIN subjects s ON t.subject_id = s.id
                WHERE u.username = ? AND u.password = ?
            ''', (username, hashed_password))
            user = cursor.fetchone()

            if user:
                user_info = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "role": user[3],
                    "subject_id": user[4], 
                    "teacher_id": user[5]  # Teacher ID
                }
                self.failed_attempts = 0
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
            self.lock_time = time() + 30
            messagebox.showerror("Too Many Attempts", "You have been locked out. Try again in 30 seconds.")
        else:
            remaining_attempts = 3 - self.failed_attempts
            messagebox.showerror("Error", f"Invalid username or password. {remaining_attempts} attempts remaining.")

    def redirect_dashboard(self, user_info):
        if user_info['role'] == "Admin":
            self.main_container.destroy()
            AdminDashboard(self.root, user_info["id"], self)
            messagebox.showinfo("Admin", f"Welcome to the Admin Dashboard, {user_info['name']}!")
        elif user_info['role'] == "Teacher":
            self.main_container.destroy()
            TeacherDashboard(self.root, user_info)
            messagebox.showinfo("Teacher", f"Welcome to the Teacher Dashboard, {user_info['name']}!")
        elif user_info['role'] == "Student":
            self.main_container.destroy()
            StudentDashboard(self.root, user_info["id"], self)
            messagebox.showinfo("Student", f"Welcome to the Student Dashboard, {user_info['name']}!")


class StudentRegistration:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Registration")

        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)

        header_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(30, 20))

        ttk.Label(header_frame, text="Student Registration", style="Title.TLabel").pack()

        user_card = ttk.Frame(self.main_container, style="Card.TFrame")
        user_card.pack(pady=40, padx=200, ipadx=100, ipady=50)

        fields = ["Username:", "Password:", "Email:", "Full Name:", "Class:"]
        self.entries = {}

        for field in fields:
            ttk.Label(user_card, text=field, style="Card.TLabel").pack(pady=(10, 5), anchor='w')
            entry = ttk.Entry(user_card, font=('Segoe UI', 14))
            if field == "Password:":
                entry.config(show="*")
            entry.pack(pady=5, fill='x', expand=True)
            self.entries[field] = entry

        ttk.Button(user_card, text="Register", style="Custom.TButton", command=self.register).pack(pady=(20, 10), fill='x')
        ttk.Button(user_card, text="Back", style="Custom.TButton", command=self.go_back).pack(pady=(10, 20), fill='x')

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


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#121212')  # Set root window background to dark
    
    app = UserTypeSelection(root)
    root.mainloop()