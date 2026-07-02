import asyncio
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from api_service import BinanceAPI
import keyboards as kb
from strings import texts
import database as db

# Загрузка токена
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("ERROR: BOT_TOKEN not found!")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Веб-сервер для Render (порт 10000)
async def handle(request):
    return web.Response(text="bot is alive")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# Обработчики
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = await db.get_user(message.from_user.id)
    await message.answer(texts[user.lang]['welcome'], reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "start")
async def back_home(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    await callback.message.edit_text(texts[user.lang]['welcome'], reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "view_market")
async def market_detail(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    data = await BinanceAPI.get_ticker_data("btc")
    if data:
        status = texts[user.lang]['price_up'] if data['change'] > 0 else texts[user.lang]['price_down']
        res = (
            f"💎 <b>1 {data['symbol']} = ${data['price']:,.2f}</b> {status} ▲ <b>{data['change']}%</b>\n\n"
            f"<b>range 24h:</b> <code>{data['low']:,.0f}</code> — <code>{data['high']:,.0f}</code>\n"
            f"<b>vol 24h:</b> <code>{data['vol']/1000000:.1f}m</code>"
        ).lower()
        await callback.message.edit_text(res, reply_markup=kb.main_menu(user.lang), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    await callback.message.edit_text("<b>settings</b>", reply_markup=kb.settings_menu(), parse_mode=ParseMode.HTML)

@dp.callback_query(F.data.startswith("set_"))
async def set_lang(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    await db.update_user(callback.from_user.id, lang=lang)
    await callback.answer(texts[lang]['lang_set'])
    await back_home(callback)

# Микро-спам (фоновый мониторинг)
async def price_monitor():
    last_price = 0
    while True:
        try:
            data = await BinanceAPI.get_ticker_data("btc")
            if data and last_price != 0:
                diff = abs(data['price'] - last_price) / last_price
                if diff > 0.01: # 1% изменение
                    # Тут можно добавить логику рассылки всем юзерам
                    last_price = data['price']
            elif data:
                last_price = data['price']
        except:
            pass
        await asyncio.sleep(60)

async def main():
    if not os.getenv("DATABASE_URL"):
        print("ERROR: DATABASE_URL not found!")
        return
    
    await db.init_db()
    asyncio.create_task(start_webserver())
    asyncio.create_task(price_monitor())
    print("--- BOT STARTED ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# 1. Изменяем обработчик вызова меню рынка
@dp.callback_query(F.data == "view_market")
async def show_market_menu(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    # Показываем меню выбора монет
    await callback.message.edit_text(
        "<b>select asset:</b>", 
        reply_markup=kb.market_menu(), 
        parse_mode=ParseMode.HTML
    )

# 2. Добавляем обработчик для выбора конкретной монеты
@dp.callback_query(F.data.startswith("coin_"))
async def coin_detail(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    ticker = callback.data.split("_")[1] # получаем 'btc', 'ton' или 'usdt'
    
    data = await BinanceAPI.get_ticker_data(ticker)
    
    if data:
        # Логика статуса цены
        status = texts[user.lang].get('price_up', '▲') if data['change'] > 0 else texts[user.lang].get('price_down', '▼')
        
        # Собираем сообщение (в твоем стиле)
        res = (
            f"💎 <b>1 {data['symbol']} = ${data['price']:,.2f}</b> {status} ▲ <b>{data['change']}%</b>\n\n"
            f"<b>range 24h:</b> <code>{data['low']:,.0f}</code> — <code>{data['high']:,.0f}</code>\n"
            f"<b>vol 24h:</b> <code>{data['vol']/1000000:.1f}m</code>"
        ).lower()
        
        # Отправляем с кнопкой возврата в маркет-меню
        await callback.message.edit_text(
            res, 
            reply_markup=kb.market_menu(), 
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.answer("error fetching data")
