import sqlite3 as sl
from datetime import datetime

def db_start():
    global db,cur
    db = sl.connect('database_project.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS curators(curator_id INTEGER PRIMARY KEY, curator_fio TEXT, chat_id TEXT, password TEXT)")
    db.commit()

db_start()

date_of_report = datetime.now().strftime('%Y-%m-%d')

# Проверка на наличие даты
def check(date_of_report):
    info = cur.execute(f"select * from attendance_report where date_of_report='{date_of_report}'").fetchone()
    if info is None:
        return True

def new_day(date_of_report):
    if check(date_of_report): # если записей с датой нет, то добавит незаполненные группы и фио
        cur.execute(f"""INSERT INTO attendance_report
        (group_name, curator_fio, date_of_report, valid_reason, disrespectful_reason, disease_reason, who_is_present, itog_percent, itog_u_b)
        SELECT group_name, curator_fio, '{date_of_report}', "-", "-", "-", "-", "-", "-" FROM groups JOIN curators ON groups.curator_id = curators.curator_id""")
        db.commit()

new_day(date_of_report)

