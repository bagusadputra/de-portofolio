# load.py
# Simpan data ke PostgreSQL

import psycopg2
import psycopg2.extras
import pandas as pd
from config import DB_CONFIG, TABLE_NAME


def setup_table() -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id                   SERIAL PRIMARY KEY,
            coin_id              VARCHAR(100),
            symbol               VARCHAR(20),
            name                 VARCHAR(100),
            current_price        NUMERIC(20, 8),
            market_cap           NUMERIC(25, 2),
            market_cap_rank      INTEGER,
            total_volume         NUMERIC(25, 2),
            high_24h             NUMERIC(20, 8),
            low_24h              NUMERIC(20, 8),
            price_change_pct_24h NUMERIC(10, 4),
            price_category       VARCHAR(20),
            signal_24h           VARCHAR(20),
            last_updated         TIMESTAMP,
            ingested_at          TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print(f"[LOAD] Tabel {TABLE_NAME} siap")


def load(df: pd.DataFrame) -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    try:
        records = [
            (
                row["id"],
                row["symbol"],
                row["name"],
                float(row["current_price"]),
                float(row["market_cap"])        if pd.notna(row["market_cap"])        else None,
                int(row["market_cap_rank"])      if pd.notna(row["market_cap_rank"])   else None,
                float(row["total_volume"])       if pd.notna(row["total_volume"])      else None,
                float(row["high_24h"])           if pd.notna(row["high_24h"])          else None,
                float(row["low_24h"])            if pd.notna(row["low_24h"])           else None,
                float(row["price_change_percentage_24h"]),
                row["price_category"],
                row["signal_24h"],
                row["last_updated"],
                row["ingested_at"]
            )
            for _, row in df.iterrows()
        ]

        psycopg2.extras.execute_values(
            cur,
            f"""
            INSERT INTO {TABLE_NAME} (
                coin_id, symbol, name,
                current_price, market_cap, market_cap_rank,
                total_volume, high_24h, low_24h,
                price_change_pct_24h, price_category, signal_24h,
                last_updated, ingested_at
            ) VALUES %s
            """,
            records
        )

        conn.commit()
        rows_loaded = len(records)
        print(f"[LOAD] {rows_loaded} rows berhasil disimpan!")
        return rows_loaded

    except Exception as e:
        conn.rollback()
        print(f"[LOAD] Error: {e}")
        raise

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    df = extract()
    df = transform(df)
    setup_table()
    load(df)