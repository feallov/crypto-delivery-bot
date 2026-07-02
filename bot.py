import asyncio, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from api_service import BinanceAPI
import keyboards as kb
import database as db
from strings import texts

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

class AlertSetup(StatesGroup):
    choosing_coin = State()
    entering_price = State()
    entering_spam = State()

# Функция для быстрой стилизации текста
def style(text):
    return f"<b>{text.lower()}</b>"

@dp.message(Command("start"))
async def start(m: types.Message):
    user = await db.get_user(m.from_user.id)
    await m.answer(style(texts[user.lang]['welcome']), reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

# --- СОЗДАНИЕ ПЕРСОНАЛЬНОГО АЛЕРТА ---

@dp.callback_query(F.data == "manage_alerts")
async def start_alert_setup(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text(style("select coin for alert:"), reply_markup=kb.coin_list_kb("alertcoin", user.lang), parse_mode=ParseMode.HTML)
    await state.set_state(AlertSetup.choosing_coin)

@dp.callback_query(AlertSetup.choosing_coin, F.data.startswith("alertcoin_"))
async def alert_coin_chosen(call: types.CallbackQuery, state: FSMContext):
    coin = call.data.split("_")[1]
    await state.update_data(coin=coin)
    data = await BinanceAPI.get_ticker_data(coin)
    await call.message.edit_text(style(f"current {coin} price: ${data['price']}\n\nenter target price:"), parse_mode=ParseMode.HTML)
    await state.set_state(AlertSetup.entering_price)

@dp.message(AlertSetup.entering_price)
async def alert_price_entered(m: types.Message, state: FSMContext):
    try:
        price = float(m.text.replace(',', '.'))
        await state.update_data(price=price)
        await m.answer(style("how many times to spam? (1-10):"), parse_mode=ParseMode.HTML)
        await state.set_state(AlertSetup.entering_spam)
    except:
        await m.answer(style("enter a valid number"))

@dp.message(AlertSetup.entering_spam)
async def alert_spam_entered(m: types.Message, state: FSMContext):
    try:
        spam = int(m.text)
        if not 1 <= spam <= 10: raise ValueError()
        
        data = await state.get_data()
        coin_data = await BinanceAPI.get_ticker_data(data['coin'])
        direction = "up" if data['price'] > coin_data['price'] else "down"
        
        await db.add_alert(m.from_user.id, data['coin'], data['price'], direction, spam)
        await m.answer(style(f"alert set!\n{data['coin']} {direction} to {data['price']}\nspam: {spam} times"), parse_mode=ParseMode.HTML)
        await state.clear()
    except:
        await m.answer(style("enter a number between 1 and 10"))

# --- МОНИТОРИНГ ---

async def alert_monitor():
    while True:
        try:
            alerts = await db.get_active_alerts()
            for a in alerts:
                data = await BinanceAPI.get_ticker_data(a.symbol)
                if not data: continue
                
                triggered = False
                if a.direction == "up" and data['price'] >= a.target_price: triggered = True
                elif a.direction == "down" and data['price'] <= a.target_price: triggered = True
                
                if triggered:
                    msg = style(f"⚠️ {a.symbol} target hit!\nprice: ${data['price']}")
                    for _ in range(a.spam_count):
                        try:
                            await bot.send_message(a.user_id, msg, parse_mode=ParseMode.HTML)
                            await asyncio.sleep(0.3)
                        except: break
                    await db.deactivate_alert(a.id)
        except: pass
        await asyncio.sleep(20)

# --- ОСТАЛЬНОЕ ---

@dp.callback_query(F.data == "view_market")
async def market(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text(style("market:"), reply_markup=kb.coin_list_kb("coin", user.lang), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data.startswith("coin_"))
async def coin_info(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    coin = call.data.split("_")[1]
    data = await BinanceAPI.get_ticker_data(coin)
    if data:
        status = texts[user.lang]['price_up'] if data['change'] > 0 else texts[user.lang]['price_down']
        res = style(f"💎 1 {data['symbol']} = ${data['price']:,.2f} {status}\n24h: {data['change']}%")
        await call.message.edit_text(res, reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "start")
async def back_home(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text(style(texts[user.lang]['welcome']), reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

async def main():
    await db.init_db()
    asyncio.create_task(alert_monitor())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
