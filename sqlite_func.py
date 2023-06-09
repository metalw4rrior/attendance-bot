import sqlite3 as sl
from datetime import datetime
import schedule
import asyncio

def db_start():
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

async def logout(chat_id):
    cur.execute(f"UPDATE curators SET chat_id = '' WHERE chat_id = '{chat_id}'")
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
async def in_dbase(group_name, disrespectful_reason, valid_reason, disease_reason, present, comment, date_of_report, itog_percent1, itog_percent2):
    cur.execute(f"""UPDATE attendance_report SET
    valid_reason = {valid_reason},
    disrespectful_reason = {disrespectful_reason},
    disease_reason = {disease_reason},
    who_is_present = {present},
    comment = "{comment}",
    itog_percent = "{itog_percent1}",
    itog_u_b = "{itog_percent2}"
    WHERE date_of_report = '{date_of_report}' and group_name = '{group_name}'""")
    db.commit()


# Эта гавнина работает PogChamp :V
# Высчитывает присутствующих
async def all_that_present(disrespectful_reason, valid_reason, disease_reason, user_id):
    curator_db_id = list(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id='{user_id}'").fetchone())[0]
    how_much = list(cur.execute(f"SELECT how_much FROM groups WHERE curator_id='{curator_db_id}'").fetchone())[0]
    present = how_much - disrespectful_reason - valid_reason - disease_reason
    if present >= 0:
        return present

# Высчитывает проценты посещаемости без у и б
async def itog_percent(disrespectful_reason, valid_reason, disease_reason, user_id):
    curator_db_id = list(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id=?", (user_id,)).fetchone())[0]
    how_much = list(cur.execute(f"SELECT how_much FROM groups WHERE curator_id=?", (curator_db_id,)).fetchone())[0]
    itog_percent1 = ((how_much - disrespectful_reason - valid_reason - disease_reason) / how_much) * 100
    itog_percent1 = str(round(itog_percent1))+'%'
    return itog_percent1

# Высчитывает проценты посещаемости с у и б
async def itog_percent_u_b(disrespectful_reason, user_id):
    curator_db_id = list(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id=?", (user_id,)).fetchone())[0]
    how_much = list(cur.execute(f"SELECT how_much FROM groups WHERE curator_id=?", (curator_db_id,)).fetchone())[0]
    itog_percent1 = ((how_much - disrespectful_reason) / how_much) * 100
    itog_percent_u_b = str(round(itog_percent1))+'%'
    return itog_percent_u_b

# Функция, которая выводит группы
async def get_unoccupied_groups(user_id):
    curator_id = list(cur.execute(f"SELECT curator_id FROM curators WHERE chat_id='{user_id}'").fetchone())[0]
    info = cur.execute(f'SELECT group_name FROM groups WHERE curator_id="{curator_id}"').fetchall()
    info = [list(i)[0] for i in info]
    return info

# Достает фио куратора по chat_id
async def get_curator_fio(user_id):
    curator_fio = list(cur.execute(f"SELECT curator_fio FROM curators WHERE chat_id='{user_id}'").fetchone())[0]
    return curator_fio

# Вытаскивает группу и введенные данные в список
async def get_stats(user_id, date_of_report):
    fio = await get_curator_fio(user_id)
    stats = list(cur.execute(f"""SELECT group_name, disrespectful_reason, valid_reason, disease_reason
                            FROM attendance_report
                            WHERE date_of_report = '{date_of_report}' and curator_fio = '{fio}' """).fetchall())
    stats = [list(i) for i in stats]
    return stats

# Функция спецом для кнопки
async def check_stats(user_id, date_of_report):
    stats = await get_stats(user_id, date_of_report)
    curator_fio = await get_curator_fio(user_id)
    answer = f"Куратор - {curator_fio}\n\n"
    for i in stats:
        if i[1] == "-" or i[2] == "-" or i[3] == "-":
            answer += f'Группа "{i[0]}" не заполнена\n\n'
        else:
            answer += f'В группе "{i[0]}" отсутствуют: по неуважительной {i[1]}, по уважительной {i[2]}, по болезни {i[3]}\n\n'
    return answer

# По сути, это таже функция, что и check_stats, но для уведомлений
async def check_stats_notify(user_id, date_of_report):
    stats = await get_stats(user_id, date_of_report)
    for i in stats:
        if i[1] == "-" or i[2] == "-" or i[3] == "-":
            return True

# Проверка записей на текущий день
async def record_checker(date_of_report, group_name):
    info = cur.execute(f"""SELECT valid_reason FROM attendance_report
                       WHERE date_of_report='{date_of_report}' and group_name='{group_name}'""").fetchone()
    if info[0] == "-":
        return True

# Проверка на наличие даты
def check():
    date_of_report = datetime.now().strftime('%Y-%m-%d')
    info = cur.execute(f"select * from attendance_report where date_of_report='{date_of_report}'").fetchone()
    if info is None:
        return True

async def new_day():
    if check(): # если записей с датой нет, то добавит незаполненные группы и фио
        date_of_report = datetime.now().strftime('%Y-%m-%d')
        cur.execute(f"""INSERT INTO attendance_report
        (group_name, curator_fio, date_of_report, valid_reason, disrespectful_reason, disease_reason, who_is_present, itog_percent, itog_u_b)
        SELECT group_name, curator_fio, '{date_of_report}', "-", "-", "-", "-", "-", "-" FROM groups JOIN curators ON groups.curator_id = curators.curator_id""")
        db.commit()

# Уведомления и новый день
def get_users_from_database():
    conn = sl.connect('database_project.db')
    cursor = conn.cursor()
    users = cursor.execute("SELECT chat_id FROM curators where chat_id not like 'None'").fetchall()
    conn.close()
    chat_ids = [int(id[0]) for id in users if id[0] is not None and id[0].isdigit()]
    return chat_ids

async def send_notification(user_id, bot):
    await bot.send_message(user_id, "Введите посещаемость")

async def schedule_bot(bot):
    USERS = get_users_from_database()
    while True:
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_day = datetime.today().strftime("%A")
        # Уведомление кроме воскресенья
        if current_day != "Sunday":
            if current_time == "12:00" or current_time == "15:00":
                for user_id in USERS:
                    if await check_stats_notify(user_id, current_date): # Проверяет введены ли данные
                        await send_notification(user_id, bot)
            # Новый день
            if current_time == "00:01" or current_time == "01:00": # час ночи на всякий случай
                await new_day()
        await asyncio.sleep(60)  # Проверяем каждую минуту



