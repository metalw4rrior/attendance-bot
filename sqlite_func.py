import sqlite3 as sl
async def db_start():
    global db,cur
    db = sl.connect('database_project.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS curators(curator_id INTEGER PRIMARY KEY, curator_fio TEXT, chat_id TEXT, password TEXT)")
    db.commit()

# async def curators_values(chat_id):
#     chat_id = str(chat_id)
#     cur.execute = ("""INSERT INTO curators(chat_id) VALUES (?) """)
#     # cur.execute(" INSERT INTO curators SET chat_id = (?)",(chat_id))
#     db.commit()

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

''' Проблема только с выбором группы
async def in_dbase(present, disrespectful_reason, valid_reason, disease_reason, user_id, date_of_report):
    curator_id = str(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id='{user_id}'").fetchone())
    delete = {ord('(') : None, ord(')') : None, ord(',') : None}
    curator_id = curator_id.translate(delete)

    sql = f"""INSERT INTO attendance_report 
    (group_id, curator_id, date_of_report, valid_reason, disrespectful_reason, disease_reason, who_is_present)
    VALUES ('{curator_id}', ?, '{date_of_report}', {valid_reason}, {disrespectful_reason}, {disease_reason}, {present})"""
'''
### Перенес в buttons.py :Р ###

# # Функция, которая выводит группы без куратора. Потом можно переделать под выбор группы для ввода посещения
# async def get_unoccupied_groups():
#     info = str(cur.execute('SELECT group_name FROM groups WHERE curator_id is NULL').fetchall())
#     # Эта ерунда убирает символы. Иначе это бы было вот так - [('ИБАС21-11',), ('ИСИП22-11',), ...
#     delete = {ord('[') : None, ord(']') : None, ord('(') : None, ord(')') : None, ord(',') : None, ord("'") : None}
#     info = info.translate(delete).split()
#     return info


