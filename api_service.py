import aiohttp

class BinanceAPI:
    @staticmethod
    async def get_ticker_data(symbol: str):
        # получаем данные без ключей, напрямую
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}USDT"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "symbol": symbol.lower(),
                            "price": float(data['lastPrice']),
                            "change": float(data['priceChangePercent']),
                            "high": float(data['highPrice']),
                            "low": float(data['lowPrice']),
                            "vol": float(data['quoteVolume'])
                        }
            except:
                return None
