import sqlite3
from flask import Flask, render_template
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

# Страница для отображения списка посещаемости
@app.route('/')
def index():
    date_obj = datetime.now().date() 
    date_str = str(date_obj.strftime('%Y-%m-%d'))
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance_report where date_of_report =(?)", (date_str,))
    attendance_report = c.fetchall()
    conn.close()
    return render_template('index.html', attendance_report=attendance_report)


if __name__ == '__main__':
    conn_db()
    app.run()






    

