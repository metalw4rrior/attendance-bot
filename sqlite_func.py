import sqlite3 as sl
async def db_start():
    global db,cur
    db = sl.connect('database_project.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS curators(curator_id INTEGER PRIMARY KEY, curator_fio TEXT, chat_id TEXT, password TEXT)")
    db.commit()


async def edit_profile(password, chat_id):
    password = str(password)
    chat_id = str(chat_id)
    cur.execute(f"UPDATE curators SET chat_id = '{chat_id}' WHERE password = '{password}'")
    db.commit()

# Эта функция проверяет, есть ли в базе id куратора
async def curator_cheker(chat_id):
    info = cur.execute(f'SELECT chat_id FROM curators WHERE chat_id={chat_id}').fetchone()
    if info is None: 
        return True
    

async def password_cheker(password):
    password = str(password)
    info = cur.execute(f"SELECT password FROM curators WHERE password='{password}'").fetchone()
    if info is None: 
        return True

# Я думаю, можно назвать это говнокодом
# Ввод статистики в бд
async def in_dbase(group_name, disrespectful_reason, valid_reason, disease_reason, present, user_id, date_of_report):
    curator_fio = str(cur.execute(f"SELECT curator_fio FROM curators WHERE chat_id='{user_id}'").fetchone())
    delete = {ord('(') : None, ord(')') : None, ord(',') : None, ord('\'') : None}
    curator_fio = curator_fio.translate(delete)
    cur.execute(f"""INSERT INTO attendance_report 
    (group_name, curator_fio, date_of_report, valid_reason, disrespectful_reason, disease_reason, who_is_present)
    VALUES ("{group_name}", "{curator_fio}", '{date_of_report}', {valid_reason}, {disrespectful_reason}, {disease_reason}, {present})""")
    db.commit()

# Эта гавнина работает PogChamp :V
# Высчитывает присутствующих
async def all_that_present(disrespectful_reason, valid_reason, disease_reason, user_id):
    curator_db_id = str(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id='{user_id}'").fetchone())
    delete = {ord('(') : None, ord(')') : None, ord(',') : None, ord('\'') : None}
    curator_db_id = curator_db_id.translate(delete)
    how_much = str(cur.execute(f"SELECT how_much FROM groups WHERE curator_id='{curator_db_id}'").fetchone())
    how_much = int(how_much.translate(delete))
    present = how_much - disrespectful_reason - valid_reason - disease_reason
    if present >= 0:
        return present

# Функция, которая выводит группы
async def get_unoccupied_groups(user_id):
    curator_id = str(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id='{user_id}'").fetchone())
    delete = {ord('(') : None, ord(')') : None, ord(',') : None}
    curator_id = curator_id.translate(delete)
    info = str(cur.execute(f'SELECT group_name FROM groups WHERE curator_id="{curator_id}"').fetchall())
    delete = {ord('[') : None, ord(']') : None, ord('(') : None, ord(')') : None, ord(',') : None, ord("'") : None}
    info = info.translate(delete).split()
    if len(info)>1:
        info = [info[i] + ' ' + info[i+1] for i in range(0, len(info), 2)]
    return info

# Проверка записей на текущий день
async def record_checker(date_of_report, group_name):
    info = cur.execute(f"SELECT group_name FROM attendance_report WHERE date_of_report='{date_of_report}'").fetchone()
    if info is None:
        print(info)
        return True
