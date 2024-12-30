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
        self.questions = []
        self.answers = {}
        self.current_question = 0
        self.timer_active = False
        self.exam_id = None
        self.exam_title = None
        self.duration = None
        
        # Initialize database tables
        self.init_database()
        
        # Configure the window
        self.root.state('zoomed')  # Maximize window
        
        # Configure the window
        self.root.title("Exam Interface")
        self.root.state('zoomed')  # Maximize window

    # Include the remaining methods and logic as provided...

        # Configure colors and styles
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
            'primary': '#1B2B65',       # Primary color
            'success': '#4CAF50',       # Success color (green)
            'error': '#F44336',         # Error color (red)
            'warning': '#FFA726'        # Warning color (orange)
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
        
        # Create main content frame
        self.content_frame = ttk.Frame(self.root, style="Content.TFrame")
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Setup menu
        self.setup_menu()
        
        # Show available exams by default
        self.show_available_exams()
        
        # Initialize database tables
        self.init_database()
        
        # Configure the window
        self.root.state('zoomed')  # Maximize window
        
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
        
    def setup_menu(self):
        """Set up the menu buttons"""
        self.menu_frame = ttk.Frame(self.root, style="Menu.TFrame")
        self.menu_frame.pack(side='left', fill='y')
        
        # Configure menu frame background
        self.menu_frame.configure(style='Menu.TFrame')
        
        # Available Exams button
        ttk.Button(
            self.menu_frame,
            text="Available Exams",
            style="MenuButton.TButton",
            command=self.show_available_exams
        ).pack(fill='x', padx=10, pady=5)
        
        # My Results button
        ttk.Button(
            self.menu_frame,
            text="My Results",
            style="MenuButton.TButton",
            command=self.show_results
        ).pack(fill='x', padx=10, pady=5)
        
        # Profile button
        ttk.Button(
            self.menu_frame,
            text="My Profile",
            style="MenuButton.TButton",
            command=self.show_profile
        ).pack(fill='x', padx=10, pady=5)
        
    def clear_content(self):
        """Clear all widgets from the content frame"""
        # Destroy all widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Reset the frame's size and position
        self.content_frame.pack_configure(fill='both', expand=True)

    def show_available_exams(self):
        """Show available exams and refresh the list"""
        # Clear everything first
        self.clear_content()
        
        """Set up the exam list interface"""
        # Create main container
        main_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        main_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="Available Exams",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(side='left')
        
        # Configure Treeview style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=self.colors['menu_bg'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['menu_bg'],
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=self.colors['menu_bg'],
            foreground=self.colors['text'],
            borderwidth=1,
            font=('Segoe UI', 10, 'bold')
        )
        style.map(
            "Custom.Treeview",
            background=[('selected', self.colors['accent1'])],
            foreground=[('selected', self.colors['text'])]
        )
        
        # Create Treeview for exams
        tree_frame = ttk.Frame(main_container, style="Card.TFrame")
        tree_frame.pack(fill='both', expand=True)
        
        self.exam_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Title', 'Duration', 'Questions', 'Status'),
            show='headings',
            style='Custom.Treeview',
            height=15
        )
        
        # Configure columns
        self.exam_tree.heading('ID', text='ID')
        self.exam_tree.heading('Title', text='Title')
        self.exam_tree.heading('Duration', text='Duration (min)')
        self.exam_tree.heading('Questions', text='Questions')
        self.exam_tree.heading('Status', text='Status')
        
        self.exam_tree.column('ID', width=50, anchor='center')
        self.exam_tree.column('Title', width=300, anchor='w')
        self.exam_tree.column('Duration', width=100, anchor='center')
        self.exam_tree.column('Questions', width=100, anchor='center')
        self.exam_tree.column('Status', width=100, anchor='center')
        
        # Add scrollbar with matching colors
        scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient='vertical', 
            command=self.exam_tree.yview,
            style='Custom.Vertical.TScrollbar'
        )
        self.exam_tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure scrollbar style
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=self.colors['menu_bg'],
            arrowcolor=self.colors['text'],
            bordercolor=self.colors['menu_bg'],
            troughcolor=self.colors['content_bg']
        )
        
        self.exam_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load exams
        self.load_available_exams()
        
        # Add Start Exam button
        button_frame = ttk.Frame(main_container, style="Content.TFrame")
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(
            button_frame,
            text="Start Selected Exam",
            style="Custom.TButton",
            command=self.start_exam
        ).pack(side='right')

    def load_available_exams(self):
        # Clear existing items
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Get exams that student hasn't taken yet
            cursor.execute("""
                SELECT e.id, e.title, e.duration,
                    (SELECT COUNT(*) FROM questions q WHERE q.exam_id = e.id) as question_count
                FROM exams e
                WHERE e.id NOT IN (
                    SELECT exam_id FROM results WHERE student_id = ?
                )
            """, (self.student_id,))
            
            exams = cursor.fetchall()
            
            if not exams:
                self.exam_tree.insert('', 'end', values=(
                    "-",
                    "No available exams",
                    "-",
                    "-",
                    "-"
                ))
                return
            
            # Insert available exams into the tree
            for exam in exams:
                exam_id, title, duration, question_count = exam
                self.exam_tree.insert('', 'end', values=(
                    exam_id,
                    title,
                    duration,
                    question_count,
                    "Available"
                ))
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading exams: {str(e)}")
        finally:
            conn.close()


    def show_results(self):
        if self.current_page == "results":
            return
            
        self.clear_content()
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
        self.clear_content()
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
        """Initialize and start the exam"""
        selection = self.exam_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an exam")
            return
        
        self.exam_id = self.exam_tree.item(selection[0])['values'][0]  # Set exam_id from selection
        
        # Load exam questions
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Get exam details
            cursor.execute("SELECT title, duration FROM exams WHERE id = ?", (self.exam_id,))
            exam_info = cursor.fetchone()
            
            if not exam_info:
                messagebox.showerror("Error", "Exam not found")
                return
                
            self.exam_title = exam_info[0]
            self.duration = exam_info[1]
            
            # Get questions
            cursor.execute("""
                SELECT id, question, option_a, option_b, option_c, option_d, correct_answer
                FROM questions
                WHERE exam_id = ?
                ORDER BY RANDOM()
            """, (self.exam_id,))
            
            self.questions = cursor.fetchall()
            
            if not self.questions:
                messagebox.showwarning("No Questions", "This exam has no questions yet.")
                return
            
            # Set up exam UI
            self.setup_exam_ui()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading exam: {str(e)}")
        finally:
            conn.close()
            
    def load_questions(self):
        try:
            conn = sqlite3.connect('exam_system.db', timeout=20)
            cursor = conn.cursor()
            
            # Get exam details
            cursor.execute("""
                SELECT title, duration 
                FROM exams 
                WHERE id = ?
            """, (self.exam_id,))
            
            exam_info = cursor.fetchone()
            if not exam_info:
                messagebox.showerror("Error", "Exam not found")
                conn.close()
                return False
                
            self.exam_title = exam_info[0]
            self.duration = exam_info[1]
            self.remaining_time = self.duration * 60  # Convert to seconds
            
            # Get questions
            cursor.execute("""
                SELECT id, question, option_a, option_b, option_c, option_d, correct_answer
                FROM questions
                WHERE exam_id = ?
                ORDER BY RANDOM()
            """, (self.exam_id,))
            
            self.questions = cursor.fetchall()
            conn.close()
            
            if not self.questions:
                messagebox.showinfo("No Questions", "This exam has no questions yet.")
                return False
                
            return True
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading questions: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return False

    def setup_exam_ui(self):
        # Clear current content
        self.clear_content()
        
        # Create exam container
        exam_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        exam_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header with exam title and timer
        header_frame = ttk.Frame(exam_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text=self.exam_title,
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(side='left')
        
        self.timer_label = ttk.Label(
            header_frame,
            text="Time Remaining: --:--",
            font=('Segoe UI', 16),
            foreground=self.colors['accent2'],
            background=self.colors['content_bg']
        )
        self.timer_label.pack(side='right')
        
        # Question container
        self.question_frame = ttk.Frame(exam_container, style="Card.TFrame")
        self.question_frame.pack(fill='both', expand=True, pady=10)
        
        # Question number and text
        self.question_label = ttk.Label(
            self.question_frame,
            text="",
            font=('Segoe UI', 14),
            foreground=self.colors['text'],
            background=self.colors['menu_bg'],
            wraplength=800
        )
        self.question_label.pack(pady=20, padx=20)
        
        # Options frame
        self.options_frame = ttk.Frame(self.question_frame, style="Card.TFrame")
        self.options_frame.pack(fill='x', padx=20, pady=10)
        
        # Radio variable for options
        self.selected_option = tk.StringVar()
        
        # Navigation buttons
        nav_frame = ttk.Frame(exam_container, style="Content.TFrame")
        nav_frame.pack(fill='x', pady=20)
        
        self.prev_btn = ttk.Button(
            nav_frame,
            text="Previous",
            style="Custom.TButton",
            command=self.prev_question
        )
        self.prev_btn.pack(side='left')
        
        self.next_btn = ttk.Button(
            nav_frame,
            text="Next",
            style="Custom.TButton",
            command=self.next_question
        )
        self.next_btn.pack(side='right')
        
        self.submit_btn = ttk.Button(
            nav_frame,
            text="Submit Exam",
            style="Custom.TButton",
            command=self.submit_exam
        )
        self.submit_btn.pack(side='right', padx=10)
        
        # Start exam timer
        self.start_timer()
        
        # Show first question
        self.show_question(0)

    def start_timer(self):
        """Start the exam timer"""
        if not self.timer_active:
            self.remaining_time = self.duration * 60  # Convert minutes to seconds
            self.timer_active = True
            self.update_timer()

    def update_timer(self):
        """Update the timer display"""
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            self.timer_active = False
            return
            
        if self.timer_active and self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            try:
                self.timer_label.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
                self.remaining_time -= 1
                self.root.after(1000, self.update_timer)
            except Exception:
                self.timer_active = False
        elif self.remaining_time <= 0:
            self.timer_active = False
            messagebox.showwarning("Time's Up!", "Your time is up! Submitting exam...")
            self.submit_exam()


    def show_question(self, index):
        """Display the question at the given index"""
        if 0 <= index < len(self.questions):
            self.current_question = index
            question = self.questions[index]
            
            # Update question text
            self.question_label.config(
                text=f"Question {index + 1} of {len(self.questions)}\n\n{question[1]}"
            )
            
            # Clear previous options
            for widget in self.options_frame.winfo_children():
                widget.destroy()
            
            # Create new option buttons
            options = [
                ('A', question[2]),
                ('B', question[3]),
                ('C', question[4]),
                ('D', question[5])
            ]
            
            for opt_letter, opt_text in options:
                option_frame = ttk.Frame(self.options_frame, style="Card.TFrame")
                option_frame.pack(fill='x', pady=5)
                
                radio_btn = ttk.Radiobutton(
                    option_frame,
                    text=f"{opt_letter}. {opt_text}",
                    variable=self.selected_option,
                    value=opt_letter,
                    style="Custom.TRadiobutton"
                )
                radio_btn.pack(pady=5, padx=10, anchor='w')
            
            # Set previously selected answer if any
            if index in self.answers:
                self.selected_option.set(self.answers[index])
            else:
                self.selected_option.set('')
            
            # Update navigation buttons
            self.prev_btn.config(state='normal' if index > 0 else 'disabled')
            self.next_btn.config(state='normal' if index < len(self.questions) - 1 else 'disabled')

    def next_question(self):
        """Save current answer and move to next question"""
        self.save_answer()
        if self.current_question < len(self.questions) - 1:
            self.show_question(self.current_question + 1)

    def prev_question(self):
        """Save current answer and move to previous question"""
        self.save_answer()
        if self.current_question > 0:
            self.show_question(self.current_question - 1)

    def show_review_dialog(self):
        self.clear_content()
        
        # Main review container with proper styling
        review_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        review_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header with title
        header_frame = ttk.Frame(review_container, style="Content.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="Review Your Answers",
            font=('Segoe UI', 24, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(side='left')
        
        # Summary section with better styling
        summary_frame = ttk.Frame(review_container, style="Card.TFrame")
        summary_frame.pack(fill='x', pady=(0, 20))
        
        total = len(self.questions)
        answered = len(self.answers)
        unanswered = total - answered
        
        # Count correct and incorrect answers
        correct_answers = 0
        incorrect_answers = 0
        for question in self.questions:
            question_id = str(question[0])
            correct_answer = question[-1]
            student_answer = self.answers.get(question_id, "Not answered")
            if student_answer == correct_answer:
                correct_answers += 1
            elif student_answer != "Not answered":
                incorrect_answers += 1
        
        # Summary statistics with improved layout
        stats_frame = ttk.Frame(summary_frame, style="Card.TFrame")
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(
            stats_frame,
            text=f"Total Questions: {total}",
            font=('Segoe UI', 12),
            foreground=self.colors['text'],
            background=self.colors['menu_bg']
        ).pack(side='left', padx=20)
        
        ttk.Label(
            stats_frame,
            text=f"Answered: {answered}",
            font=('Segoe UI', 12),
            foreground=self.colors['success'],
            background=self.colors['menu_bg']
        ).pack(side='left', padx=20)
        
        ttk.Label(
            stats_frame,
            text=f"Unanswered: {unanswered}",
            font=('Segoe UI', 12),
            foreground=self.colors['error'],
            background=self.colors['menu_bg']
        ).pack(side='left', padx=20)
        
        ttk.Label(
            stats_frame,
            text=f"Correct Answers: {correct_answers}",
            font=('Segoe UI', 12),
            foreground=self.colors['success'],
            background=self.colors['menu_bg']
        ).pack(side='left', padx=20)
        
        ttk.Label(
            stats_frame,
            text=f"Incorrect Answers: {incorrect_answers}",
            font=('Segoe UI', 12),
            foreground=self.colors['error'],
            background=self.colors['menu_bg']
        ).pack(side='left', padx=20)
        
        # Split frame for correct and incorrect answers
        split_frame = ttk.Frame(review_container, style="Content.TFrame")
        split_frame.pack(fill='both', expand=True, pady=10)
        
        # Correct answers section
        correct_canvas = tk.Canvas(split_frame, bg=self.colors['content_bg'])
        correct_scrollbar = ttk.Scrollbar(split_frame, orient="vertical", command=correct_canvas.yview)
        correct_frame = ttk.Frame(correct_canvas, style="SuccessCard.TFrame")
        
        correct_frame.bind(
            "<Configure>",
            lambda e: correct_canvas.configure(scrollregion=correct_canvas.bbox("all"))
        )
        
        correct_canvas.create_window((0, 0), window=correct_frame, anchor="nw")
        correct_canvas.configure(yscrollcommand=correct_scrollbar.set)
        
        correct_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        correct_scrollbar.pack(side="left", fill="y")
        
        # Incorrect answers section
        incorrect_canvas = tk.Canvas(split_frame, bg=self.colors['content_bg'])
        incorrect_scrollbar = ttk.Scrollbar(split_frame, orient="vertical", command=incorrect_canvas.yview)
        incorrect_frame = ttk.Frame(incorrect_canvas, style="ErrorCard.TFrame")
        
        incorrect_frame.bind(
            "<Configure>",
            lambda e: incorrect_canvas.configure(scrollregion=incorrect_canvas.bbox("all"))
        )
        
        incorrect_canvas.create_window((0, 0), window=incorrect_frame, anchor="nw")
        incorrect_canvas.configure(yscrollcommand=incorrect_scrollbar.set)
        
        incorrect_canvas.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        incorrect_scrollbar.pack(side="right", fill="y")
        
        # Add labels to correct and incorrect frames
        ttk.Label(correct_frame, text="Correct Answers", style="Title.TLabel").pack(pady=10)
        ttk.Label(incorrect_frame, text="Incorrect Answers", style="Title.TLabel").pack(pady=10)
        
        # Add questions to correct or incorrect frames
        for i, question in enumerate(self.questions, 1):
            is_answered = str(question[0]) in self.answers
            student_answer = self.answers.get(str(question[0]), "Not answered")
            correct_answer = question[-1]
            options = {'A': question[2], 'B': question[3], 'C': question[4], 'D': question[5]}
            
            q_frame = ttk.Frame(correct_frame if student_answer == correct_answer else incorrect_frame, style="Card.TFrame")
            q_frame.pack(fill='x', pady=10, padx=20)
            
            # Question header with status
            status_color = self.colors['success'] if is_answered else self.colors['error']
            status_text = "Answered" if is_answered else "Not Answered"
            
            ttk.Label(
                q_frame,
                text=f"Question {i} - {status_text}",
                font=('Segoe UI', 12, 'bold'),
                foreground=status_color,
                background=self.colors['menu_bg']
            ).pack(anchor='w', pady=5)
            
            # Question text
            ttk.Label(
                q_frame,
                text=question[1],
                font=('Segoe UI', 11),
                foreground=self.colors['text'],
                background=self.colors['menu_bg'],
                wraplength=700
            ).pack(anchor='w', pady=5)
            
            # Answer status
            answer_text = f"Your Answer: {student_answer} - {options.get(student_answer, 'N/A')}"
            correct_text = f"Correct Answer: {correct_answer} - {options.get(correct_answer, 'N/A')}"
            
            ttk.Label(
                q_frame,
                text=answer_text,
                font=('Segoe UI', 11),
                foreground=self.colors['success'] if student_answer == correct_answer else self.colors['error'],
                background=self.colors['menu_bg']
            ).pack(anchor='w', pady=5)
            
            if student_answer != correct_answer:
                ttk.Label(
                    q_frame,
                    text=correct_text,
                    font=('Segoe UI', 11),
                    foreground=self.colors['success'],
                    background=self.colors['menu_bg']
                ).pack(anchor='w', pady=5)
        
        # Buttons frame with improved styling
        button_frame = ttk.Frame(review_container, style="Content.TFrame")
        button_frame.pack(fill='x', pady=20)
        
        # Warning message for unanswered questions
        if unanswered > 0:
            ttk.Label(
                button_frame,
                text=f"Warning: You have {unanswered} unanswered questions!",
                font=('Segoe UI', 11),
                foreground=self.colors['warning'],
                background=self.colors['content_bg']
            ).pack(pady=(0, 10))
        
        # Action buttons
        buttons_container = ttk.Frame(button_frame, style="Content.TFrame")
        buttons_container.pack()

        ttk.Button(
            buttons_container,
            text="Return To Available Exam",
            style="Custom.TButton",
            command=self.show_available_exams
        ).pack(side='left', padx=10)
        
        # Style configurations for success and error frames
        self.style.configure("SuccessCard.TFrame", background=self.colors['menu_bg'], borderwidth=2, relief="solid", bordercolor=self.colors['success'])
        self.style.configure("ErrorCard.TFrame", background=self.colors['menu_bg'], borderwidth=2, relief="solid", bordercolor=self.colors['error'])

    def submit_exam(self):
        self.save_answer()
        """Submit the exam and calculate results"""
        if not messagebox.askyesno("Confirm Submission", "Are you sure you want to submit the exam?"):
            return
        
        # Stop the timer
        self.timer_active = False
        
        # Calculate score based on correct answers
        total_questions = len(self.questions)
        correct_answers = 0
        
        conn = sqlite3.connect('exam_system.db')
        cursor = conn.cursor()
        
        try:
            # Compare student's answers with correct answers from questions table
            for question in self.questions:
                question_id = question[0]
                correct_answer = question[-1]  # Assuming correct_answer is stored as a letter ('A', 'B', 'C', 'D')
                student_answer = self.answers.get(str(question_id))  # Get student's answer
                # Count as correct only if student's answer matches the correct answer
                if student_answer and student_answer == correct_answer:
                    correct_answers += 1
            
            # Calculate percentage score
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

            # Get total marks for the exam
            cursor.execute("SELECT total_marks FROM exams WHERE id = ?", (self.exam_id,))
            total_marks = cursor.fetchone()[0]
            # Save results to database
            cursor.execute("""
                INSERT INTO results (student_id, exam_id, score, date)
                VALUES (?, ?, ?, datetime('now'))
            """, (self.student_id, self.exam_id, score))
            
            conn.commit()
            
            # Show results page
            self.show_result_page(score)
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to submit exam: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def show_result_page(self, score):
        """Display the final exam results"""
        self.clear_content()
        
        # Results container
        results_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        results_container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Congratulations header
        ttk.Label(
            results_container,
            text="Exam Completed!",
            font=('Segoe UI', 28, 'bold'),
            foreground=self.colors['text'],
            background=self.colors['content_bg']
        ).pack(pady=(0, 30))
        
        # Score display
        score_frame = ttk.Frame(results_container, style="Card.TFrame")
        score_frame.pack(fill='x', pady=20, padx=50)
        
        # Score color based on performance
        score_color = self.colors['success'] if score >= 80 else \
                    self.colors['accent1'] if score >= 60 else \
                    self.colors['warning']
        
        ttk.Label(
            score_frame,
            text="Your Score",
            font=('Segoe UI', 16),
            foreground=self.colors['text'],
            background=self.colors['menu_bg']
        ).pack(pady=(20, 10))
        
        ttk.Label(
            score_frame,
            text=f"{score:.1f}%",
            font=('Segoe UI', 48, 'bold'),
            foreground=score_color,
            background=self.colors['menu_bg']
        ).pack(pady=(0, 20))
        
        # Performance message
        message = "Excellent!" if score >= 80 else \
                "Good job!" if score >= 60 else \
                "Keep practicing!"
        
        ttk.Label(
            score_frame,
            text=message,
            font=('Segoe UI', 14),
            foreground=score_color,
            background=self.colors['menu_bg']
        ).pack(pady=(0, 20))
        
        # Return to exams button
        ttk.Button(
            results_container,
            text="Review Questions",
            style="Custom.TButton",
            command=self.show_review_dialog
        ).pack(pady=30)

    def save_answer(self):
        """Save the current answer to the answers dictionary"""
        current_q_id = self.questions[self.current_question][0]
        self.answers[str(current_q_id)] = self.selected_option.get()

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
