from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
import sqlite3 as sl
from sqlite_func import get_unoccupied_groups

db = sl.connect('database_project.db')
cur = db.cursor()


# Клава с кнопками, правда кнопки все широкие
kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
# for i in grp_btns_names:
#     button = KeyboardButton(i)
#     kb_groups.add(button)


kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("Ввод статистики")
b2 = KeyboardButton("Описание")
kb.add(b1,b2)

