from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
import sqlite3 as sl
from sqlite_func import get_unoccupied_groups

db = sl.connect('database_project.db')
cur = db.cursor()


start_btn = KeyboardButton("/restart")

# Клава с кнопками, правда кнопки все широкие
kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_btn = KeyboardButton("Отмена")
kb_groups.add(cancel_btn)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("Ввод статистики")
b2 = KeyboardButton("Описание")
kb.add(b1,b2).add(start_btn)

