import sqlite3
import hashlib


def create_database():
    conn = sqlite3.connect('exam_system.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, -- Encrypted password
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'Teacher', 'Student')) NOT NULL
    )''')

    # Create admins table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )''')

    # Create teachers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        phone TEXT,
        subject_id INTEGER,
        FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )''')

    # Create subjects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL
    )''')

    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        class TEXT NOT NULL,
        phone TEXT,
        profile_pic BLOB,
        bio TEXT,
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )''')

    # Create exams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        duration INTEGER NOT NULL,
        total_marks INTEGER NOT NULL DEFAULT 100,
        created_by INTEGER,
        FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
    )''')

    # Create questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        marks INTEGER NOT NULL DEFAULT 1,
        created_by INTEGER,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES teachers (id) ON DELETE SET NULL
    )''')

    # Create results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        exam_id INTEGER,
        score INTEGER,
        date TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
    )''')

    # Insert default admin if not exists
    default_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)",
                   ("admin", default_password, "Administrator", "admin@example.com", "Admin"))

    # Link admin to admins table
    cursor.execute("INSERT OR IGNORE INTO admins (id, name) VALUES ((SELECT id FROM users WHERE username = ?), ?)",
                   ("admin", "Administrator"))

    conn.commit()
    conn.close()


# Call the function to create the database
create_database()
