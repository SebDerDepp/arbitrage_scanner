import streamlit as st
import ccxt
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Krypto Arbitrage Scanner", layout="wide")
st.title("🔁 Krypto Arbitrage Scanner (Binance & Kraken)")

# Auto-Refresh alle 10 Sekunden
st_autorefresh(interval=10 * 1000, key="arbitrage-refresh")
st.caption("⏱️ Die Seite aktualisiert sich automatisch alle 10 Sekunden.")

# Mehr Coins zur Auswahl
coins = ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "ADA/USDT"]
selected_symbol = st.selectbox("Handelspaar auswählen", coins)

# Einstellbare Arbitrage-Schwelle
threshold = st.slider("Arbitrage-Schwelle (%)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)

# Symbol-Mapping für Kraken (XBT statt BTC)
symbol_map = {
    "BTC/USDT": {"Binance": "BTC/USDT", "Kraken": "XBT/USDT"},
    "ETH/USDT": {"Binance": "ETH/USDT", "Kraken": "ETH/USDT"},
    "XRP/USDT": {"Binance": "XRP/USDT", "Kraken": "XRP/USDT"},
    "SOL/USDT": {"Binance": "SOL/USDT", "Kraken": "SOL/USDT"},
    "ADA/USDT": {"Binance": "ADA/USDT", "Kraken": "ADA/USDT"},
}

# Börsen
exchanges = {
    "Binance": ccxt.binance(),
    "Kraken": ccxt.kraken({'enableRateLimit': True}),
}

# Preis-Abfrage
def fetch_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker.get('ask'), ticker.get('bid')
    except Exception:
        return None, None

# Preisübersicht
st.subheader(f"Aktuelle Preise für {selected_symbol}")
col1, col2 = st.columns(2)
results = {}

for i, (name, exchange) in enumerate(exchanges.items()):
    mapped_symbol = symbol_map[selected_symbol][name]
    ask, bid = fetch_price(exchange, mapped_symbol)
    if ask and bid:
        results[name] = {"ask": ask, "bid": bid}
        with [col1, col2][i]:
            st.metric(label=name, value=f"{ask:.2f} USD (ask)", delta=f"{bid:.2f} USD (bid)")
    else:
        with [col1, col2][i]:
            st.warning(f"⚠️ Keine Daten von {name}")

# Arbitrage-Erkennung
st.subheader("🔍 Mögliche Arbitrage-Gelegenheiten")
found = False

for buy_exchange, buy_data in results.items():
    for sell_exchange, sell_data in results.items():
        if buy_exchange == sell_exchange:
            continue
        spread = (sell_data['bid'] - buy_data['ask']) / buy_data['ask'] * 100
        if spread > threshold:
            found = True
            st.success(f"💰 Kaufe auf {buy_exchange} ({buy_data['ask']:.2f}) → Verkaufe auf {sell_exchange} ({sell_data['bid']:.2f}) → Spread: {spread:.2f}%")
            st.audio("https://actions.google.com/sounds/v1/cartoon/concussive_drum_hit.ogg", format="audio/ogg", start_time=0)

if not found:
    st.info(f"Keine Arbitrage-Gelegenheit über {threshold:.1f}% gefunden.")
