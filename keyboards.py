from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Новый турнир', callback_data='create_tournament')],
    
    ])

register_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Регистрация в боте', callback_data='register_bot')],
    
    ])

