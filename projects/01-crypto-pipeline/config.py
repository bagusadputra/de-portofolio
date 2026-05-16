# config.py

# ── API ──────────────────────────────────────────
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

API_PARAMS = {
    "vs_currency": "usd",
    "order":"market_cap_desc",
    "per_page":20,
    "page":1,
    "sparkline":False}

KOLOM = [
    "id",
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "market_cap_rank",
    "total_volume",
    "high_24h",
    "low_24h",
    "price_change_percentage_24h",
    "last_updated"]

# ── DATABASE ──────────────────────────────────────
DB_CONFIG = {
    "host":     "172.17.192.118",
    "port":     5432,
    "database": "project1_crypto",
    "user":     "postgres",
    "password": "postgres"
}

TABLE_NAME = "raw_crypto_price"