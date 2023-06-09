from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
import sqlite3 as sl
from sqlite_func import get_unoccupied_groups

db = sl.connect('database_project.db')
cur = db.cursor()


start_btn = KeyboardButton("/start")
restart_btn = KeyboardButton("/restart")
help_btn = KeyboardButton("/help")

# Клава с кнопками, правда кнопки все широкие
kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_btn = KeyboardButton("Отмена")
kb_groups.add(cancel_btn)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("Ввод статистики")
b2 = KeyboardButton("Проверка")
b3 = KeyboardButton("Описание")
kb.add(b1,b2,b3).add(restart_btn)

kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_start.add(start_btn, help_btn)
