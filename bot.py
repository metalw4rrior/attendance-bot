#!/usr/bin/env python3
import sqlite3 as sl
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import API_TOKEN
from sqlite_func import *
from buttons import kb, kb_groups, kb_start, restart_btn
from datetime import datetime
import schedule
import asyncio


storage = MemoryStorage()

# Объект бота
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)

async def on_startup(self):
    db_start()
    # В loop'е работает, хз почему
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_bot(bot)) # Принимает bot т.к. без него не отправить уведу, а импортировать в sqlite_func не особо хочется


class Pas(StatesGroup):
    password = State()       # пароль

class Attendance(StatesGroup):
    group = State()
    disrespectful_reason = State()   # Отсутствуют
    valid_reason = State()           # Уважительная
    disease_reason = State()         # Болеют
    comment = State()                # Коментарий

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    check = curator_cheker(str(message.from_user.id))
    if await check: #not in database:
        await message.answer('Добро пожаловать! Для того, чтобы продолжить работу, введите ваш пароль.')
        await Pas.password.set()
    else:
        await bot.send_message(message.from_user.id,
                               text='С возвращением! ',
                               reply_markup=kb)

@dp.message_handler(commands=["restart"])
async def restart_command(message: types.Message):
    check = curator_cheker(str(message.from_user.id))
    if await check: #not in database:
        await message.answer('С нашей стороны произошли какие-то проблемы. Пожалуйста, введите ваш пароль.')
        await Pas.password.set()
    else:
        await bot.send_message(message.from_user.id,
                               text='Бот перезагружен',
                               reply_markup=kb)

@dp.message_handler(commands=["exit"])
async def start_command(message: types.Message):
    await logout(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           text='Вы вышли из аккаунта.\nДля продолжения работы, нажмите "/start"',
                           reply_markup=kb_start)

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await logout(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           text="""Это бот для ввода статистики в КЦПТ.
                           \nДля работы с ботом, нажмите или введите "/start". После, введите пароль.
                           \nЕсли вы не получили пароль, обратитесь за ним к Гуляеву И.П.""",
                           reply_markup=kb_start)

# принимаем пасс
@dp.message_handler(state = Pas.password)
async def load_password(message: types.Message, state: FSMContext):
    pass_check = await password_cheker(message.text)
    if message.text == "/help":
        await help_command(message)
        await state.finish()
    elif pass_check: #not in database
        await message.answer('Пароль введен неверно, попробуйте снова.')
        await Pas.password.set()
    else:
        await edit_profile(message.text, message.from_user.id)
        await message.answer(text='Вы успешно прошли авторизацию.',
                             reply_markup=kb)
        await state.finish()


reason = []
@dp.message_handler(Text(equals="Ввод статистики"))
async def load_statistics(message: types.Message):
    groups = await get_unoccupied_groups(str(message.from_user.id))
    kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_groups.add(KeyboardButton("Отмена"))
    for i in groups:
        button = KeyboardButton(i)
        kb_groups.insert(button)
    kb_groups.add(restart_btn)
    await message.answer(text='Выберите группу',
                         reply_markup=kb_groups)
    await Attendance.group.set()

