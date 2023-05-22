from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
import sqlite3 as sl

# git test

# Хз как запихать в sqlite_func, у меня ошибка вылазит :Р
db = sl.connect('database_project.db')
cur = db.cursor()

def get_unoccupied_groups():
    info = str(cur.execute('SELECT group_name FROM groups WHERE curator_id is NULL').fetchall())
    # Эта ерунда убирает символы. Иначе было бы вот так - [('ИБАС21-11',), ('ИСИП22-11',), ...
    delete = {ord('[') : None, ord(']') : None, ord('(') : None, ord(')') : None, ord(',') : None, ord("'") : None}
    info = info.translate(delete).split()
    return info

# Имена кнопок
grp_btns_names = get_unoccupied_groups()

# Клава с кнопками, правда кнопки все широкие
kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
for i in grp_btns_names:
    button = KeyboardButton(i)
    kb_groups.add(button)


kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("/vvod")
b2 = KeyboardButton("/description")
b3 = KeyboardButton("/help")
b4 = KeyboardButton("/settings")
kb.add(b1,b2).add(b3,b4)


HELP_COMMAND = """
/help - список команд
/description - описание бота
"""

