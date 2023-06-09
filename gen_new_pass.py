import sqlite3 as sl
import random
import string

def db_start():
    global db,cur
    db = sl.connect('database_project.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS curators(curator_id INTEGER PRIMARY KEY, curator_fio TEXT, chat_id TEXT, password TEXT)")
    db.commit()

db_start()


def generate_password(length):
    letters = string.ascii_letters + string.digits
    password = ''.join(random.choice(letters) for i in range(length))
    return password

def pas_update():
    users = cur.execute("SELECT curator_id FROM curators").fetchall()
    for i in range(len(users)+1):
        cur.execute(f"UPDATE curators SET password = '{generate_password(6)}' WHERE curator_id = '{i}'")
        db.commit()
pas_update()

