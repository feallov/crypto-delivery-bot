from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu(lang):
    builder = InlineKeyboardBuilder()
    m_text = "◌ market" if lang == 'en' else "◌ маркет"
    a_text = "✧ alerts" if lang == 'en' else "✧ уведомления"
    s_text = "⚙ settings" if lang == 'en' else "⚙ настройки"
    builder.row(InlineKeyboardButton(text=m_text, callback_data="view_market"))
    builder.row(InlineKeyboardButton(text=a_text, callback_data="manage_alerts"))
    builder.row(InlineKeyboardButton(text=s_text, callback_data="settings"))
    return builder.as_markup()

def coin_list_kb(prefix: str, lang='en'):
    builder = InlineKeyboardBuilder()
    coins = ["btc", "eth", "ton", "sol", "bnb", "xrp", "doge", "ada", "trx", "avax", "dot", "link", "ltc", "matic", "usdt"]
    for c in coins:
        builder.button(text=f"• {c}", callback_data=f"{prefix}_{c}")
    back_text = "← back" if lang == 'en' else "← назад"
    builder.button(text=back_text, callback_data="start")
    builder.adjust(3)
    return builder.as_markup()

def settings_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇸 english", callback_data="set_en"),
        InlineKeyboardButton(text="🇷🇺 русский", callback_data="set_ru")
    )
    builder.row(InlineKeyboardButton(text="← back", callback_data="start"))
    return builder.as_markup()
