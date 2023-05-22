import sqlite3 as sl
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import API_TOKEN
from sqlite_func import db_start, curator_cheker, password_cheker,edit_profile
from buttons import kb, HELP_COMMAND

async def on_startup(self):
    await db_start()

data = []
storage = MemoryStorage()

# Объект бота
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Id_fio(StatesGroup):
    password = State()       # пароль

# до использования этого класса мы еще не доперли.потом. 
class Attendance(StatesGroup):
    present = State()                # Присутствуют    P.C. строку с присутствующими менять я не стала, ибо в базе строка who_is_present.
    disrespectful_reason = State()   # Отсутствуют
    valid_reason = State()           # Уважительная
    disease_reason = State()         # Болеют

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    id = str(message.from_user.id)
    data.append(id) #data [0] == chat_id 
    check = curator_cheker(id)
    if await check: #not in database:
        await message.answer('Добро пожаловать. Для того, чтобы продолжить работу, введите ваш пароль в кавычках.')
        await Id_fio.password.set()
    else:
        await bot.send_message(message.from_user.id,
                               text='С возвращением! ',
                               reply_markup=kb)


# принимаем пасс
@dp.message_handler(state = Id_fio.password)
async def load_password(message: types.Message):
    pass_data = str(message.text)
    data.append(pass_data) # data[1] = password
    pass_check = password_cheker(pass_data)
    if await pass_check: #not in database
        await message.answer('Пароль введен неверно, попробуйте снова. Если вы не получили пароль, обратитесь за ним к Гуляеву И.П. ')
        await Id_fio.password.set()
    else:
        await bot.send_message(message.from_user.id,
                               text='Вы успешно прошли авторизацию. ',
                               reply_markup=kb)
    await edit_profile(data[1],data[0])
    await state.finish()

@dp.message_handler(commands="help")
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           text=HELP_COMMAND,
                           reply_markup=kb)

@dp.message_handler(commands="description")
async def help_command(message: types.Message):
    await bot.send_message(message.from_user.id,
                           text="Бот предназначен для отправки статистики по посещению")

    # Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
