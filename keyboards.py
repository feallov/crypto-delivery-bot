from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(lang):
    m_text = "◌ market" if lang == 'en' else "◌ маркет"
    a_text = "✧ alerts" if lang == 'en' else "✧ уведомления"
    s_text = "⚙ settings" if lang == 'en' else "⚙ настройки"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=m_text, callback_data="view_market"))
    builder.row(
        InlineKeyboardButton(text=a_text, callback_data="manage_alerts"),
        InlineKeyboardButton(text=s_text, callback_data="settings")
    )
    return builder.as_markup()

def settings_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇸 english", callback_data="set_en"),
        InlineKeyboardButton(text="🇷🇺 русский", callback_data="set_ru")
    )
    builder.row(InlineKeyboardButton(text="← back", callback_data="start"))
    return builder.as_markup()
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def main_menu(lang):
    # Твоя текущая главная клавиатура, добавляем кнопку выбора рынка
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 market", callback_query_id="view_market")
    builder.button(text="⚙️ settings", callback_query_id="settings")
    builder.adjust(1)
    return builder.as_markup()

def market_menu():
    builder = InlineKeyboardBuilder()
    # Список монет: (Название для кнопки, тикер для API)
    coins = [
        ("btc", "btc"),
        ("ton (gram)", "ton"),
        ("usdt", "usdt")
    ]
    for name, ticker in coins:
        builder.button(text=name, callback_query_data=f"coin_{ticker}")
    
    builder.button(text="« back", callback_query_data="start")
    builder.adjust(2) # Кнопки по 2 в ряд
    return builder.as_markup()
