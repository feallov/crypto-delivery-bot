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
