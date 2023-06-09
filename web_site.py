#!/usr/bin/env python3
import sqlite3
from flask import Flask, render_template,request
import sqlite3
from datetime import datetime
from datetime import date
import json

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
    current_date = date.today().isoformat()
    return render_template('index.html', current_date=current_date)
@app.route('/process_date', methods=['POST'])
def process_date():
    date_str = request.form['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM attendance_report WHERE date_of_report = ? ORDER BY CASE
      WHEN group_name LIKE '%ДО' THEN 1
      WHEN group_name LIKE '%ПДО ТТ' THEN 2
      WHEN group_name LIKE '%АТ' THEN 3
      WHEN group_name LIKE '%ИБАС' THEN 4
      WHEN group_name LIKE '%КП' THEN 5
      WHEN group_name LIKE '%ОСАТПиП' THEN 6
      WHEN group_name LIKE '%ССА' THEN 7
      WHEN group_name LIKE '%ИСиП' THEN 8
      WHEN group_name LIKE '%TEST' THEN 9
      ELSE 10 END
      , group_name""", (formatted_date,))
    attendance_report = c.fetchall()
    conn.close()
    endings = ['ДО','ПДО ТТ','АТ','ИБАС','КП','ОСАТПиП','ССА','ИСиП','TEST']
    all_count = valid_from_database(endings)
    serialized_data = json.dumps(all_count)
    serialized_data_with_brackets = '[' + serialized_data[1:-1] + ']'
    return render_template('index.html', attendance_report=attendance_report, all_TEST_count=serialized_data_with_brackets)
    

def valid_from_database(gr_name_ending):
    absenteeism_counts = []
    date_str = request.form['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    conn = sqlite3.connect('database_project.db')
    c = conn.cursor()
    c.execute("SELECT group_name, valid_reason, disrespectful_reason, disease_reason, who_is_present FROM attendance_report WHERE date_of_report = ?", (formatted_date,))
    rows = c.fetchall()
    test_lib = []
    TEST_count = [0, 0, 0, 0, 0]  # Инициализация списка сумм значений
    all_TEST_count = []
    for i in gr_name_ending:
        test_lib.clear()
        for row in rows:
            absenteeism_counts.append(row)
            if str(row[0]).endswith(i):
                test_lib.append(row)
        valid_sum = 0
        disr_sum = 0
        diseas_sum = 0
        present_sum = 0
        for row in test_lib:
            valid_reason = row[1]
            disr_reason = row[2]
            diseas_reason = row[3]
            present_here = row[4]
            if valid_reason != "-":
                valid_sum += int(valid_reason)
            if disr_reason != "-":
                disr_sum += int(disr_reason)
            if diseas_reason != "-":
                diseas_sum += int(diseas_reason)
            if present_here != "-":
                present_sum += int(present_here)
        if present_sum != 0:
            sum_all = present_sum+valid_sum+diseas_sum+disr_sum
            all_for_percent = round((((sum_all-disr_sum-valid_sum-diseas_sum) / sum_all) * 100),1)
            all_for_u_b = round((((sum_all-disr_sum)/sum_all)*100),1)
            all_for_percent = str(all_for_percent)+'%'
            all_for_u_b = str(all_for_u_b)+'%'
        else:
            all_for_percent = '0%'
            all_for_u_b = '0%'
        this_all = valid_sum + diseas_sum + disr_sum
        TEST_count = ['','','','Итого',valid_sum, disr_sum, diseas_sum, present_sum, all_for_percent, all_for_u_b]
        all_TEST_count.append(TEST_count)

    return all_TEST_count
if __name__ == '__main__':
    conn_db()
    app.run(host = '0.0.0.0')