# ОТМЕНА
@dp.message_handler(Text(equals='Отмена'), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    reason.clear()
    await message.reply('Ввод отменен', reply_markup=kb)

@dp.message_handler(state = Attendance.group)
async def load_group(message: types.Message, state: FSMContext)-> None:
    groups = await get_unoccupied_groups(str(message.from_user.id))
    if message.text in groups:
        date_obj = datetime.now().date()
        date_str = str(date_obj.strftime('%Y-%m-%d'))
        if not await record_checker(date_str, message.text):
            # print("Заглушка") # Если надо будет добавить ограничение, то считать тут (вроде :Р)
            reason.append(message.text)     #ИМЯ ГРУППЫ [0]
            await message.answer('Обновляем данные, введите отсутствующих по НЕУВАЖИТЕЛЬНОЙ причине')
            await Attendance.disrespectful_reason.set()
        else:
            reason.append(message.text)     #ИМЯ ГРУППЫ [0]
            await message.answer('Введите количество студентов, отсутствующих по НЕУВАЖИТЕЛЬНОЙ причине')
            await Attendance.disrespectful_reason.set()
    else:
        await state.finish()
        reason.clear()
        await message.reply('Операция отменена. Ошибка в вводимых данных', reply_markup=kb)


@dp.message_handler(state = Attendance.disrespectful_reason)
async def load_reason_N(message: types.Message, state: FSMContext)-> None:
    if message.text.isdigit():
        reason.append(int(message.text))     #НЕУВАЖИТЕЛЬНАЯ ПРИЧИНА ИНДЕКС [1]
        await message.answer('Введите количество студентов, отсутствующих по УВАЖИТЕЛЬНОЙ причине')
        await Attendance.valid_reason.set()
    else:
        await state.finish()
        reason.clear()
        await message.reply('Операция отменена. Ошибка в вводимых данных', reply_markup=kb)


@dp.message_handler(state = Attendance.valid_reason)
async def load_reason_U(message: types.Message, state: FSMContext)-> None:
    if message.text.isdigit():
        reason.append(int(message.text)) #УВАЖИТЕЛЬНАЯ ПРИЧИНА ИНДЕКС [2]
        await message.answer('Введите количество студентов, отсутствующих по БОЛЕЗНИ')
        await Attendance.disease_reason.set()
    else:
        await state.finish()
        reason.clear()
        await message.reply('Операция отменена. Ошибка в вводимых данных', reply_markup=kb)


@dp.message_handler(state = Attendance.disease_reason)
async def load_reason_U(message: types.Message, state: FSMContext)-> None:
    if message.text.isdigit():
        reason.append(int(message.text)) #БОЛЕЗНЬ  ИНДЕКС [3]
        present = await all_that_present(reason[1], reason[2], reason[3], message.from_user.id)
        if present or present == 0:
            if reason[1] > 0:
                kb_groups = ReplyKeyboardMarkup(resize_keyboard=True)
                kb_groups.add(KeyboardButton("Отмена"))
                await message.answer('Введите фамилии отсутствующих по неуважительной')
                await Attendance.comment.set()
            else:
                reason.append(str("-")) # Комментарий [4]
                present = await all_that_present(reason[1], reason[2], reason[3], message.from_user.id)
                itog_percent1 = await itog_percent(reason[1], reason[2], reason[3], message.from_user.id)
                itog_percent2 = await itog_percent_u_b(reason[1], message.from_user.id)
                date_obj = datetime.now().date()   # Получаем текущую дату и преобразуем в объект даты
                date_str = str(date_obj.strftime('%Y-%m-%d'))   # Преобразуем объект даты в строку в нужном формате
                # Тут заносим
                await in_dbase(reason[0], reason[1], reason[2], reason[3], present, reason[4], date_str,itog_percent1,itog_percent2)
                reason.clear()
                await bot.send_message(message.from_user.id,
                                           text='Вы успешно ввели данные.',
                                           reply_markup=kb)
                await state.finish()
        else:
            await state.finish()
            reason.clear()
            await message.reply('Операция отменена. Превышено кол-во студентов', reply_markup=kb)
    else:
        await state.finish()
        reason.clear()
        await message.reply('Операция отменена. Ошибка в вводимых данных', reply_markup=kb)

@dp.message_handler(state = Attendance.comment)
async def load_reason_B(message: types.Message, state: FSMContext)-> None:
    reason.append(str(message.text)) # Комментарий [4]
    present = await all_that_present(reason[1], reason[2], reason[3], message.from_user.id)
    itog_percent1 = await itog_percent(reason[1], reason[2], reason[3], message.from_user.id)
    itog_percent2 = await itog_percent_u_b(reason[1], message.from_user.id)
    date_obj = datetime.now().date()   # Получаем текущую дату и преобразуем в объект даты
    date_str = str(date_obj.strftime('%Y-%m-%d'))   # Преобразуем объект даты в строку в нужном формате
    # Тут заносим
    await in_dbase(reason[0], reason[1], reason[2], reason[3], present, reason[4], date_str,itog_percent1,itog_percent2)
    reason.clear()
    await bot.send_message(message.from_user.id,
                               text='Вы успешно ввели данные.',
                               reply_markup=kb)
    await state.finish()


@dp.message_handler(Text(equals="Проверка"))
async def description_command(message: types.Message):
    date_of_report = datetime.now().strftime('%Y-%m-%d')
    stats = await check_stats(message.from_user.id, date_of_report)
    await message.answer(text=stats)

@dp.message_handler(Text(equals="Описание"))
async def description_command(message: types.Message):
    await message.answer(text='''Бот предназначен для отправки статистики по посещению.\n
Для ввода статистики, нажмите на кнопку "Ввод статистики".\n
Если вы хотите обновить статистику, нажмите на кнопку
"Ввод статистики". Новые данные перезапишут старые!\n
Для проверки статистики, нажмите "Проверка"\n
Если вы хотите отменить ввод посещения, нажмите "Отмена".\n
Если бот не реагирует на команды, нажмите на кнопку
"/restart" или введите "/restart" с клавиатуры.\n
Если вы хотите выйти из аккаунта, введите "/exit"''')

# Если вводят что угодно, кроме команд
@dp.message_handler()
async def unknown_text(message: types.Message):
    await message.answer(text="Команда не распознана")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
