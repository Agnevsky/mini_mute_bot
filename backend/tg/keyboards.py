from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Регистрация в боте', callback_data='register_bot')],
    ])

in_tournament = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Очистить таблицу', callback_data='create_tournament')],
    [InlineKeyboardButton(text='Турнир', callback_data='join_tournament')]
    ])


info_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Таблица', callback_data='table')]])