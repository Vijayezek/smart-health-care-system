import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from utils.time_utils import get_ist_time
import os

DATABASE_PATH = 'database/smart_health.db'

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            contact TEXT NOT NULL,
            experience TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            symp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom_name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            med_id INTEGER PRIMARY KEY AUTOINCREMENT,
            med_name TEXT NOT NULL,
            disease TEXT NOT NULL,
            usage TEXT,
            side_effects TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            feed_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            sentiment TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
    if cursor.fetchone() is None:
        admin_password = generate_password_hash('admin123')
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', admin_password))
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        sample_doctors = [
            ('Dr. Rajesh Kumar', 'Cardiologist', '+91-9876543210', '15 years'),
            ('Dr. Priya Sharma', 'General Physician', '+91-9876543211', '10 years'),
            ('Dr. Amit Patel', 'Neurologist', '+91-9876543212', '12 years'),
            ('Dr. Sneha Reddy', 'Dermatologist', '+91-9876543213', '8 years'),
            ('Dr. Vikram Singh', 'Pediatrician', '+91-9876543214', '20 years')
        ]
        cursor.executemany("INSERT INTO doctors (name, specialization, contact, experience) VALUES (?, ?, ?, ?)", sample_doctors)
    
    cursor.execute("SELECT COUNT(*) FROM symptoms")
    if cursor.fetchone()[0] == 0:
        sample_symptoms = [
            ('Fever', 'High body temperature above 100.4°F'),
            ('Headache', 'Pain in the head or upper neck'),
            ('Cough', 'Sudden expulsion of air from lungs'),
            ('Cold', 'Runny nose and sneezing'),
            ('Fatigue', 'Extreme tiredness'),
            ('Nausea', 'Feeling of sickness'),
            ('Dizziness', 'Light-headedness or vertigo'),
            ('Body Pain', 'Aches in muscles or joints')
        ]
        cursor.executemany("INSERT INTO symptoms (symptom_name, description) VALUES (?, ?)", sample_symptoms)
    
    cursor.execute("SELECT COUNT(*) FROM medicines")
    if cursor.fetchone()[0] == 0:
        sample_medicines = [
            ('Paracetamol', 'Fever', 'Take 500mg every 6 hours', 'Nausea, allergic reactions'),
            ('Ibuprofen', 'Body Pain', 'Take 400mg every 8 hours', 'Stomach upset'),
            ('Amoxicillin', 'Cold', 'Take 500mg every 8 hours', 'Diarrhea, allergic reactions'),
            ('Cetirizine', 'Cold', 'Take 10mg once daily', 'Drowsiness'),
            ('Dolo 650', 'Fever', 'Take 1 tablet every 6 hours', 'Liver damage if overdosed'),
            ('Azithromycin', 'Cough', 'Take 500mg once daily for 3 days', 'Nausea, diarrhea'),
            ('ORS', 'Nausea', 'Dissolve in water and drink', 'None'),
            ('Aspirin', 'Headache', 'Take 325mg every 4-6 hours', 'Stomach irritation')
        ]
        cursor.executemany("INSERT INTO medicines (med_name, disease, usage, side_effects) VALUES (?, ?, ?, ?)", sample_medicines)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_unique_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is None

def validate_unique_mobile(mobile):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    result = cursor.fetchone()
    conn.close()
    return result is None

def register_user(name, email, mobile, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    created_at = get_ist_time()
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, mobile, password, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, mobile, hashed_password, created_at)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return dict(user)
    return None

def verify_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()
    
    if admin and check_password_hash(admin['password'], password):
        return dict(admin)
    return None
