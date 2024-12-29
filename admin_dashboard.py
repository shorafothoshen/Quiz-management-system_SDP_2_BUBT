import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

class AdminDashboard:
    def __init__(self, root, admin_id, login_window):
        self.root = root
        self.admin_id = admin_id
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
        self.create_nav_button("👥 Manage Teachers", self.show_teachers_page)
        self.create_nav_button("📚 Manage Subjects", self.show_subject_page)
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

        add_button = ttk.Button(button_frame, text="Add Student", command=self.show_add_student_page)
        add_button.pack(side='left', padx=10)

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

    def show_add_student_page(self):
        self.current_page = "add_student"  # Update current page
        self.clear_content()  # Clear the current content before showing Add Student page

        # Create add student page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Add New Student",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Input fields
        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        fields = ["Name", "Username", "Email", "Password", "Class", "Phone"]
        entries = {}

        for field in fields: 
            ttk.Label(form_frame, text=field + ":", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content']).pack(pady=(5, 5), anchor='w') 
            if field == "Password": 
                entry = ttk.Entry(form_frame, font=('Segoe UI', 12), show="*") 
            else: 
                entry = ttk.Entry(form_frame, font=('Segoe UI', 12)) 
            entry.pack(fill='x', pady=(0, 10)) 
            entries[field] = entry
        
        # Add button
        add_button = ttk.Button(page_frame, text="Save", command=lambda: self.add_student_to_database(
            entries["Name"], entries["Username"], entries["Email"], entries["Password"], entries["Class"], entries["Phone"]))
        add_button.pack(pady=20)

        # Corrected Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_students_page)  # Going back to student list
        back_button.pack(pady=10)

    def add_student_to_database(self, name_var, username_var, email_var, password_var, class_var, phone_var):
        name = name_var.get().strip()
        username = username_var.get().strip()
        email = email_var.get().strip()
        password = password_var.get().strip()
        class_name = class_var.get().strip()
        phone = phone_var.get().strip()

        # Validation
        if not name or not username or not email or not password or not class_name or not phone:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Hash the password using hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert data into database
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            # Insert into users table
            cursor.execute('''
                INSERT INTO users (username, name, email, password, role)
                VALUES (?, ?, ?, ?, 'Student')
            ''', (username, name, email, hashed_password))

            # Get the last inserted user ID
            user_id = cursor.lastrowid

            # Insert into students table
            cursor.execute('''
                INSERT INTO students (id, class, phone)
                VALUES (?, ?, ?)
            ''', (user_id, class_name, phone))

            conn.commit()
            messagebox.showinfo("Success", "New student added successfully!")
            
            # Return to the student list page
            self.show_students_page()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username must be unique!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
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
        form_frame = ttk.Frame(edit_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        fields = {
            "Name": current_name,
            "Email": current_email,
            "Class": current_class
        }
        entries = {}

        for field, value in fields.items(): 
            ttk.Label(form_frame, text=field + ":", font=("Segoe UI", 12), foreground=self.colors['text'], background=self.colors['content']).pack(pady=(5, 5), anchor='w') 
            entry = ttk.Entry(form_frame, font=("Segoe UI", 12)) 
            entry.insert(0, value) 
            if field == "Password": 
                entry.config(show="*") 
            entry.pack(fill='x', pady=(0, 10)) 
            entries[field] = entry
            
        # Save Button
        save_button = ttk.Button(edit_frame, text="Save", 
                                command=lambda: self.save_student_data(student_id, entries["Name"], entries["Email"], entries["Class"]))
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
    
    def show_teachers_page(self):
        if self.current_page == "teachers":
            return
        self.current_page = "teachers"
        self.clear_content()  # Clear the current content before loading the page

        # Create teachers page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Manage Teachers",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Teacher list
        self.teacher_tree = ttk.Treeview(page_frame,
                                        columns=("ID", "Username", "Name", "Phone", "Subject"),
                                        show="headings",
                                        style="Treeview")
        self.teacher_tree.heading("ID", text="ID")
        self.teacher_tree.heading("Username", text="Username")
        self.teacher_tree.heading("Name", text="Name")
        self.teacher_tree.heading("Phone", text="Phone")
        self.teacher_tree.heading("Subject", text="Subject")
        self.teacher_tree.pack(pady=10, expand=True, fill='both')

        # Add buttons for Add, Edit, and Delete
        button_frame = ttk.Frame(page_frame)
        button_frame.pack(pady=20)

        add_button = ttk.Button(button_frame, text="Add Teacher", command=self.show_add_teacher_page)
        add_button.pack(side='left', padx=10)

        edit_button = ttk.Button(button_frame, text="Edit Teacher", command=self.edit_teacher)
        edit_button.pack(side='left', padx=10)

        delete_button = ttk.Button(button_frame, text="Delete Teacher", command=self.delete_teacher)
        delete_button.pack(side='left', padx=10)

        self.refresh_teacher_list()

    def refresh_teacher_list(self):
        # Clear existing data
        for row in self.teacher_tree.get_children():
            self.teacher_tree.delete(row)

        # Fetch teachers from the database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.username, u.name, t.phone, s.subject_name
            FROM users u
            JOIN teachers t ON u.id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE u.role = 'Teacher'
        ''')

        teachers = cursor.fetchall()

        for teacher in teachers:
            self.teacher_tree.insert("", "end", values=teacher)

        conn.close()

    def show_add_teacher_page(self):
        self.current_page = "add_teacher"  # Update current page
        self.clear_content()  # Clear the current content before showing Add Teacher page

        # Create add teacher page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Add New Teacher",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Input fields
        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        fields = ["Name", "Username", "Email", "Password", "Phone"]
        entries = {}

        for field in fields:
            label = ttk.Label(form_frame, text=field, font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content'])
            label.pack(anchor='w', pady=5)
            if field == "Password":
                entry = ttk.Entry(form_frame, font=('Segoe UI', 12), show="*")
            else:
                entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
            entry.pack(fill='x', pady=5)
            entries[field] = entry

        # Subject dropdown
        ttk.Label(form_frame, text="Subject", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content']).pack(anchor='w', pady=5)
        subject_var = tk.StringVar()
        subject_dropdown = ttk.Combobox(form_frame, textvariable=subject_var, font=('Segoe UI', 12), state="readonly")
        subject_dropdown.pack(fill='x', pady=5)

        # Fetch subjects from database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT subject_name FROM subjects')  # Assuming subjects table has 'subject_name' column
        subjects = [row[0] for row in cursor.fetchall()]
        conn.close()

        subject_dropdown['values'] = subjects
        entries["Subject"] = subject_var

        # Add button
        add_button = ttk.Button(page_frame, text="Save", command=lambda: self.add_teacher_to_database(entries))
        add_button.pack(pady=20)

        # Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_teachers_page)
        back_button.pack(pady=20)

    def add_teacher_to_database(self, entries):
        # Get the input data from the form
        name = entries['Name'].get().strip()
        username = entries['Username'].get().strip()
        email = entries['Email'].get().strip()
        password = entries['Password'].get().strip()
        phone = entries['Phone'].get().strip()
        subject_name = entries['Subject'].get().strip()

        if not name or not username or not email or not password or not phone or not subject_name:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Encrypt the password using SHA256
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            # Insert into users table
            cursor.execute('''
                INSERT INTO users (username, password, name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, encrypted_password, name, email, 'Teacher'))

            # Get the ID of the inserted user
            user_id = cursor.lastrowid

            # Find the subject_id from the subjects table
            cursor.execute('''
                SELECT id FROM subjects WHERE subject_name = ?
            ''', (subject_name,))
            subject_row = cursor.fetchone()

            if not subject_row:
                messagebox.showerror("Error", f"Subject '{subject_name}' not found in the database.")
                return

            subject_id = subject_row[0]

            # Insert into teachers table
            cursor.execute('''
                INSERT INTO teachers (id, phone, subject_id)
                VALUES (?, ?, ?)
            ''', (user_id, phone, subject_id))

            conn.commit()
            messagebox.showinfo("Success", "Teacher added successfully!")
            self.show_teachers_page()

        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", f"Failed to add teacher. Integrity error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def edit_teacher(self):
        selected_item = self.teacher_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a teacher to edit!")
            return

        teacher_id = self.teacher_tree.item(selected_item, 'values')[0]

        self.current_page = "edit_teacher"  # Update current page
        self.clear_content()  # Clear the current content before showing Edit Teacher page

        # Create edit page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Edit Teacher",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Fetch teacher details
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()
        # Fetch teacher details
        cursor.execute('''
            SELECT u.name, u.username, u.email, t.phone, s.subject_name
            FROM users u
            JOIN teachers t ON u.id = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE u.id = ?
        ''', (teacher_id,))
        teacher_data = cursor.fetchone()
        # Fetch subjects from database
        cursor.execute('SELECT id, subject_name FROM subjects')
        subjects = cursor.fetchall()
        conn.close()

        if not teacher_data:
            messagebox.showerror("Error", "Unable to fetch teacher details!")
            return

        fields = ["Name", "Username", "Email", "Phone"]
        entries = {}

        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        for i, field in enumerate(fields):
            label = ttk.Label(form_frame, text=field, font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content'])
            label.pack(anchor='w', pady=5)
            entry = ttk.Entry(form_frame, font=('Segoe UI', 12))
            entry.insert(0, teacher_data[i])
            entry.pack(fill='x', pady=5)
            entries[field] = entry

        # Subject dropdown
        ttk.Label(form_frame, text="Subject", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content']).pack(anchor='w', pady=5)

        subject_var = tk.StringVar()
        subject_dropdown = ttk.Combobox(form_frame, textvariable=subject_var, font=('Segoe UI', 12), state="readonly")
        subject_dropdown['values'] = [subject[1] for subject in subjects]

        # Set default selected subject if it exists
        default_subject = next((subject[1] for subject in subjects if subject[0] == teacher_data[4]), None)
        if default_subject:
            subject_dropdown.set(default_subject)

        subject_dropdown.pack(fill='x', pady=5)
        entries["Subject"] = subject_var


        # Save button
        save_button = ttk.Button(page_frame, text="Save Changes", command=lambda: self.save_teacher_changes(teacher_id, entries, subjects))
        save_button.pack(pady=20)

        # Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_teachers_page)
        back_button.pack(pady=20)

    def save_teacher_changes(self, teacher_id, entries, subjects):
        name = entries['Name'].get().strip()
        username = entries['Username'].get().strip()
        email = entries['Email'].get().strip()
        phone = entries['Phone'].get().strip()
        subject_name = entries['Subject'].get().strip()

        if not name or not username or not email or not phone or not subject_name:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Get the subject_id from the subject_name
        subject_id = next((subject[0] for subject in subjects if subject[1] == subject_name), None)

        if not subject_id:
            messagebox.showerror("Error", "Selected subject is not valid.")
            return

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            # Update users table
            cursor.execute('''UPDATE users
                            SET name = ?, username = ?, email = ?
                            WHERE id = ?''', (name, username, email, teacher_id))

            # Update teachers table
            cursor.execute('''UPDATE teachers
                            SET phone = ?, subject_id = ?
                            WHERE id = ?''', (phone, subject_id, teacher_id))

            conn.commit()
            messagebox.showinfo("Success", "Teacher details updated successfully!")
            self.show_teachers_page()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or email must be unique!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def delete_teacher(self):
        selected_item = self.teacher_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a teacher to delete!")
            return

        teacher_id = self.teacher_tree.item(selected_item, 'values')[0]

        # Confirm delete
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this teacher?")
        if not confirm:
            return

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            # Delete from teachers table
            cursor.execute('''DELETE FROM teachers WHERE id = ?''', (teacher_id,))

            # Delete from users table
            cursor.execute('''DELETE FROM users WHERE id = ?''', (teacher_id,))

            conn.commit()
            messagebox.showinfo("Success", "Teacher deleted successfully!")
            self.refresh_teacher_list()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def show_subject_page(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Manage Subjects", style="Subtitle.TLabel").pack(pady=10)

        self.tree = ttk.Treeview(self.content_frame, columns=("ID", "Subject Name"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Subject Name", text="Subject Name")

        self.tree.pack(fill='both', expand=True, padx=20, pady=20)

        button_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text="Add Subject", command=self.add_subject)
        add_button.pack(side='left', padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Subject", command=self.edit_subject)
        edit_button.pack(side='left', padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Subject", command=self.delete_subject)
        delete_button.pack(side='left', padx=5)

        self.populate_subjects_tree()

    def populate_subjects_tree(self):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id, subject_name FROM subjects")
        subjects = cursor.fetchall()

        for subject in subjects:
            self.tree.insert("", 'end', values=subject)

        conn.close()

    def add_subject(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Add New Subject", style="Subtitle.TLabel").pack(pady=10)

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        subject_name_var = tk.StringVar()

        ttk.Label(form_frame, text="Subject Name:", style="Text.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        ttk.Entry(form_frame, textvariable=subject_name_var, style="Content.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky='w')

        submit_button = ttk.Button(form_frame, text="Add Subject", style="Custom.TButton", command=lambda: self.submit_subject(subject_name_var.get()))
        submit_button.grid(row=1, columnspan=2, pady=20)

        # Add Back button
        back_button = ttk.Button(form_frame, text="Back", style="Custom.TButton", command=self.show_subject_page)
        back_button.grid(row=2, columnspan=2, pady=10)


    def submit_subject(self, subject_name):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject_name,))
            conn.commit()
            messagebox.showinfo("Success", "Subject added successfully!")
            self.show_subject_page()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        finally:
            conn.close()

    def edit_subject(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a subject to edit!")
            return

        subject_id = self.tree.item(selected_item, 'values')[0]
        self.show_edit_subject_page(subject_id)

    def show_edit_subject_page(self, subject_id):
        self.clear_content()

        ttk.Label(self.content_frame, text="Edit Subject", style="Subtitle.TLabel").pack(pady=10)

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name FROM subjects WHERE id = ?", (subject_id,))
        subject_name = cursor.fetchone()[0]
        conn.close()

        form_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        subject_name_var = tk.StringVar(value=subject_name)

        ttk.Label(form_frame, text="Subject Name:", style="Text.TLabel").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        ttk.Entry(form_frame, textvariable=subject_name_var, style="Content.TEntry").grid(row=0, column=1, padx=10, pady=10, sticky='w')

        submit_button = ttk.Button(form_frame, text="Save Changes", style="Custom.TButton", command=lambda: self.update_subject(subject_id, subject_name_var.get()))
        submit_button.grid(row=1, columnspan=2, pady=20)

        # Add Back button
        back_button = ttk.Button(form_frame, text="Back", style="Custom.TButton", command=self.show_subject_page)
        back_button.grid(row=2, columnspan=2, pady=10)


    def update_subject(self, subject_id, subject_name):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE subjects SET subject_name = ? WHERE id = ?", (subject_name, subject_id))
            conn.commit()
            messagebox.showinfo("Success", "Subject updated successfully!")
            self.show_subject_page()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

        finally:
            conn.close()

    def delete_subject(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a subject to delete!")
            return

        subject_id = self.tree.item(selected_item, 'values')[0]

    def show_exams_page(self):
        if self.current_page == "exams":
            return
        
        self.clear_content()
        self.current_page = "exams"

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
        
        # Add buttons for Add, Edit, and Delete
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text="Add Exam", command=self.show_add_exam_page)
        add_button.pack(side='left', padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Exam", command=self.edit_exam)
        edit_button.pack(side='left', padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Exam", command=self.delete_exam)
        delete_button.pack(side='left', padx=5)
        
        # Load exams
        self.refresh_exam_list()


    def refresh_exam_list(self):
        # Connect to the database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        # Fetch exams data with subject names
        cursor.execute('''
        SELECT exams.id, exams.title, subjects.subject_name AS subject, exams.duration, users.name AS created_by
        FROM exams
        LEFT JOIN subjects ON exams.subject_id = subjects.id
        LEFT JOIN users ON exams.created_by = users.id
        ''')
        exams = cursor.fetchall()

        # Clear the existing items in the Treeview
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)

        # Insert the fetched data into the Treeview
        for exam in exams:
            self.exam_tree.insert('', 'end', values=exam)

        # Close the database connection
        conn.close()


    def show_add_exam_page(self):
        self.clear_content()  # Clear the current content before showing Add Exam page
        self.current_page = "add_exam"

        # Create add exam page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Add New Exam",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Input fields
        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        # Title field
        row = ttk.Frame(form_frame)
        row.pack(fill='x', pady=5)

        label = ttk.Label(row, text="Title:", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content'])
        label.pack(side='left', padx=5)

        title_entry = ttk.Entry(row, font=('Segoe UI', 12))
        title_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Subject dropdown
        subject_row = ttk.Frame(form_frame)
        subject_row.pack(fill='x', pady=5)

        subject_label = ttk.Label(subject_row, text="Subject:", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content'])
        subject_label.pack(side='left', padx=5)

        subject_combobox = ttk.Combobox(subject_row, font=('Segoe UI', 12), state='readonly')
        subject_combobox.pack(side='left', fill='x', expand=True, padx=5)

        # Load subjects from database
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject_name FROM subjects")
        subjects = cursor.fetchall()
        conn.close()

        # Populate the combobox
        subject_dict = {subject[1]: subject[0] for subject in subjects}  # Map subject_name to subject_id
        subject_combobox['values'] = list(subject_dict.keys())

        # Duration field
        duration_row = ttk.Frame(form_frame)
        duration_row.pack(fill='x', pady=5)

        duration_label = ttk.Label(duration_row, text="Duration (minutes):", font=('Segoe UI', 12), foreground=self.colors['text'], background=self.colors['content'])
        duration_label.pack(side='left', padx=5)

        duration_entry = ttk.Entry(duration_row, font=('Segoe UI', 12))
        duration_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Save button
        save_button = ttk.Button(page_frame, text="Save", command=lambda: self.add_exam_to_database(title_entry.get(), subject_combobox.get(), duration_entry.get(), subject_dict))
        save_button.pack(pady=20)

        # Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_exams_page)  # Going back to exam list
        back_button.pack(pady=10)


    def add_exam_to_database(self, title, selected_subject, duration, subject_dict):
        # Validate inputs
        if not title or not selected_subject or not duration:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            subject_id = subject_dict[selected_subject]  # Get subject_id from selected subject name
            duration = int(duration)  # Validate duration

            conn = sqlite3.connect("exam_system.db")
            cursor = conn.cursor()

            # Insert into exams table
            cursor.execute('''
                INSERT INTO exams (title, subject_id, duration, created_by)
                VALUES (?, ?, ?, ?)
            ''', (title, subject_id, duration, self.admin_id))

            conn.commit()
            messagebox.showinfo("Success", "Exam added successfully!")
            self.show_exams_page()

        except ValueError:
            messagebox.showerror("Error", "Duration must be a number!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    
    def edit_exam(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an exam to edit!")
            return

        exam_id = self.exam_tree.item(selected_item, 'values')[0]
        self.show_edit_exam_page(exam_id)


    def show_edit_exam_page(self, exam_id):
        self.clear_content()
        self.current_page = "edit_exam"

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()
        
        # Fetch exam data and subject options
        cursor.execute('''
            SELECT exams.title, subjects.subject_name, exams.duration
            FROM exams
            JOIN subjects ON exams.subject_id = subjects.id
            WHERE exams.id = ?
        ''', (exam_id,))
        exam_data = cursor.fetchone()

        cursor.execute('SELECT id, subject_name FROM subjects')
        subjects_data = cursor.fetchall()
        
        conn.close()

        if not exam_data:
            messagebox.showerror("Error", "Exam not found!")
            return

        current_title, current_subject, current_duration = exam_data

        # Create a dictionary for subjects for the dropdown
        subjects_dict = {subject[1]: subject[0] for subject in subjects_data}

        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(page_frame,
                text="Edit Exam Details",
                font=("Segoe UI", 24, "bold"),
                foreground=self.colors['text']).pack(pady=(0, 20))

        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        fields = {
            "Title": current_title,
            "Duration": current_duration
        }
        entries = {}

        # Title and Duration entry fields
        for field, value in fields.items():
            row = ttk.Frame(form_frame)
            row.pack(fill='x', pady=5)

            label = ttk.Label(row, text=field + ":", font=("Segoe UI", 12), foreground=self.colors['text'], background=self.colors['content'])
            label.pack(side='left', padx=5)

            entry = ttk.Entry(row, font=("Segoe UI", 12))
            entry.insert(0, value)
            entry.pack(side='left', fill='x', expand=True, padx=5)
            entries[field] = entry

        # Subject dropdown
        row = ttk.Frame(form_frame)
        row.pack(fill='x', pady=5)

        subject_label = ttk.Label(row, text="Subject:", font=("Segoe UI", 12), foreground=self.colors['text'], background=self.colors['content'])
        subject_label.pack(side='left', padx=5)

        subject_combobox = ttk.Combobox(row, values=list(subjects_dict.keys()), state="readonly", font=("Segoe UI", 12))
        subject_combobox.set(current_subject)  # Set the current subject as default
        subject_combobox.pack(side='left', fill='x', expand=True, padx=5)

        # Save button
        save_button = ttk.Button(page_frame, text="Save Changes", 
                                command=lambda: self.save_exam_data(exam_id, entries["Title"], subject_combobox, entries["Duration"]))
        save_button.pack(pady=20)

        # Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_exams_page)
        back_button.pack(pady=10)


    def save_exam_data(self, exam_id, title_var, subject_combobox, duration_var):
        new_title = title_var.get().strip()
        new_subject_name = subject_combobox.get().strip()
        new_duration = duration_var.get().strip()

        if not new_title or not new_subject_name or not new_duration:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Get the subject ID from the dictionary
        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM subjects WHERE subject_name = ?', (new_subject_name,))
        subject_id_data = cursor.fetchone()
        conn.close()

        if not subject_id_data:
            messagebox.showerror("Error", "Invalid subject!")
            return

        new_subject_id = subject_id_data[0]

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE exams
                SET title = ?, subject_id = ?, duration = ?
                WHERE id = ?
            ''', (new_title, new_subject_id, new_duration, exam_id))

            conn.commit()
            messagebox.showinfo("Success", "Exam updated successfully!")
            self.show_exams_page()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()


    def delete_exam(self):
        selected_item = self.exam_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an exam to delete!")
            return

        exam_id = self.exam_tree.item(selected_item, 'values')[0]

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
            conn.commit()
            messagebox.showinfo("Success", "Exam deleted successfully!")
            self.refresh_exam_list()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def show_questions_page(self):
        if self.current_page == "questions":
            return
                
        self.clear_content()
        self.current_page = "questions"
        
        # Questions list section
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
        
        # Add buttons for Add, Edit, and Delete
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text="Add Question", command=self.show_add_question_page)
        add_button.pack(side='left', padx=5)
        
        edit_button = ttk.Button(button_frame, text="Edit Question", command=self.edit_question)
        edit_button.pack(side='left', padx=5)
        
        delete_button = ttk.Button(button_frame, text="Delete Question", command=self.delete_question)
        delete_button.pack(side='left', padx=5)
        
        # Load questions
        self.refresh_question_list()


    def refresh_question_list(self):
        # Connect to the database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        # Fetch questions data
        cursor.execute('''
        SELECT questions.id, exams.title, questions.question, questions.correct_answer
        FROM questions
        JOIN exams ON questions.exam_id = exams.id
        ''')
        questions = cursor.fetchall()

        # Clear the existing items in the Treeview
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)

        # Insert the fetched data into the Treeview
        for question in questions:
            self.question_tree.insert('', 'end', values=question)

        # Close the database connection
        conn.close()

    def show_add_question_page(self):
        self.clear_content()  # Clear the current content before showing Add Question page
        self.current_page = "add_question"

        # Create add question page content
        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(page_frame,
                text="Add New Question",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content']).pack(pady=(0, 20))

        # Input fields
        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        # Exam selection
        exam_frame = ttk.Frame(form_frame, style="Card.TFrame")
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
        question_frame = ttk.Frame(form_frame, style="Card.TFrame")
        question_frame.pack(fill='x', pady=10)
        ttk.Label(question_frame,
                text="Question:",
                style="Card.TLabel").pack(anchor='w', padx=(0, 10))
        self.question_text = tk.Text(question_frame, height=3, width=50)
        self.question_text.pack(fill='x', pady=5)
        
        # Options
        options_frame = ttk.Frame(form_frame, style="Card.TFrame")
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
        answer_frame = ttk.Frame(form_frame, style="Card.TFrame")
        answer_frame.pack(fill='x', pady=10)
        ttk.Label(answer_frame,
                text="Correct Answer:",
                style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.correct_var = tk.StringVar()
        for i, label in enumerate(option_labels):
            ttk.Radiobutton(answer_frame,
                            text=label,
                            variable=self.correct_var,
                            value=label,  # Use the string value directly
                            style="Custom.TRadiobutton").pack(side='left', padx=10)
        
        # Add button
        add_button = ttk.Button(page_frame, text="Add", command=lambda: self.add_question_to_database(self.exam_var, self.question_text, self.option_entries, self.correct_var))
        add_button.pack(pady=20)

        # Back button
        back_button = ttk.Button(page_frame, text="Back", command=self.show_questions_page)  # Going back to question list
        back_button.pack(pady=10)
            

    def add_question_to_database(self, exam_var, question_text, option_entries, correct_var):
        exam_id = exam_var.get().split('-')[0].strip()
        question = question_text.get("1.0", tk.END).strip()
        options = [entry.get().strip() for entry in option_entries]
        correct = correct_var.get()
        
        if not exam_id or not question or not all(options) or not correct:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO questions (exam_id, question, option_a, option_b, option_c, option_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (exam_id, question, options[0], options[1], options[2], options[3], correct))  # Insert options and correct answer as strings

            conn.commit()
            messagebox.showinfo("Success", "Question added successfully!")
            self.show_questions_page()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()


    def edit_question(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to edit!")
            return

        question_id = self.question_tree.item(selected_item, 'values')[0]
        self.show_edit_question_page(question_id)
    
    def get_exam_title(self, exam_id):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        cursor.execute("SELECT title FROM exams WHERE id = ?", (exam_id,))
        exam_title = cursor.fetchone()

        conn.close()

        return exam_title[0] if exam_title else "Unknown Exam"


    def show_edit_question_page(self, question_id):
        self.clear_content()
        self.current_page = "edit_question"

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT exam_id, question, option_a, option_b, option_c, option_d, correct_answer
            FROM questions
            WHERE id = ?
        ''', (question_id,))
        question_data = cursor.fetchone()
        conn.close()

        if not question_data:
            messagebox.showerror("Error", "Question not found!")
            return

        exam_id, current_question, option_a, option_b, option_c, option_d, current_correct = question_data

        page_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        page_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(page_frame,
                text="Edit Question",
                font=("Segoe UI", 24, "bold"),
                foreground=self.colors['text']).pack(pady=(0, 20))

        form_frame = ttk.Frame(page_frame, style="Content.TFrame")
        form_frame.pack(pady=20)

        # Exam selection
        exam_frame = ttk.Frame(form_frame, style="Card.TFrame")
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

        self.exam_var.set(f"{exam_id} - {self.get_exam_title(exam_id)}")

        # Question text
        question_frame = ttk.Frame(form_frame, style="Card.TFrame")
        question_frame.pack(fill='x', pady=10)
        ttk.Label(question_frame,
                text="Question:",
                style="Card.TLabel").pack(anchor='w', padx=(0, 10))
        self.question_text = tk.Text(question_frame, height=3, width=50)
        self.question_text.insert('1.0', current_question)
        self.question_text.pack(fill='x', pady=5)
        
        # Options
        options_frame = ttk.Frame(form_frame, style="Card.TFrame")
        options_frame.pack(fill='x', pady=10)
        
        self.option_entries = []
        option_labels = ['A', 'B', 'C', 'D']
        options = [option_a, option_b, option_c, option_d]
        
        for i, (label, option) in enumerate(zip(option_labels, options)):
            option_frame = ttk.Frame(options_frame, style="Card.TFrame")
            option_frame.pack(fill='x', pady=5)
            ttk.Label(option_frame,
                    text=f"Option {label}:",
                    style="Card.TLabel").pack(side='left', padx=(0, 10))
            entry = ttk.Entry(option_frame, width=50)
            entry.insert(0, option)
            entry.pack(side='left', fill='x', expand=True)
            self.option_entries.append(entry)
        
        # Correct answer
        answer_frame = ttk.Frame(form_frame, style="Card.TFrame")
        answer_frame.pack(fill='x', pady=10)
        ttk.Label(answer_frame,
                text="Correct Answer:",
                style="Card.TLabel").pack(side='left', padx=(0, 10))
        self.correct_var = tk.StringVar()
        for i, label in enumerate(option_labels):
            ttk.Radiobutton(answer_frame,
                        text=label,
                        variable=self.correct_var,
                        value=label,
                        style="Custom.TRadiobutton").pack(side='left', padx=10)

        self.correct_var.set(current_correct)
        
        # Save button
        save_button = ttk.Button(page_frame, text="Save Changes", 
                                command=lambda: self.save_question_data(question_id, self.exam_var, self.question_text, self.option_entries, self.correct_var))
        save_button.pack(pady=20)

        back_button = ttk.Button(page_frame, text="Back", command=self.show_questions_page)
        back_button.pack(pady=10)

    def save_question_data(self, question_id, exam_var, question_text, option_entries, correct_var):
        exam_id = exam_var.get().split('-')[0].strip()
        new_question = question_text.get("1.0", tk.END).strip()
        new_options = [entry.get().strip() for entry in option_entries]
        new_correct = correct_var.get()

        if not exam_id or not new_question or not all(new_options) or not new_correct:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE questions
                SET exam_id = ?, question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_answer = ?
                WHERE id = ?
            ''', (exam_id, new_question, new_options[0], new_options[1], new_options[2], new_options[3], new_correct, question_id))

            conn.commit()
            messagebox.showinfo("Success", "Question updated successfully!")
            self.show_questions_page()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def delete_question(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a question to delete!")
            return

        question_id = self.question_tree.item(selected_item, 'values')[0]

        conn = sqlite3.connect("exam_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
            conn.commit()
            messagebox.showinfo("Success", "Question deleted successfully!")
            self.refresh_question_list()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def refresh_exam_dropdown(self):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM exams")
        exams = cursor.fetchall()
        conn.close()

        self.exam_dropdown['values'] = [f"{exam[0]} - {exam[1]}" for exam in exams]
        
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
        
    def refresh_results_list(self):
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, u.name, e.title, r.score, r.date
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN users u ON s.id = u.id  -- Join with users table to get the student name
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

    def logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Create new main window
            root = tk.Tk()
            from main import UserTypeSelection
            UserTypeSelection(root)
            root.mainloop()