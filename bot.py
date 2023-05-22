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

storage = MemoryStorage()

# Объект бота
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Pas(StatesGroup):
    password = State()       # пароль

# до использования этого класса мы еще не доперли.потом. 
class Attendance(StatesGroup):
    present = State()                # Присутствуют    P.C. строку с присутствующими менять я не стала, ибо в базе строка who_is_present.
    disrespectful_reason = State()   # Отсутствуют
    valid_reason = State()           # Уважительная
    disease_reason = State()         # Болеют

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    check = curator_cheker(str(message.from_user.id))
    if await check: #not in database:
        await message.answer('Добро пожаловать. Для того, чтобы продолжить работу, введите ваш пароль.')
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
        await bot.send_message(message.from_user.id,
                               text='Вы успешно прошли авторизацию. ',
                               reply_markup=kb)

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
