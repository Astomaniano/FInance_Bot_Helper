import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardMarkup

from aiogram import Bot, Dispatcher, F
from aiogram. filters import CommandStart, Command
from aiogram. types import Message, FSInputFile
from aiogram. fsm. context import FSMContext
from aiogram. fsm.state import State, StatesGroup
from aiogram. fsm. storage. memory import MemoryStorage

from config import TOKEN, EXCHANGE_API_KEY
import sqlite3
import aiohttp
import logging
import requests
import random

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

@dp.message(Command('start'))
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
async def exchange(message: Message):
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD'
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer('Не удалось получить данные о курсе валют!')
            return
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']

        euro_to_rub = eur_to_usd * usd_to_rub
        await message.answer(f'Курс доллара к рублю: {usd_to_rub:.2f} RUB\n'
                             f'Курс евро к рублю: {euro_to_rub:.2f} RUB')

    except:
        await message.answer('Произошла ошибка')

@dp.message(F.text == 'Советы по экономии')
async def send_tips(message: Message):
    tips =[
        'Составляйте бюджет: Определите свои доходы и расходы. Создайте бюджет и придерживайтесь его, чтобы контролировать свои финансовые потоки.',
        'Следите за расходами: Ведите учёт всех расходов, даже самых мелких. Это поможет понять, куда уходят деньги, и выявить возможности для экономии.',
        'Сравнивайте цены: Перед покупкой изучите предложения разных продавцов. Используйте приложения и сайты для сравнения цен и поиска скидок.',
        'Покупайте оптом: Некоторые товары дешевле покупать в большем объёме. Это касается продуктов питания, бытовой химии и других товаров длительного хранения.',
        'Используйте скидки и купоны: Следите за акциями и распродажами. Используйте купоны и промокоды, чтобы сэкономить на покупках.',
        'Избегайте импульсивных покупок: Прежде чем что-то купить, подумайте, действительно ли вам это нужно. Дайте себе время на раздумья, особенно если речь идет о крупных тратах.',
        'Готовьте дома: Питание в кафе и ресторанах обходится дороже, чем приготовление еды дома. Планируйте меню и готовьте заранее.',
        'Экономьте на развлечениях: Ищите бесплатные или недорогие варианты отдыха, такие как прогулки на свежем воздухе, посещение бесплатных мероприятий или просмотр фильмов дома.',
        'Оптимизируйте коммунальные услуги: Следите за потреблением электроэнергии и воды. Устанавливайте энергосберегающие лампочки и не забывайте выключать свет, когда выходите из комнаты.',
        'Создавайте финансовую подушку**: Откладывайте часть дохода на сберегательный счёт. Это поможет избежать долгов в случае непредвиденных расходов.'
    ]
    tip = random.choice(tips)
    await message.answer(tip)

#Личные Финансы
@dp.message(F.text == 'Личные Финансы')
async def personal_finances(message: Message, state: FSMContext):
    await state.set_state(FinancesForm.category1)
    await message.reply('Введите первую категорию:')

@dp.message(FinancesForm.category1)
async def personal_finances(message: Message, state: FSMContext):
    await state.update_data(category1 = message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply('Введите расходы для категории 1:')

@dp.message(FinancesForm.expenses1)
async def personal_finances(message: Message, state: FSMContext):
    await state.update_data(expenses1 = float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply('Введите вторую категорию:')

@dp.message(FinancesForm.category2)
async def personal_finances(message: Message, state: FSMContext):
    await state.update_data(category2 = message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply('Введите расходы для категории 2')

@dp.message(FinancesForm.expenses2)
async def personal_finances(message: Message, state: FSMContext):
    await state.update_data(expenses2 = float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply('Введите третью категорию')

@dp.message(FinancesForm.category3)
async def personal_finances(message: Message, state: FSMContext):
    await state.update_data(category3 = message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply('Введите расходы для категории 3')

@dp.message(FinancesForm.expenses3)
async def personal_finances(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    cursor.execute('''
    UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
                   (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], float(message.text), telegram_id)
                   )
    conn.commit()
    await state.clear()
    await message.answer('Категории и расходы сохранены!')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())