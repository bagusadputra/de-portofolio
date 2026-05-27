import requests
import pandas as pd
import psycopg2
import psycopg2.extras
from datetime import datetime

# ── CONFIG ───────────────────────────────────────
API_URL = "https://restcountries.com/v3.1/all"
API_PARAMS = {
    "fields": "name,population,area,region,subregion,capital,currencies,languages"
}

DB_CONFIG = {
    "host":     "172.17.192.118",
    "port":     5432,
    "database": "countries_db",
    "user":     "postgres",
    "password": "postgres"
}

# ── EXTRACT ──────────────────────────────────────
def extract() -> list:
    response = requests.get(API_URL, params=API_PARAMS)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")
    data = response.json()
    print(f"[EXTRACT] {len(data)} countries fetched")
    return data

# ── TRANSFORM ─────────────────────────────────────
def parse_country(country: dict) -> dict:
    capital    = country.get("capital", [])
    currencies = country.get("currencies", {})
    languages  = country.get("languages", {})
    area       = country.get("area", 0) or 0
    population = country.get("population", 0) or 0

    return {
        "name_common":     country["name"]["common"],
        "name_official":   country["name"]["official"],
        "capital":         capital[0] if capital else None,
        "region":          country.get("region"),
        "subregion":       country.get("subregion"),
        "area_km2":        area,
        "population":      population,
        "density":         round(population / area, 2) if area > 0 else None,
        "currency_name":   ", ".join([v["name"] for v in currencies.values()]),
        "currency_symbol": ", ".join([v.get("symbol","") for v in currencies.values()]),
        "languages":       ", ".join(languages.values()),
        "ingested_at":     datetime.now()
    }

def transform(data: list) -> pd.DataFrame:
    records = [parse_country(c) for c in data]
    df = pd.DataFrame(records)
    print(f"[TRANSFORM] Shape: {df.shape}")
    return df

# ── LOAD ─────────────────────────────────────────
def setup_table():
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_countries (
            id               SERIAL PRIMARY KEY,
            name_common      VARCHAR(200),
            name_official    VARCHAR(200),
            capital          VARCHAR(200),
            region           VARCHAR(100),
            subregion        VARCHAR(100),
            area_km2         NUMERIC(15, 2),
            population       BIGINT,
            density          NUMERIC(10, 2),
            currency_name    TEXT,
            currency_symbol  VARCHAR(50),
            languages        TEXT,
            ingested_at      TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("[SETUP] Table ready!")

def load(df: pd.DataFrame) -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()
    try:
        records = [
            (
                row["name_common"], row["name_official"],
                row["capital"], row["region"], row["subregion"],
                float(row["area_km2"])  if pd.notna(row["area_km2"])  else None,
                int(row["population"])  if pd.notna(row["population"]) else None,
                float(row["density"])   if pd.notna(row["density"])    else None,
                row["currency_name"], row["currency_symbol"],
                row["languages"], row["ingested_at"]
            )
            for _, row in df.iterrows()
        ]
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO raw_countries (
                name_common, name_official, capital,
                region, subregion, area_km2, population,
                density, currency_name, currency_symbol,
                languages, ingested_at
            ) VALUES %s
            """,
            records
        )
        conn.commit()
        print(f"[LOAD] {len(records)} rows inserted!")
        return len(records)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# ── PIPELINE ─────────────────────────────────────
def run_pipeline():
    print("=" * 50)
    print(f"Pipeline started: {datetime.now()}")
    print("=" * 50)
    data = extract()
    df   = transform(data)
    setup_table()
    rows = load(df)
    print("=" * 50)
    print(f"Pipeline finished: {datetime.now()}")
    print(f"Total rows: {rows}")
    print("=" * 50)

if __name__ == "__main__":
    run_pipeline()