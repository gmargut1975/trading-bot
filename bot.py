import os
import time
import schedule
import requests
from anthropic import Anthropic
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

# Configuración
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Clientes
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
anthropic_client = Anthropic()

# Acciones a seguir
SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def get_prices():
    prices = {}
    for symbol in SYMBOLS:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = data_client.get_stock_latest_quote(request)
        prices[symbol] = round((quote[symbol].ask_price + quote[symbol].bid_price) / 2, 2)
    return prices

def get_portfolio():
    account = trading_client.get_account()
    positions = trading_client.get_all_positions()
    portfolio = {
        "cash": round(float(account.cash), 2),
        "portfolio_value": round(float(account.portfolio_value), 2),
        "positions": {p.symbol: {"qty": float(p.qty), "current_price": float(p.current_price), "market_value": float(p.market_value), "unrealized_pl": float(p.unrealized_pl)} for p in positions}
    }
    return portfolio

def ask_claude(prices, portfolio):
    prompt = f"""Eres un gestor de inversiones conservador. Tu objetivo es hacer crecer una cartera pequeña de forma prudente.

Estado actual de la cartera:
- Cash disponible: ${portfolio['cash']}
- Valor total: ${portfolio['portfolio_value']}
- Posiciones abiertas: {portfolio['positions']}

Precios actuales:
{prices}

Acciones disponibles para operar: {SYMBOLS}

Basándote en esta información, decide qué hacer. Puedes:
- Comprar fracciones de acciones (mínimo $1)
- Vender posiciones existentes
- No hacer nada si no hay oportunidad clara

Responde SOLO en este formato JSON exacto:
{{
  "accion": "comprar" | "vender" | "esperar",
  "symbol": "AAPL" | "MSFT" | "GOOGL" | null,
  "cantidad_dolares": numero | null,
  "razon": "explicación breve"
}}"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import json
    text = response.content[0].text
    # Limpiar posibles markdown
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def execute_decision(decision, prices):
    accion = decision["accion"]
    symbol = decision["symbol"]
    razon = decision["razon"]

    if accion == "esperar":
        send_telegram(f"⏳ Sin operaciones. Motivo: {razon}")
        return

    if accion == "comprar" and symbol and decision["cantidad_dolares"]:
        cantidad = decision["cantidad_dolares"]
        order = MarketOrderRequest(
            symbol=symbol,
            notional=cantidad,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        trading_client.submit_order(order)
        send_telegram(f"✅ COMPRA: ${cantidad} de {symbol} a ${prices[symbol]}\n📝 {razon}")

    elif accion == "vender" and symbol:
        positions = trading_client.get_all_positions()
        for p in positions:
            if p.symbol == symbol:
                order = MarketOrderRequest(
                    symbol=symbol,
                    qty=float(p.qty),
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                trading_client.submit_order(order)
                send_telegram(f"🔴 VENTA: {p.qty} acciones de {symbol} a ${prices[symbol]}\n📝 {razon}")

def run():
    try:
        send_telegram("🤖 Analizando mercado...")
        prices = get_prices()
        portfolio = get_portfolio()
        decision = ask_claude(prices, portfolio)
        execute_decision(decision, prices)
    except Exception as e:
        send_telegram(f"⚠️ Error: {str(e)}")

# Ejecutar cada 30 minutos en horario de mercado (UTC)
schedule.every().monday.at("13:30").do(run)
schedule.every().monday.at("14:00").do(run)
schedule.every().monday.at("14:30").do(run)
schedule.every().monday.at("15:00").do(run)
schedule.every().monday.at("15:30").do(run)
schedule.every().monday.at("16:00").do(run)
schedule.every().monday.at("16:30").do(run)
schedule.every().monday.at("17:00").do(run)
schedule.every().monday.at("17:30").do(run)
schedule.every().monday.at("18:00").do(run)
schedule.every().monday.at("18:30").do(run)
schedule.every().monday.at("19:00").do(run)
schedule.every().tuesday.at("13:30").do(run)
schedule.every().tuesday.at("14:00").do(run)
schedule.every().tuesday.at("14:30").do(run)
schedule.every().tuesday.at("15:00").do(run)
schedule.every().tuesday.at("15:30").do(run)
schedule.every().tuesday.at("16:00").do(run)
schedule.every().tuesday.at("16:30").do(run)
schedule.every().tuesday.at("17:00").do(run)
schedule.every().tuesday.at("17:30").do(run)
schedule.every().tuesday.at("18:00").do(run)
schedule.every().tuesday.at("18:30").do(run)
schedule.every().tuesday.at("19:00").do(run)
schedule.every().wednesday.at("13:30").do(run)
schedule.every().wednesday.at("14:00").do(run)
schedule.every().wednesday.at("14:30").do(run)
schedule.every().wednesday.at("15:00").do(run)
schedule.every().wednesday.at("15:30").do(run)
schedule.every().wednesday.at("16:00").do(run)
schedule.every().wednesday.at("16:30").do(run)
schedule.every().wednesday.at("17:00").do(run)
schedule.every().wednesday.at("17:30").do(run)
schedule.every().wednesday.at("18:00").do(run)
schedule.every().wednesday.at("18:30").do(run)
schedule.every().wednesday.at("19:00").do(run)
schedule.every().thursday.at("13:30").do(run)
schedule.every().thursday.at("14:00").do(run)
schedule.every().thursday.at("14:30").do(run)
schedule.every().thursday.at("15:00").do(run)
schedule.every().thursday.at("15:30").do(run)
schedule.every().thursday.at("16:00").do(run)
schedule.every().thursday.at("16:30").do(run)
schedule.every().thursday.at("17:00").do(run)
schedule.every().thursday.at("17:30").do(run)
schedule.every().thursday.at("18:00").do(run)
schedule.every().thursday.at("18:30").do(run)
schedule.every().thursday.at("19:00").do(run)
schedule.every().friday.at("13:30").do(run)
schedule.every().friday.at("14:00").do(run)
schedule.every().friday.at("14:30").do(run)
schedule.every().friday.at("15:00").do(run)
schedule.every().friday.at("15:30").do(run)
schedule.every().friday.at("16:00").do(run)
schedule.every().friday.at("16:30").do(run)
schedule.every().friday.at("17:00").do(run)
schedule.every().friday.at("17:30").do(run)
schedule.every().friday.at("18:00").do(run)
schedule.every().friday.at("18:30").do(run)
schedule.every().friday.at("19:00").do(run)

send_telegram("🚀 Bot de trading iniciado. Operando en Paper Trading.")

while True:
    schedule.run_pending()
    time.sleep(30)
