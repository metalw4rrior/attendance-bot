#!/usr/bin/env python3
import sqlite3
from flask import Flask, render_template,request
import sqlite3
from datetime import datetime
app = Flask(__name__)
def conn_db():
    conn = sqlite3.connect('database_project.db')
    if conn:
        print ("Connected Successfully")
    else:
        print ("Connection Not Established")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/process_date', methods=['POST'])
def process_date():
    date_str = request.form['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d') 
    formatted_date = date_obj.strftime('%Y-%m-%d')  
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance_report WHERE date_of_report = ?", (formatted_date,))
    attendance_report = c.fetchall()
    conn.close()

    return render_template('index.html', attendance_report=attendance_report)


if __name__ == '__main__':
    conn_db()
    app.run(host = '0.0.0.0')
