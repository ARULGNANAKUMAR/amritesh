from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime, date

app = Flask(__name__)

# Database initialization for Render
def init_db():
    # Render la database path different
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    contact TEXT,
                    address TEXT,
                    blood_group TEXT,
                    emergency_contact TEXT,
                    registered_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialization TEXT,
                    contact TEXT,
                    email TEXT,
                    consultation_fee DECIMAL(10,2),
                    available_days TEXT,
                    available_time TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    doctor_id INTEGER,
                    appointment_date DATE,
                    appointment_time TIME,
                    status TEXT DEFAULT 'Scheduled',
                    reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
                )''')
    
    # Insert sample data if empty
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        sample_patients = [
            ('Ramesh Kumar', 45, 'Male', '9876543210', 'Chennai', 'O+', '9876543211'),
            ('Priya Sharma', 32, 'Female', '8765432109', 'Bangalore', 'A+', '8765432110')
        ]
        c.executemany('INSERT INTO patients (name, age, gender, contact, address, blood_group, emergency_contact) VALUES (?,?,?,?,?,?,?)', sample_patients)
        
        sample_doctors = [
            ('Dr. Rajesh Khanna', 'Cardiology', '9123456780', 'dr.rajesh@hospital.com', 800.00, 'Mon,Wed,Fri', '09:00-13:00'),
            ('Dr. Anjali Mehta', 'Pediatrics', '9234567891', 'dr.anjali@hospital.com', 600.00, 'Tue,Thu,Sat', '10:00-14:00')
        ]
        c.executemany('INSERT INTO doctors (name, specialization, contact, email, consultation_fee, available_days, available_time) VALUES (?,?,?,?,?,?,?)', sample_doctors)
    
    conn.commit()
    conn.close()

# Database connection for Render
def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# API Routes - same as before
@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO patients (name, age, gender, contact, address, blood_group, emergency_contact) VALUES (?,?,?,?,?,?,?)',
              (data['name'], data['age'], data['gender'], data['contact'], data['address'], data['blood_group'], data['emergency_contact']))
    conn.commit()
    patient_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Patient added!', 'patient_id': patient_id})

@app.route('/get_patients')
def get_patients():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return jsonify([dict(patient) for patient in patients])

@app.route('/get_doctors')
def get_doctors():
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors').fetchall()
    conn.close()
    return jsonify([dict(doctor) for doctor in doctors])

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason) VALUES (?,?,?,?,?)',
              (data['patient_id'], data['doctor_id'], data['appointment_date'], data['appointment_time'], data['reason']))
    conn.commit()
    appointment_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Appointment scheduled!', 'appointment_id': appointment_id})

@app.route('/get_appointments')
def get_appointments():
    conn = get_db_connection()
    appointments = conn.execute('''
        SELECT a.*, p.name as patient_name, d.name as doctor_name 
        FROM appointments a 
        JOIN patients p ON a.patient_id = p.patient_id 
        JOIN doctors d ON a.doctor_id = d.doctor_id
    ''').fetchall()
    conn.close()
    return jsonify([dict(appt) for appt in appointments])

@app.route('/get_dashboard_stats')
def get_dashboard_stats():
    conn = get_db_connection()
    total_patients = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    total_doctors = conn.execute('SELECT COUNT(*) FROM doctors').fetchone()[0]
    total_appointments = conn.execute('SELECT COUNT(*) FROM appointments').fetchone()[0]
    today_appointments = conn.execute('SELECT COUNT(*) FROM appointments WHERE appointment_date = ?', 
                                     (date.today().isoformat(),)).fetchone()[0]
    conn.close()
    return jsonify({
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments
    })

# Render specific - port configuration
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
