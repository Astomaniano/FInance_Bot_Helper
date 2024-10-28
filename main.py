import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardMarkup

from aiogram import Bot, Dispatcher, F
from aiogram. filters import CommandStart, Command
from aiogram. types import Message, FSInputFile
from aiogram. fsm. context import FSMContext
from aiogram. fsm.state import State, StatesGroup
from aiogram. fsm. storage. memory import MemoryStorage

from config import TOKEN
import sqlite3
import aiohttp
import logging

bot = Bot(token=TOKEN)
dp = Dispatcher()

#Добавляем логирование
logging.basicConfig(level=logging.INFO)

#Добавляем клавиатуру
button_register = KeyboardButton(text = 'Регистрация в боте')
button_exchange = KeyboardButton(text = 'Курс валют')
button_tips = KeyboardButton(text = 'Советы по экономии')
button_finance = KeyboardButton(text = 'Личные Финансы')

keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_register, button_exchange],
    [button_tips, button_finance]
    ], resize_keyboard=True)

#Создаем БД
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
    )
''')

conn.commit()

class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

@dp.message(CommandStart)
async def command_start(message: Message):
    await message.answer(f'Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:', reply_markup=keyboard)

@dp.message(F.text == 'Регистрация в боте')
async def register(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer(f'Вы уже зарегистрированы в боте. Выберите одну из опций в меню:', reply_markup=keyboard)
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer(f'Вы успешно зарегистрированы в боте. Выберите одну из опций в меню:', reply_markup=keyboard)

@dp.message(F.text == 'Курс валют')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())