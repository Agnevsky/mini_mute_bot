# keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_USERNAME = "test_work_my_bot"

# Меню в общем чате
keyboards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Регистрация в боте', url=f'https://t.me/{BOT_USERNAME}?start=register_bot')],
])

in_tournament = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Очистить таблицу', callback_data='create_tournament')],
    [InlineKeyboardButton(text='Регистрация в турнире', url=f'https://t.me/{BOT_USERNAME}?start=join_tournament')],
    [InlineKeyboardButton(text='Внести результаты игр', url=f'https://t.me/{BOT_USERNAME}?start=result_game')]
])


info_tournament = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Таблица', callback_data='table')]
])
