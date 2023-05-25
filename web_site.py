import sqlite3
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
def conn_db():
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS "attendance_report" (
	"note_id"	integer,
	"group_id"	INTEGER,
	"curator_id"	TEXT,
	"date_of_report"	date,
	"valid_reason"	integer,
	"disrespectful_reason"	INTEGER,
	"disease_reason"	INTEGER,
	"who_is_present"	INTEGER,
	FOREIGN KEY("group_id") REFERENCES "groups"("group_id"),
	FOREIGN KEY("curator_id") REFERENCES "curators"("curator_id"),
	PRIMARY KEY("note_id"))""")
    if conn:
        print ("Connected Successfully")
    else:
        print ("Connection Not Established")
    conn.commit()
    conn.close()

# Страница для отображения списка посещаемости
@app.route('/')
def index():
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance_report")
    attendance_report = c.fetchall()
    conn.close()
    return render_template('index.html', attendance_report=attendance_report)


if __name__ == '__main__':
    conn_db()
    app.run()






    

