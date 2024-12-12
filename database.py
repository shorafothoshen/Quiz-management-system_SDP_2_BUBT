import sqlite3
import hashlib


def create_database():
    conn = sqlite3.connect('exam_system.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        class TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        duration INTEGER NOT NULL,
        total_marks INTEGER NOT NULL DEFAULT 100,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES admins (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        exam_id INTEGER,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        marks INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        exam_id INTEGER,
        score INTEGER,
        date TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (exam_id) REFERENCES exams (id)
    )''')

    # Insert default admin if not exists
    default_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("INSERT OR IGNORE INTO admins (username, password, name) VALUES (?, ?, ?)",
                   ("admin", default_password, "Administrator"))

    conn.commit()
    conn.close()