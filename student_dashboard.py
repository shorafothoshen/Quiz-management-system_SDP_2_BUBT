import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from PIL import Image, ImageTk
class StudentDashboard:
    def __init__(self, root, student_id, login_window):
        self.root = root
        self.student_id = student_id
        self.login_window = login_window
        self.root.title("Student Dashboard")
        self.current_page = None
        
        # Initialize database tables
        self.init_database()
        
        # Configure the window
        self.root.state('zoomed')  # Maximize window
        
        # Configure colors
        self.colors = {
            'bg_dark': '#0B1437',       # Dark blue background
            'menu_bg': '#1B2B65',       # Slightly lighter blue for menu
            'content_bg': '#0B1437',    # Main content background
            'accent1': '#6C72FF',       # Purple accent
            'accent2': '#00D8D8',       # Cyan accent
            'text': '#FFFFFF',          # White text
            'text_secondary': '#A0AEC0', # Secondary text color
            'hover': '#2A3F7E',         # Hover state color
            'selected': '#2A3F7E',      # Selected row color
            'primary': '#1B2B65'        # Primary color
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure widget styles
        self.style.configure("Menu.TFrame", 
                           background=self.colors['menu_bg'])
        self.style.configure("Content.TFrame", 
                           background=self.colors['content_bg'])
        self.style.configure("MenuButton.TButton",
                           background=self.colors['menu_bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11),
                           borderwidth=0,
                           padding=(20, 15))
        self.style.map("MenuButton.TButton",
                      background=[('active', self.colors['hover'])],
                      foreground=[('active', self.colors['accent1'])])
        
        # Configure Treeview style to match teacher dashboard
        self.style.configure("Timeline.Treeview",
                           background=self.colors['content_bg'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['content_bg'],
                           borderwidth=0,
                           font=('Segoe UI', 10))
        self.style.configure("Timeline.Treeview.Heading",
                           background=self.colors['menu_bg'],
                           foreground=self.colors['text'],
                           borderwidth=0,
                           font=('Segoe UI', 11, 'bold'))
        self.style.map('Timeline.Treeview',
                      background=[('selected', self.colors['selected'])],
                      foreground=[('selected', self.colors['text'])])
        
        # Main container
        self.main_container = ttk.Frame(root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)
        
        # Create left menu
        self.menu_frame = ttk.Frame(self.main_container, style="Menu.TFrame", width=250)
        self.menu_frame.pack(side='left', fill='y')
        self.menu_frame.pack_propagate(False)
        
        # Dashboard header in menu
        header_frame = ttk.Frame(self.menu_frame, style="Menu.TFrame")
        header_frame.pack(fill='x', pady=(30, 20), padx=20)
        
        ttk.Label(header_frame, 
                 text="Student Portal",
                 font=('Segoe UI', 20, 'bold'),
                 foreground=self.colors['text'],
                 background=self.colors['menu_bg']).pack(anchor='w')
        
        ttk.Label(header_frame,
                 text="Manage your exams and results",
                 font=('Segoe UI', 10),
                 foreground=self.colors['text_secondary'],
                 background=self.colors['menu_bg']).pack(anchor='w', pady=(5,0))
        
        # Menu items with icons
        self.create_menu_button("📝 Available Exams", self.show_available_exams)
        self.create_menu_button("📊 My Results", self.show_results)
        self.create_menu_button("👤 My Profile", self.show_profile)
        
        # Get student info for profile section (with additional details)
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        # Fetch student info from both users and students tables
        cursor.execute('''
        SELECT u.name, u.email,s.class, s.phone, s.profile_pic, s.bio 
        FROM users u
        JOIN students s ON u.id = s.id
        WHERE u.id = ?
        ''', (student_id,))

        self.student_info = cursor.fetchone()

        conn.close()

        
        # Profile section at bottom of menu
        profile_frame = ttk.Frame(self.menu_frame, style="Menu.TFrame")
        profile_frame.pack(side='bottom', fill='x', pady=20, padx=20)
        
        ttk.Label(profile_frame,
                 text=self.student_info[0],
                 font=('Segoe UI', 12, 'bold'),
                 foreground=self.colors['text'],
                 background=self.colors['menu_bg']).pack(anchor='w')
        
        ttk.Label(profile_frame,
                 text=f"Class {self.student_info[1]}",
                 font=('Segoe UI', 10),
                 foreground=self.colors['text_secondary'],
                 background=self.colors['menu_bg']).pack(anchor='w')
        
        ttk.Button(profile_frame,
                  text="🚪 Logout",
                  style="MenuButton.TButton",
                  command=self.logout).pack(fill='x', pady=(10,0))
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(side='left', fill='both', expand=True, padx=30, pady=30)
        
        # Initialize with available exams view
        self.show_available_exams()
        
    
    def create_menu_button(self, text, command):
        btn = ttk.Button(self.menu_frame,
                        text=text,
                        style="MenuButton.TButton",
                        command=command)
        btn.pack(fill='x', pady=2, padx=20)
        return btn
    
    def clear_current_page(self):
        if self.current_page and self.current_page.winfo_exists():
            self.current_page.destroy()
        self.current_page = None

    def show_dashboard(self):
        self.clear_current_page()
        self.current_page = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.current_page.pack(fill='both', expand=True)
        
        # Add dashboard content
        welcome_label = ttk.Label(
            self.current_page,
            text="Welcome to Your Dashboard",
            style="Title.TLabel"
        )
        welcome_label.pack(pady=20)

        # Fetch student information
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Corrected query to fetch student information
            cursor.execute("""
            SELECT u.name, s.class 
            FROM users u
            JOIN students s ON u.id = s.id
            WHERE u.id = ?
            """, (self.student_id,))

            student_info = cursor.fetchone()
            
            if student_info:
                info_frame = ttk.Frame(self.current_page, style="Card.TFrame")
                info_frame.pack(fill='x', padx=20, pady=10)
                
                ttk.Label(
                    info_frame,
                    text=f"Name: {student_info[0]}",
                    style="Card.TLabel"
                ).pack(pady=5)
                
                ttk.Label(
                    info_frame,
                    text=f"Class: {student_info[1]}",
                    style="Card.TLabel"
                ).pack(pady=5)

            # Timeline section
            timeline_frame = ttk.Frame(self.current_page, style="Card.TFrame")
            timeline_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            ttk.Label(
                timeline_frame,
                text="Upcoming Exams",
                style="Title.TLabel"
            ).pack(pady=10)

            # Create Treeview for exams
            columns = ('Title', 'Subject', 'Duration', 'Total Marks')
            self.timeline_tree = ttk.Treeview(timeline_frame, columns=columns, show='headings', style="Timeline.Treeview")
            
            # Configure columns
            for col in columns:
                self.timeline_tree.heading(col, text=col)
                self.timeline_tree.column(col, width=150)
            
            self.timeline_tree.pack(fill='both', expand=True, padx=10, pady=5)
            
            try:
                # Fetch and display upcoming exams
                cursor.execute("""
                SELECT e.title, e.subject, e.duration, e.total_marks
                FROM exams e
                WHERE e.id NOT IN (
                    SELECT r.exam_id
                    FROM results r
                    WHERE r.student_id = ?
                )
                """, (self.student_id,))
                
                upcoming_exams = cursor.fetchall()
                
                if upcoming_exams:
                    for exam in upcoming_exams:
                        self.timeline_tree.insert('', 'end', values=exam)
                else:
                    self.timeline_tree.insert('', 'end', values=('No upcoming exams', '', '', ''))
                    
            except sqlite3.OperationalError:
                self.timeline_tree.insert('', 'end', values=('No exams available', '', '', ''))
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    
    def show_available_exams(self):
        self.clear_current_page()
        self.current_page = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.current_page.pack(fill='both', expand=True)
        
        # Header with title
        header_frame = ttk.Frame(self.current_page, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="Available Exams",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(side='left')
        
        # Create Treeview for exams
        columns = ('ID', 'Title', 'Subject', 'Duration (min)')
        self.exam_tree = ttk.Treeview(
            self.current_page,
            columns=columns,
            show='headings',
            style="Timeline.Treeview",
            height=15
        )
        
        # Configure style for Treeview
        style = ttk.Style()
        style.configure("Timeline.Treeview",
            background=self.colors['content_bg'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['content_bg'],
            rowheight=30
        )
        style.configure("Timeline.Treeview.Heading",
            background=self.colors['primary'],
            foreground=self.colors['text'],
            relief="flat"
        )
        style.map("Timeline.Treeview",
            background=[('selected', self.colors['primary'])],
            foreground=[('selected', self.colors['text'])]
        )
        
        # Configure columns
        column_widths = {
            'ID': 80,
            'Title': 300,
            'Subject': 200,
            'Duration (min)': 150
        }
        
        for col, width in column_widths.items():
            self.exam_tree.heading(col, text=col)
            self.exam_tree.column(col, width=width, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.current_page, orient='vertical', command=self.exam_tree.yview)
        self.exam_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the Treeview and scrollbar
        self.exam_tree.pack(side='left', fill='both', expand=True, padx=20)
        scrollbar.pack(side='right', fill='y')
        
        # Add Start Exam button
        button_frame = ttk.Frame(self.current_page, style="Content.TFrame")
        button_frame.pack(fill='x', pady=20, padx=20)
        
        ttk.Button(
            button_frame,
            text="Start Selected Exam",
            style="MenuButton.TButton",
            command=self.start_exam
        ).pack(side='right')
        
        # Fetch and display available exams
        self.refresh_available_exams()
        
        # Bind double-click event
        self.exam_tree.bind('<Double-1>', lambda e: self.start_exam())
    
    def refresh_available_exams(self):
        # Clear existing items
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Get exams that student hasn't taken yet
            cursor.execute("""
                SELECT e.id, e.title, s.subject_name, e.duration
                FROM exams e
                JOIN subjects s ON e.subject_id = s.id
                WHERE e.id NOT IN (
                    SELECT exam_id FROM results WHERE student_id = ?
                )
                ORDER BY e.id DESC
            """, (self.student_id,))
            
            exams = cursor.fetchall()
            
            if not exams:
                # If no available exams, show this message
                self.exam_tree.insert('', 'end', values=(
                    "-",
                    "No available exams",
                    "-",
                    "-"
                ))
                return
            
            # Insert available exams into the tree
            for exam in exams:
                exam_id, title, subject_name, duration = exam
                self.exam_tree.insert('', 'end', values=(
                    exam_id,
                    title,
                    subject_name,
                    duration
                ))
        
        except sqlite3.Error as e:
            # Display a message box if a database error occurs
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()


    def show_results(self):
        if self.current_page == "results":
            return
            
        self.clear_current_page()
        self.current_page = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.current_page.pack(fill='both', expand=True)
        
        # Header frame
        header_frame = ttk.Frame(self.current_page, style="Content.TFrame")
        header_frame.pack(fill='x', padx=20, pady=(20,10))
        
        # Title on the left
        ttk.Label(
            header_frame,
            text="Exam Results",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(side='left')
        
        # Print Report button on the right
        ttk.Button(
            header_frame,
            text="Print Progress Report",
            style="Custom.TButton",
            command=self.generate_progress_report
        ).pack(side='right', padx=10)

        # Create a frame for the results list
        results_frame = ttk.Frame(self.current_page, style="Content.TFrame")
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Create Treeview with columns matching teacher dashboard
        columns = ('ID', 'Student', 'Exam', 'Score (%)', 'Date')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', style="Timeline.Treeview")
        
        # Configure column headings
        self.results_tree.heading('ID', text='ID')
        self.results_tree.heading('Student', text='Student')
        self.results_tree.heading('Exam', text='Exam')
        self.results_tree.heading('Score (%)', text='Score (%)')
        self.results_tree.heading('Date', text='Date')
        
        # Configure column widths
        self.results_tree.column('ID', width=50)
        self.results_tree.column('Student', width=200)
        self.results_tree.column('Exam', width=200)
        self.results_tree.column('Score (%)', width=100)
        self.results_tree.column('Date', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the Treeview and scrollbar
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Fetch exam results from database
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.id, u.name, e.title, r.score, r.date
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN exams e ON r.exam_id = e.id
                JOIN users u ON s.id = u.id  -- Join with users table to get the name
                WHERE r.student_id = ?
                ORDER BY r.date DESC
            """, (self.student_id,))
            
            results = cursor.fetchall()
            if results:
                for result in results:
                    # Format the date to match the teacher dashboard
                    date_obj = datetime.strptime(result[4], '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Insert data into treeview
                    self.results_tree.insert('', 'end', values=(
                        result[0],  # ID
                        result[1],  # Student Name
                        result[2],  # Exam Title
                        f"{result[3]:.2f}",  # Score with 2 decimal places
                        formatted_date  # Formatted Date
                    ))
            else:
                self.results_tree.insert('', 'end', values=('--', 'No results available', '--', '--', '--'))
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Error", "Failed to fetch results from database")
            self.results_tree.insert('', 'end', values=('--', 'Error loading results', '--', '--', '--'))
        finally:
            conn.close()

    def refresh_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT e.title, r.score, r.date
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                WHERE r.student_id = ?
                ORDER BY r.date DESC
            """, (self.student_id,))
            self.results = cursor.fetchall()  # Store results for PDF generation
            
            if self.results:
                for result in self.results:
                    completion_date = datetime.strptime(result[2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                    self.results_tree.insert('', 'end', values=(
                        result[0],
                        result[1],
                        result[2],
                        completion_date
                    ))
            else:
                self.results_tree.insert('', 'end', values=('No results available', '', '', ''))
                
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()
    
    def show_profile(self):
        self.clear_current_page()
        self.current_page = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.current_page.pack(fill='both', expand=True)
        
        # Create a main container for profile content
        profile_container = ttk.Frame(self.current_page, style="Content.TFrame")
        profile_container.pack(padx=50, pady=20, fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(profile_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame,
                text="My Profile",
                font=('Segoe UI', 24, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content_bg']).pack(side='left')
        
        # Edit button
        ttk.Button(header_frame,
                text="✏️ Edit Profile",
                style="Custom.TButton",
                command=self.edit_profile).pack(side='right')
        
        # Create two columns
        columns_frame = ttk.Frame(profile_container, style="Content.TFrame")
        columns_frame.pack(fill='both', expand=True)
        
        # Left column - Profile Picture
        left_column = ttk.Frame(columns_frame, style="Card.TFrame")
        left_column.pack(side='left', padx=(0, 20), fill='both')
        
        # Profile picture frame with border
        pic_frame = ttk.Frame(left_column, style="Card.TFrame")
        pic_frame.pack(pady=20, padx=20)
        
        # Try to load and display profile picture
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        # Fetch profile picture from `students` table based on logged-in user
        cursor.execute("""
            SELECT students.profile_pic 
            FROM students 
            JOIN users ON students.id = users.id
            WHERE users.id = ?
        """, (self.student_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            try:
                image_data = io.BytesIO(result[0])
                pil_image = Image.open(image_data)
                target_size = (200, 200)
                pil_image.thumbnail(target_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                self.profile_photo = photo
                image_label = ttk.Label(pic_frame, image=photo, background=self.colors['menu_bg'])
                image_label.pack(padx=10, pady=10)
            except Exception as e:
                ttk.Label(pic_frame,
                        text="👤",
                        font=('Segoe UI', 48),
                        foreground=self.colors['text'],
                        background=self.colors['menu_bg']).pack(padx=40, pady=40)
        else:
            ttk.Label(pic_frame,
                    text="👤",
                    font=('Segoe UI', 48),
                    foreground=self.colors['text'],
                    background=self.colors['menu_bg']).pack(padx=40, pady=40)
        
        conn.close()
        
        ttk.Button(left_column,
                text="Upload Photo",
                style="Custom.TButton",
                command=self.upload_profile_pic).pack(pady=10)
        
        # Right column - Profile Information
        right_column = ttk.Frame(columns_frame, style="Card.TFrame")
        right_column.pack(side='left', fill='both', expand=True)
        
        # Fetch profile data
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT users.name, students.class, users.email, students.phone, students.bio 
                FROM students 
                JOIN users ON students.id = users.id
                WHERE users.id = ?
            """, (self.student_id,))
            student_info = cursor.fetchone()
            
            if student_info:
                info_frame = ttk.Frame(right_column, style="Card.TFrame")
                info_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                def create_info_row(label_text, value, row):
                    ttk.Label(info_frame,
                            text=label_text,
                            font=('Segoe UI', 12, 'bold'),
                            foreground=self.colors['text_secondary'],
                            background=self.colors['menu_bg']).grid(row=row, column=0, sticky='w', pady=10)
                    
                    ttk.Label(info_frame,
                            text=value if value else "Not set",
                            font=('Segoe UI', 12),
                            foreground=self.colors['text'],
                            background=self.colors['menu_bg']).grid(row=row, column=1, sticky='w', padx=20, pady=10)
                
                create_info_row("Full Name:", student_info[0], 0)
                create_info_row("Class:", student_info[1], 1)
                create_info_row("Email:", student_info[2], 2)
                create_info_row("Phone:", student_info[3], 3)
                
                ttk.Label(info_frame,
                        text="About Me:",
                        font=('Segoe UI', 12, 'bold'),
                        foreground=self.colors['text_secondary'],
                        background=self.colors['menu_bg']).grid(row=4, column=0, sticky='w', pady=(20,10))
                
                bio_text = student_info[4] if student_info[4] else "No bio added yet."
                ttk.Label(info_frame,
                        text=bio_text,
                        font=('Segoe UI', 12),
                        foreground=self.colors['text'],
                        background=self.colors['menu_bg'],
                        wraplength=400).grid(row=5, column=0, columnspan=2, sticky='w', pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()

    
    def edit_profile(self):
        # Create a new top-level window for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")
        edit_window.configure(bg=self.colors['content_bg'])

        # Center the window
        window_width = 500
        window_height = 600
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Main container
        main_frame = ttk.Frame(edit_window, style="Content.TFrame")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        ttk.Label(main_frame,
                text="Edit Profile",
                font=('Segoe UI', 20, 'bold'),
                foreground=self.colors['text'],
                background=self.colors['content_bg']).pack(pady=(0, 20))

        # Form frame
        form_frame = ttk.Frame(main_frame, style="Card.TFrame")
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Get current profile data
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT users.name, students.class, users.email, students.phone, students.bio
                FROM students
                JOIN users ON students.id = users.id
                WHERE students.id = ?
            """, (self.student_id,))
            student_info = cursor.fetchone()
        finally:
            conn.close()

        # Create form fields
        def create_field(label_text, row, default_value="", is_text_area=False):
            ttk.Label(form_frame,
                    text=label_text,
                    font=('Segoe UI', 11),
                    foreground=self.colors['text'],
                    background=self.colors['menu_bg']).grid(row=row, column=0, sticky='w', pady=(10, 5))

            if is_text_area:
                text_widget = tk.Text(form_frame, height=4, width=40)
                text_widget.grid(row=row + 1, column=0, sticky='ew', pady=(0, 10))
                text_widget.insert('1.0', default_value if default_value else "")
                return text_widget
            else:
                var = tk.StringVar(value=default_value if default_value else "")
                entry = ttk.Entry(form_frame, textvariable=var, width=40)
                entry.grid(row=row + 1, column=0, sticky='ew', pady=(0, 10))
                return var

        # Create form fields with current values
        name_var = create_field("Full Name", 0, student_info[0])
        class_var = create_field("Class", 2, student_info[1])
        email_var = create_field("Email", 4, student_info[2])
        phone_var = create_field("Phone", 6, student_info[3])
        bio_text = create_field("About Me", 8, student_info[4], True)

        def save_changes():
            try:
                conn = sqlite3.connect('exam_system.db')
                cursor = conn.cursor()

                # Update the `users` table
                cursor.execute("""
                    UPDATE users
                    SET name = COALESCE(?, name), email = COALESCE(?, email)
                    WHERE id = (
                        SELECT id FROM students WHERE id = ?
                    )
                """, (
                    name_var.get() if name_var.get().strip() else None,
                    email_var.get() if email_var.get().strip() else None,
                    self.student_id
                ))

                # Update the `students` table
                cursor.execute("""
                    UPDATE students
                    SET class = COALESCE(?, class), phone = COALESCE(?, phone), bio = COALESCE(?, bio)
                    WHERE id = ?
                """, (
                    class_var.get() if class_var.get().strip() else None,
                    phone_var.get() if phone_var.get().strip() else None,
                    bio_text.get('1.0', 'end-1c').strip() if bio_text.get('1.0', 'end-1c').strip() else None,
                    self.student_id
                ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Profile updated successfully!")
                edit_window.destroy()
                self.show_profile()  # Refresh the profile view
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update profile: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(main_frame, style="Content.TFrame")
        button_frame.pack(fill='x', pady=(10, 0), anchor='n')  # Adjust padding for better positioning

        # Add buttons with proper alignment
        cancel_button = ttk.Button(button_frame,
                                    text="Cancel",
                                    style="Custom.TButton",
                                    command=edit_window.destroy)
        cancel_button.pack(side="left", padx=(50, 10), pady=5)  # Left aligned

        save_button = ttk.Button(button_frame,
                                text="Save Changes",
                                style="Custom.TButton",
                                command=save_changes)
        save_button.pack(side="right", padx=(10, 50), pady=5)  # Right aligned

    def upload_profile_pic(self):
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                # Open and resize image before saving
                with Image.open(file_path) as img:
                    # Resize image while maintaining aspect ratio
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    
                    # Convert image to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format)
                    img_byte_arr = img_byte_arr.getvalue()
                
                conn = sqlite3.connect('exam_system.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET profile_pic=? WHERE id=?",
                             (img_byte_arr, self.student_id))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Profile picture updated successfully!")
                self.show_profile()  # Refresh the profile view
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload profile picture: {str(e)}")
    
    def refresh_exam_list(self):
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            # Get exams that student hasn't taken yet
            cursor.execute("""
                SELECT 
                    id,
                    title,
                    subject,
                    duration
                FROM exams 
                WHERE id NOT IN (
                    SELECT exam_id FROM results WHERE student_id = ?
                )
            """, (self.student_id,))

            for exam in cursor.fetchall():
                self.exam_tree.insert("", "end", values=exam)
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    
    def refresh_timeline(self):
        for item in self.timeline.get_children():
            self.timeline.delete(item)

        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT e.date, e.subject, e.title, e.duration
                FROM exams e
                WHERE e.id IN (
                    SELECT exam_id FROM results WHERE student_id = ?
                )
            """, (self.student_id,))

            for exam in cursor.fetchall():
                self.timeline.insert("", "end", values=exam)
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()
    
    def start_exam(self):
        selection = self.exam_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an exam")
            return

        exam_id = self.exam_tree.item(selection[0])['values'][0]
        
        # Check if there are any questions for the selected exam
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions WHERE exam_id = ?", (exam_id,))
        question_count = cursor.fetchone()[0]
        conn.close()
        
        if question_count == 0:
            messagebox.showwarning("No Questions", "There are no questions for the selected exam.")
            return
        
        # Hide the dashboard window
        self.root.withdraw()
        
        # Create exam window
        exam_window = tk.Toplevel()
        from exam_interface import ExamInterface
        exam = ExamInterface(exam_window, self.student_id, exam_id)
        
        # When exam window is closed, show dashboard and refresh
        exam_window.protocol("WM_DELETE_WINDOW", 
                            lambda: [exam_window.destroy(), 
                                    self.root.deiconify(),
                                    self.refresh_exam_list(),
                                    self.refresh_results()])

    def init_database(self):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, -- Encrypted password
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT CHECK(role IN ('Admin', 'Teacher', 'Student')) NOT NULL
            )
        ''')

        # Create students table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                class TEXT NOT NULL,
                phone TEXT,
                profile_pic BLOB,
                bio TEXT,
                FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # Create exams table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                duration INTEGER NOT NULL,
                total_marks INTEGER NOT NULL
            )
        ''')

        # Create results table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                exam_id INTEGER,
                score INTEGER,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (exam_id) REFERENCES exams(id)
            )
        ''')

        conn.commit()
        conn.close()

    def generate_progress_report(self):
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Get student information
            cursor.execute("""
                SELECT name, class, email
                FROM students 
                JOIN users ON students.id = users.id -- Ensure students join with users to get name and email
                WHERE students.id = ?
            """, (self.student_id,))
            student_info = cursor.fetchone()
            
            # Get exam results
            cursor.execute("""
                SELECT e.title, r.score, r.date
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                WHERE r.student_id = ?
                ORDER BY r.date DESC
            """, (self.student_id,))
            results = cursor.fetchall()
            
            if not results:
                messagebox.showinfo("Info", "No results available to generate report.")
                return
                
            # Ask user where to save the PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Progress Report"
            )
            
            if not file_path:
                return
                
            # Create the PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Prepare the elements list
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'Heading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceBefore=6,
                spaceAfter=6
            )
            
            # Add header
            elements.append(Paragraph("Student Progress Report", title_style))
            elements.append(Spacer(1, 20))
            
            # Add student information
            elements.append(Paragraph("Student Information", heading_style))
            elements.append(Paragraph(f"Name: {student_info[0]}", normal_style))
            elements.append(Paragraph(f"Class: {student_info[1]}", normal_style))
            if student_info[2]:  # If email exists
                elements.append(Paragraph(f"Email: {student_info[2]}", normal_style))
            elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Add performance summary
            elements.append(Paragraph("Performance Summary", heading_style))
            
            # Calculate basic statistics
            total_exams = len(results)
            average_score = sum(result[1] for result in results) / total_exams if total_exams > 0 else 0
            
            # Add summary statistics
            elements.append(Paragraph(f"Total Exams Taken: {total_exams}", normal_style))
            elements.append(Paragraph(f"Average Score: {average_score:.2f}", normal_style))
            
            # Create exam results table
            elements.append(Paragraph("Detailed Exam Results", heading_style))
            
            # Table header
            table_data = [['Exam Title', 'Score', 'Date']]
            
            # Add exam data
            for result in results:
                date = datetime.strptime(result[2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                table_data.append([
                    result[0],  # Exam title
                    str(result[1]),  # Score
                    date  # Formatted date
                ])
            
            # Create and style the table
            table = Table(table_data, colWidths=[250, 100, 150])
            table.setStyle(TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B2B65')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Data style
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            
            elements.append(table)
            
            # Add performance analysis
            elements.append(Paragraph("Performance Analysis", heading_style))
            
            # Calculate and add performance metrics
            highest_score = max(result[1] for result in results)
            lowest_score = min(result[1] for result in results)
            
            elements.append(Paragraph(f"Highest Score: {highest_score}", normal_style))
            elements.append(Paragraph(f"Lowest Score: {lowest_score}", normal_style))
            elements.append(Paragraph(f"Average Score: {average_score:.2f}", normal_style))
            
            # Build the PDF
            doc.build(elements)
            messagebox.showinfo("Success", "Progress report has been generated successfully!")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Error", "Failed to generate progress report due to database error")
        except Exception as e:
            print(f"Error generating report: {e}")
            messagebox.showerror("Error", f"Failed to generate progress report: {str(e)}")
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
