from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from utils.db_helper import (
    init_db, get_db_connection, validate_unique_email, 
    validate_unique_mobile, register_user, verify_user, verify_admin
)
from utils.time_utils import get_ist_time
from utils.sentiment_model import analyze_sentiment
from utils.symptom_predictor import predict_disease
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import re
import io
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
try:
    app.secret_key = os.environ['SESSION_SECRET']
except KeyError:
    raise RuntimeError("SESSION_SECRET environment variable is required but not set. Please configure it in your environment.")

init_db()

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([name, email, mobile, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')
        
        if not validate_mobile(mobile):
            flash('Invalid mobile number. Must be 10 digits starting with 6-9', 'error')
            return render_template('register.html')
        
        if not validate_unique_email(email):
            flash('Email already registered. Please use a different email', 'error')
            return render_template('register.html')
        
        if not validate_unique_mobile(mobile):
            flash('Mobile number already registered. Please use a different number', 'error')
            return render_template('register.html')
        
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            flash(message, 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if register_user(name, email, mobile, password):
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_type'] = 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = verify_admin(username, password)
        if admin:
            session['admin_id'] = admin['admin_id']
            session['admin_name'] = admin['username']
            session['user_type'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', doctors=doctors)

@app.route('/user/predict', methods=['POST'])
def predict_symptoms():
    if 'user_id' not in session or session.get('user_type') != 'user':
        return jsonify({'error': 'Unauthorized'}), 401
    
    symptoms = request.form.get('symptoms', '').strip()
    if not symptoms:
        return jsonify({'error': 'Please enter symptoms'}), 400
    
    disease = predict_disease(symptoms)
    
    conn = get_db_connection()
    medicines = conn.execute("SELECT * FROM medicines WHERE disease = ?", (disease,)).fetchall()
    conn.close()
    
    medicines_list = [dict(med) for med in medicines]
    
    return jsonify({
        'disease': disease,
        'medicines': medicines_list
    })

@app.route('/user/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        
        if message:
            sentiment = analyze_sentiment(message)
            timestamp = get_ist_time()
            
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO feedbacks (user_id, message, sentiment, timestamp) VALUES (?, ?, ?, ?)",
                (session['user_id'], message, sentiment, timestamp)
            )
            conn.commit()
            conn.close()
            
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Please enter your feedback', 'error')
    
    return render_template('feedback.html')

@app.route('/user/download_prescription')
def download_prescription():
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    disease = request.args.get('disease', 'General Checkup')
    medicines = request.args.get('medicines', 'Consult Doctor')
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFillColorRGB(0, 0.47, 0.71)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 100, "Smart Health Care System")
    
    p.setFillColorRGB(0.18, 0.18, 0.18)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, height - 150, "PRESCRIPTION")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 200, f"Patient Name: {session.get('user_name', 'N/A')}")
    p.drawString(100, height - 220, f"Date: {get_ist_time()}")
    p.drawString(100, height - 240, f"Predicted Condition: {disease}")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 280, "Recommended Medicines:")
    
    p.setFont("Helvetica", 11)
    y_position = height - 310
    
    if medicines and medicines != 'Consult Doctor':
        med_list = medicines.split(',')
        for i, med in enumerate(med_list, 1):
            p.drawString(120, y_position, f"{i}. {med.strip()}")
            y_position -= 20
    else:
        p.drawString(120, y_position, "Please consult a doctor for proper diagnosis")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 100, "Note: This is an AI-generated prescription. Please consult a qualified doctor.")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='prescription.pdf', mimetype='application/pdf')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    
    total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    total_doctors = conn.execute("SELECT COUNT(*) as count FROM doctors").fetchone()['count']
    total_feedbacks = conn.execute("SELECT COUNT(*) as count FROM feedbacks").fetchone()['count']
    total_medicines = conn.execute("SELECT COUNT(*) as count FROM medicines").fetchone()['count']
    
    positive_feedback = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'positive'").fetchone()['count']
    negative_feedback = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'negative'").fetchone()['count']
    neutral_feedback = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'neutral'").fetchone()['count']
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_doctors=total_doctors,
                         total_feedbacks=total_feedbacks,
                         total_medicines=total_medicines,
                         positive_feedback=positive_feedback,
                         negative_feedback=negative_feedback,
                         neutral_feedback=neutral_feedback)

@app.route('/admin/users')
def manage_users():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    
    return render_template('manage_users.html', users=users)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/doctors')
def manage_doctors():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    
    return render_template('manage_doctors.html', doctors=doctors)

@app.route('/admin/doctors/add', methods=['POST'])
def add_doctor():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    name = request.form.get('name')
    specialization = request.form.get('specialization')
    contact = request.form.get('contact')
    experience = request.form.get('experience')
    
    conn = get_db_connection()
    conn.execute("INSERT INTO doctors (name, specialization, contact, experience) VALUES (?, ?, ?, ?)",
                (name, specialization, contact, experience))
    conn.commit()
    conn.close()
    
    flash('Doctor added successfully', 'success')
    return redirect(url_for('manage_doctors'))

@app.route('/admin/doctors/delete/<int:doc_id>', methods=['POST'])
def delete_doctor(doc_id):
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    conn.execute("DELETE FROM doctors WHERE doc_id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    flash('Doctor deleted successfully', 'success')
    return redirect(url_for('manage_doctors'))

@app.route('/admin/medicines')
def manage_medicines():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    medicines = conn.execute("SELECT * FROM medicines").fetchall()
    conn.close()
    
    return render_template('manage_medicines.html', medicines=medicines)

@app.route('/admin/medicines/add', methods=['POST'])
def add_medicine():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    med_name = request.form.get('med_name')
    disease = request.form.get('disease')
    usage = request.form.get('usage')
    side_effects = request.form.get('side_effects')
    
    conn = get_db_connection()
    conn.execute("INSERT INTO medicines (med_name, disease, usage, side_effects) VALUES (?, ?, ?, ?)",
                (med_name, disease, usage, side_effects))
    conn.commit()
    conn.close()
    
    flash('Medicine added successfully', 'success')
    return redirect(url_for('manage_medicines'))

@app.route('/admin/medicines/delete/<int:med_id>', methods=['POST'])
def delete_medicine(med_id):
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    conn.execute("DELETE FROM medicines WHERE med_id = ?", (med_id,))
    conn.commit()
    conn.close()
    
    flash('Medicine deleted successfully', 'success')
    return redirect(url_for('manage_medicines'))

@app.route('/admin/feedbacks')
def manage_feedbacks():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    feedbacks = conn.execute("""
        SELECT f.*, u.name as user_name, u.email 
        FROM feedbacks f 
        JOIN users u ON f.user_id = u.user_id 
        ORDER BY f.timestamp DESC
    """).fetchall()
    conn.close()
    
    return render_template('manage_feedbacks.html', feedbacks=feedbacks)

@app.route('/admin/analytics')
def get_analytics():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    
    positive = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'positive'").fetchone()['count']
    negative = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'negative'").fetchone()['count']
    neutral = conn.execute("SELECT COUNT(*) as count FROM feedbacks WHERE sentiment = 'neutral'").fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'positive': positive,
        'negative': negative,
        'neutral': neutral
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
