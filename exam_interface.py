import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
class ExamInterface:
    def __init__(self, root, student_id, exam_id):
        self.root = root
        self.student_id = student_id
        self.exam_id = exam_id
        self.questions = []
        self.current_question = 0
        self.answers = {}
        self.timer_active = False
        
        # Configure the window
        self.root.title("Exam Interface")
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
            'hover': '#233554',         # Hover state color
            'success': '#4CAF50',       # Success/Answered color
            'warning': '#FFA726',       # Warning color
            'error': '#EF5350'          # Error/Unanswered color
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure widget styles
        self.style.configure("Sidebar.TFrame",
                           background=self.colors['sidebar'])
        self.style.configure("Content.TFrame",
                           background=self.colors['content'])
        self.style.configure("Card.TFrame",
                           background=self.colors['sidebar'])
                           
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
                           
        self.style.configure("Question.TLabel",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 14),
                           wraplength=800)
                           
        self.style.configure("Timer.TLabel",
                           background=self.colors['sidebar'],
                           foreground=self.colors['accent1'],
                           font=('Segoe UI', 16, 'bold'))
                           
        self.style.configure("Custom.TButton",
                           background=self.colors['accent1'],
                           foreground=self.colors['bg_dark'],
                           font=('Segoe UI', 11),
                           padding=(20, 10))
                           
        self.style.configure("Answered.TButton",
                           background=self.colors['success'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11))
                           
        self.style.configure("Unanswered.TButton",
                           background=self.colors['error'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11))
                           
        self.style.configure("Warning.TButton",
                           background=self.colors['warning'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 11))
                           
        self.style.configure("Custom.TRadiobutton",
                           background=self.colors['content'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 12))
                           
        # Load exam data and questions
        if self.load_questions():
            # Set up the UI
            self.setup_ui()
            # Show first question
            self.show_question()
            # Start the timer
            self.start_timer()
            
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
            
    def setup_ui(self):
        # Main container with two columns
        self.main_container = ttk.Frame(self.root, style="Content.TFrame")
        self.main_container.pack(fill='both', expand=True)
        
        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        self.sidebar.pack(side='left', fill='y', padx=2)
        self.sidebar.pack_propagate(False)
        
        # Exam info in sidebar
        ttk.Label(self.sidebar,
                 text="📝 Exam Details",
                 style="Card.TLabel").pack(pady=(30, 10), padx=20)
                 
        ttk.Label(self.sidebar,
                 text=f"Title: {self.exam_title}",
                 style="Card.TLabel").pack(pady=5, padx=20)
                 
        ttk.Label(self.sidebar,
                 text=f"Duration: {self.duration} minutes",
                 style="Card.TLabel").pack(pady=5, padx=20)
                 
        ttk.Separator(self.sidebar,
                     orient='horizontal').pack(fill='x', pady=20, padx=20)
                     
        # Timer with progress bar
        timer_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        timer_frame.pack(fill='x', padx=20, pady=10)
        
        self.timer_label = ttk.Label(timer_frame,
                                   text="Time Remaining: --:--",
                                   style="Timer.TLabel")
        self.timer_label.pack(pady=(0, 5))
        
        self.timer_progress = ttk.Progressbar(timer_frame, 
                                            mode='determinate',
                                            length=200)
        self.timer_progress.pack(fill='x')
        
        ttk.Separator(self.sidebar,
                     orient='horizontal').pack(fill='x', pady=20, padx=20)
                     
        # Question navigation
        ttk.Label(self.sidebar,
                 text="Question Navigation",
                 style="Card.TLabel").pack(pady=(0, 10), padx=20)
        
        # Question buttons grid
        nav_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        nav_frame.pack(fill='x', padx=20)
        
        self.question_buttons = []
        row = 0
        col = 0
        for i in range(len(self.questions)):
            btn = ttk.Button(nav_frame,
                           text=str(i + 1),
                           width=3,
                           style="Custom.TButton",
                           command=lambda x=i: self.goto_question(x))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.question_buttons.append(btn)
            col += 1
            if col > 4:  # 5 buttons per row
                col = 0
                row += 1
                     
        # Content area
        self.content_frame = ttk.Frame(self.main_container, style="Content.TFrame")
        self.content_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        # Question container
        self.question_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.question_container.pack(fill='both', expand=True)
        
        # Progress indicator
        self.progress_frame = ttk.Frame(self.question_container, style="Content.TFrame")
        self.progress_frame.pack(fill='x', pady=(0, 20))
        
        self.question_number_label = ttk.Label(
            self.progress_frame,
            text="Question 1 of 1",
            style="Subtitle.TLabel"
        )
        self.question_number_label.pack(side='left')
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Answered: 0/0",
            style="Subtitle.TLabel"
        )
        self.progress_label.pack(side='right')
        
        # Question text
        self.question_text = tk.Text(
            self.question_container,
            height=4,
            wrap=tk.WORD,
            font=('Segoe UI', 14),
            bg=self.colors['content'],
            fg=self.colors['text'],
            relief='flat',
            state='disabled'
        )
        self.question_text.pack(fill='x', pady=(0, 20))
        
        # Options
        self.selected_option = tk.StringVar()
        self.selected_option.trace('w', self.on_answer_change)
        self.option_buttons = []
        
        for i in range(4):
            option = ttk.Radiobutton(
                self.question_container,
                text="",
                variable=self.selected_option,
                value=str(i+1),
                style="Custom.TRadiobutton"
            )
            option.pack(anchor='w', pady=5)
            self.option_buttons.append(option)
            
        # Navigation buttons
        button_frame = ttk.Frame(self.question_container, style="Content.TFrame")
        button_frame.pack(pady=20)
        
        self.prev_button = ttk.Button(
            button_frame,
            text="Previous (←)",
            command=self.prev_question,
            style="Custom.TButton"
        )
        self.prev_button.pack(side='left', padx=10)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next (→)",
            command=self.next_question,
            style="Custom.TButton"
        )
        self.next_button.pack(side='left', padx=10)
        
        ttk.Button(
            button_frame,
            text="Submit Exam",
            command=self.show_review_dialog,
            style="Custom.TButton"
        ).pack(side='left', padx=10)
        
        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_question())
        self.root.bind('<Right>', lambda e: self.next_question())
        self.root.bind('<Control-s>', lambda e: self.auto_save())
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize autosave
        self.last_autosave = datetime.now()
        
    def goto_question(self, index):
        """Navigate to a specific question by index"""
        if 0 <= index < len(self.questions):
            self.current_question = index
            self.show_question()
            
    def on_answer_change(self, *args):
        """Handle answer changes and update UI"""
        current_q_id = str(self.questions[self.current_question][0])
        self.answers[current_q_id] = self.selected_option.get()
        
        # Update question button state
        self.question_buttons[self.current_question].configure(
            style="Answered.TButton" if current_q_id in self.answers else "Unanswered.TButton"
        )
        
        # Update progress label
        answered = len(self.answers)
        total = len(self.questions)
        self.progress_label.configure(text=f"Answered: {answered}/{total}")
        
        # Trigger autosave
        self.auto_save()
        
    def auto_save(self, *args):
        """Auto-save exam progress"""
        current_time = datetime.now()
        if (current_time - self.last_autosave).seconds >= 30:  # Auto-save every 30 seconds
            # Save to temporary storage or database
            self.last_autosave = current_time
            
    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Are you sure you want to exit the exam? Your progress will be saved."):
            self.auto_save()
            self.root.destroy()
            
    def show_question(self):
        if not self.questions:
            return
            
        question_data = self.questions[self.current_question]
        question_num = self.current_question + 1
        total_questions = len(self.questions)
        
        # Update progress label
        self.question_number_label.config(text=f"Question {question_num} of {total_questions}")
        
        # Update question text with formatting
        self.question_text.config(state='normal')
        self.question_text.delete('1.0', tk.END)
        self.question_text.insert(tk.END, question_data[1])
        self.question_text.config(state='disabled')
        
        # Update options with better formatting
        options = [question_data[i] for i in range(2, 6)]  # options start from index 2
        for i, option in enumerate(options):
            self.option_buttons[i].config(text=f"{chr(65+i)}. {option}")
            
    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()
            
    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()
            
    def show_review_dialog(self):
        review_window = tk.Toplevel(self.root)
        review_window.title("Review Answers")
        review_window.geometry("800x600")
        review_window.configure(bg=self.colors['content'])
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(review_window, bg=self.colors['content'])
        scrollbar = ttk.Scrollbar(review_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Content.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title and summary
        header_frame = ttk.Frame(scrollable_frame, style="Content.TFrame")
        header_frame.pack(fill='x', pady=20, padx=20)
        
        ttk.Label(header_frame,
                 text="Review Your Answers",
                 style="Title.TLabel").pack(side='left')
        
        # Summary statistics
        answered = len(self.answers)
        total = len(self.questions)
        unanswered = total - answered
        
        summary_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Label(summary_frame,
                text=f"Total Questions: {total}",
                style="Card.TLabel").pack(side='left', padx=20, pady=10)
        
        ttk.Label(summary_frame,
                text=f"Answered: {answered}",
                foreground=self.colors['success'],
                style="Card.TLabel").pack(side='left', padx=20)
        
        ttk.Label(summary_frame,
                text=f"Unanswered: {unanswered}",
                foreground=self.colors['error'],
                style="Card.TLabel").pack(side='left', padx=20)
        
        # Display all questions and answers
        for i, question_data in enumerate(self.questions, 1):
            q_id, question, opt1, opt2, opt3, opt4, correct_answer = question_data
            
            # Question frame
            q_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
            q_frame.pack(fill='x', pady=10, padx=20)
            
            # Status indicator
            status_frame = ttk.Frame(q_frame, style="Card.TFrame")
            status_frame.pack(fill='x', padx=10, pady=5)
            
            status_color = self.colors['success'] if str(q_id) in self.answers else self.colors['error']
            status_text = "Answered" if str(q_id) in self.answers else "Not Answered"
            
            ttk.Label(status_frame,
                    text=f"Question {i} - {status_text}",
                    foreground=status_color,
                    style="Card.TLabel").pack(side='left')
            
            # Question text
            ttk.Label(q_frame,
                    text=question,
                    style="Question.TLabel",
                    wraplength=700).pack(anchor='w', pady=(5,10), padx=10)
            
            # Your answer
            if str(q_id) in self.answers:
                answer = self.answers[str(q_id)]
                options = {'1': opt1, '2': opt2, '3': opt3, '4': opt4}
                answer_text = f"Your Answer: Option {answer} - {options[answer]}"
                
                ttk.Label(q_frame,
                        text=answer_text,
                        style="Card.TLabel",
                        foreground=self.colors['success']).pack(anchor='w', padx=10)
            else:
                ttk.Label(q_frame,
                        text="Your Answer: Not answered",
                        style="Card.TLabel",
                        foreground=self.colors['error']).pack(anchor='w', padx=10)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        button_frame = ttk.Frame(review_window, style="Content.TFrame")
        button_frame.pack(pady=20)
        
        if unanswered > 0:
            warning_label = ttk.Label(button_frame,
                                  text=f"Warning: You have {unanswered} unanswered questions!",
                                  foreground=self.colors['warning'],
                                  style="Card.TLabel")
            warning_label.pack(pady=(0, 10))
        
        ttk.Button(button_frame,
                 text="Continue Editing",
                 style="Custom.TButton",
                 command=review_window.destroy).pack(side='left', padx=10)
        
        submit_btn = ttk.Button(button_frame,
                             text="Submit Exam",
                             style="Custom.TButton" if unanswered == 0 else "Warning.TButton",
                             command=lambda: [review_window.destroy(), self.submit_exam()])
        submit_btn.pack(side='left', padx=10)
        
    def submit_exam(self):
        if not self.questions:
            messagebox.showinfo("Cannot Submit", "This exam has no questions to submit.")
            return
            
        if not messagebox.askyesno("Confirm Submission", "Are you sure you want to submit the exam?"):
            return
            
        # Calculate score
        total_questions = len(self.questions)
        correct_answers = 0
        
        for question in self.questions:
            q_id, _, _, _, _, _, correct_answer = question
            if str(q_id) in self.answers and self.answers[str(q_id)] == correct_answer:
                correct_answers += 1
                
        score = (correct_answers / total_questions) * 100
        
        # Save result to database
        try:
            with sqlite3.connect('exam_system.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO results (student_id, exam_id, score, date)
                    VALUES (?, ?, ?, datetime('now'))
                """, (self.student_id, self.exam_id, score))
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", "Failed to save results")
            return
            
        # Create results window
        results_window = tk.Toplevel()
        results_window.title("Exam Results")
        results_window.geometry("500x600")  
        results_window.configure(bg=self.colors['bg_dark'])
        
        # Center the window
        screen_width = results_window.winfo_screenwidth()
        screen_height = results_window.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 600) // 2
        results_window.geometry(f"500x600+{x}+{y}")
        
        # Make window non-resizable
        results_window.resizable(False, False)
        
        # Create main container
        main_frame = ttk.Frame(results_window, style="Content.TFrame")
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Results header
        ttk.Label(main_frame,
                text="Exam Completed!",
                style="Title.TLabel",
                font=('Segoe UI', 24, 'bold')).pack(pady=(0, 20))
        
        # Score display with custom style
        score_frame = ttk.Frame(main_frame, style="Card.TFrame")
        score_frame.pack(fill='x', pady=20)
        
        score_color = '#4CAF50' if score >= 80 else '#FFA726' if score >= 60 else '#EF5350'
        
        ttk.Label(score_frame,
                text="Your Score",
                style="Card.TLabel",
                font=('Segoe UI', 16)).pack(pady=(10, 5))
                
        ttk.Label(score_frame,
                text=f"{score:.1f}%",
                style="Card.TLabel",
                font=('Segoe UI', 48, 'bold'),  
                foreground=score_color).pack(pady=(0, 10))        
        # Statistics
        stats_frame = ttk.Frame(main_frame, style="Card.TFrame")
        stats_frame.pack(fill='x', pady=20)
        
        ttk.Label(stats_frame,
                text=f"Correct Answers: {correct_answers}/{total_questions}",
                style="Card.TLabel",
                font=('Segoe UI', 14)).pack(pady=10)  
                
        ttk.Label(stats_frame,
                text=f"Accuracy: {(correct_answers/total_questions)*100:.1f}%",
                style="Card.TLabel",
                font=('Segoe UI', 14)).pack(pady=10)  
        
        # Add spacing
        ttk.Frame(main_frame, style="Content.TFrame", height=40).pack()
        
        # Create a custom style for the dashboard button
        button_style = ttk.Style()
        button_style.configure("Dashboard.TButton",
                           background='#4CAF50',
                           foreground='white',
                           font=('Segoe UI', 14, 'bold'),
                           padding=(30, 15))
        
        # Return to Dashboard button
        dashboard_btn = ttk.Button(
            main_frame,
            text="Return to Dashboard",
            style="Dashboard.TButton",
            command=lambda: self.return_to_dashboard(results_window)
        )
        dashboard_btn.pack(pady=30, ipadx=20, ipady=10)
        
        # Make the button wider
        dashboard_btn.configure(width=25)
        
        # Handle window close
        results_window.protocol("WM_DELETE_WINDOW", lambda: self.return_to_dashboard(results_window))
        
        # Hide the exam window
        self.root.withdraw()
        
    def get_score_color(self, score):
        if score >= 80:
            return self.colors['success']
        elif score >= 60:
            return self.colors['accent1']
        else:
            return self.colors['warning']
            
    def return_to_dashboard(self, results_window):
        results_window.destroy()
        self.root.destroy()
        
        # Create a new root window for the dashboard
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Create a login window instance
        login_window = tk.Toplevel()
        login_window.withdraw()  # Hide it since we don't need it visible
        
        # Import and initialize StudentDashboard with all required parameters
        from student_dashboard import StudentDashboard
        dashboard = StudentDashboard(root, self.student_id, login_window)
        
    def view_detailed_report(self, score, correct_answers, total_questions):
        # TODO: Implement detailed report view
        messagebox.showinfo("Coming Soon", "Detailed report feature coming soon!")
        
    def start_timer(self):
        self.timer_active = True
        self.update_timer()

    def update_timer(self):
        if not hasattr(self, 'timer_active') or not self.timer_active:
            return
            
        if self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            
            # Update timer label and progress bar
            self.timer_label.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
            progress = (self.remaining_time / (self.duration * 60)) * 100
            self.timer_progress['value'] = progress
            
            # Show warnings at certain thresholds
            if minutes == 5 and seconds == 0:
                messagebox.showwarning("Time Warning", "5 minutes remaining!")
            elif minutes == 1 and seconds == 0:
                messagebox.showwarning("Time Warning", "1 minute remaining!")
            
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("Time's Up", "Your exam time has ended. The exam will be submitted automatically.")
            self.submit_exam()
