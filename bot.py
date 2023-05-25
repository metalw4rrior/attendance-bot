import sqlite3 as sl
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove 
from config import API_TOKEN
from sqlite_func import db_start, curator_cheker, password_cheker, edit_profile, get_unoccupied_groups, in_dbase
from buttons import kb, kb_groups
from datetime import datetime

async def on_startup(self):
    await db_start()

storage = MemoryStorage()

# Объект бота
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Pas(StatesGroup):
    password = State()       # пароль

# до использования этого класса мы еще не доперли.потом. 
class Attendance(StatesGroup):
    group = State()
    present = State()                # Присутствуют    P.C. строку с присутствующими менять я не стала, ибо в базе строка who_is_present.
    disrespectful_reason = State()   # Отсутствуют
    valid_reason = State()           # Уважительная
    disease_reason = State()         # Болеют

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


# принимаем пасс
@dp.message_handler(state = Pas.password)
async def load_password(message: types.Message, state: FSMContext):
    pass_check = password_cheker(str(message.text))
    if await pass_check: #not in database
        await message.answer('Пароль введен неверно, попробуйте снова. Если вы не получили пароль, обратитесь за ним к Гуляеву И.П. ')
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
    # print(groups)
    for i in groups:
        button = KeyboardButton(i)
        kb_groups.add(button)
    await message.answer(text='Ввыберите группу',
                         reply_markup=kb_groups)
    await Attendance.group.set()

@dp.message_handler(state = Attendance.group)
async def load_group(message: types.Message, state: FSMContext)-> None:
    reason.append(message.text)     #ИМЯ ГРУППЫ [0]
    await message.answer('Введите количество студентов, отсутствующих по НЕУВАЖИТЕЛЬНОЙ причине')
    await Attendance.disrespectful_reason.set()

@dp.message_handler(state = Attendance.disrespectful_reason)
async def load_reason_N(message: types.Message, state: FSMContext)-> None:
    reason.append(str(message.text))     #НЕУВАЖИТЕЛЬНАЯ ПРИЧИНА ИНДЕКС [1]
    await message.answer('Введите количество студентов, отсутствующих по УВАЖИТЕЛЬНОЙ причине')
    await Attendance.valid_reason.set()

@dp.message_handler(state = Attendance.valid_reason)
async def load_reason_U(message: types.Message, state: FSMContext)-> None:
    reason.append(int(message.text)) #УВАЖИТЕЛЬНАЯ ПРИЧИНА ИНДЕКС [2]
    await message.answer('Введите количество студентов, отсутствующих по БОЛЕЗНИ')
    await Attendance.disease_reason.set()

@dp.message_handler(state = Attendance.disease_reason)
async def load_reason_B(message: types.Message, state: FSMContext)-> None:
    reason.append(int(message.text)) #БОЛЕЗНЬ  ИНДЕКС [3]
    await message.answer('Введите количество студентов, ПРИСУТСТВУЮЩИХ на паре')
    await Attendance.present.set()

@dp.message_handler(state = Attendance.present)
async def load_reason_B(message: types.Message, state: FSMContext)-> None:
    reason.append(int(message.text)) #КТО ЗДЕСЬ ИНДЕКС [4]
    # print(reason)
    date_obj = datetime.now().date()   # Получаем текущую дату и преобразуем в объект даты
    date_str = str(date_obj.strftime('%Y-%m-%d'))   # Преобразуем объект даты в строку в нужном формате
    # Тут заносим
    await in_dbase(reason[0], reason[1], reason[2], reason[3], reason[4], message.from_user.id, date_str)
    await bot.send_message(message.from_user.id,
                               text='Вы успешно ввели данные.',
                               reply_markup=kb)
    await state.finish()

@dp.message_handler(Text(equals="Описание"))
async def description_command(message: types.Message):
    await message.answer(text="Бот предназначен для отправки статистики по посещению")

    # Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
