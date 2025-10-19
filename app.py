from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = '124578aaa'

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers WHERE username=%s AND password=%s", (username, password))
    teacher = cursor.fetchone()
    conn.close()
    if teacher:
        session['teacher'] = username
        return redirect(url_for('view_results'))
    return "Invalid credentials"

@app.route('/view_results')
def view_results():
    if 'teacher' not in session:
        return redirect(url_for('home'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template('result.html', students=students)

@app.route('/manage')
def manage():
    if 'teacher' not in session:
        return redirect(url_for('home'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template('student.html', students=students)

@app.route('/add', methods=['POST'])
def add():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            student_id, roll_number, class_name, dbms, mpmc, cn, java,
            data_structure, flat, ss_lab, dbms_lab, sgpa
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data['student_id'], data['roll_no'], data['class_name'],
        data['dbms'], data['mpmc'], data['cn'], data['java'],
        data['ds'], data['flat'], data['ss_lab'], data['dbms_lab'], data['sgpa']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('view_results'))  # ✅ Updated redirect

@app.route('/update', methods=['POST'])
def update():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET
            roll_number=%s,
            class_name=%s,
            dbms=%s,
            mpmc=%s,
            cn=%s,
            java=%s,
            data_structure=%s,
            flat=%s,
            ss_lab=%s,
            dbms_lab=%s,
            sgpa=%s
        WHERE student_id=%s
    """, (
        data['roll_no'], data['class_name'], data['dbms'], data['mpmc'],
        data['cn'], data['java'], data['ds'], data['flat'],
        data['ss_lab'], data['dbms_lab'], data['sgpa'], data['student_id']
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('manage'))

@app.route('/delete/<int:student_id>')
def delete(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage'))

@app.route('/logout')
def logout():
    session.pop('teacher', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)