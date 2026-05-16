import pandas as pd
from datetime import datetime
from extract import extract

def get_price_category(price):
    if price < 1:
        return "micro"
    elif price < 1000:
        return "low"
    elif price <10000:
        return "mid"
    else:
        return "high"
    
def get_signal(pct):
    if pct < 2:
        return "increase"
    elif pct < -2:
        return "decrease"
    else:
        return "stable"
    
def transform(df:pd.DataFrame) -> pd.DataFrame:
    print("[TRANSFORM] process data.....")

    #1. Date Parse
    df['last_updated'] = pd.to_datetime(df["last_updated"])

    #2 Handle Null
    df["price_change_percentage_24h"] = df["price_change_percentage_24h"].fillna(0)

    #3 Create new column
    df['price_category'] = df["current_price"].apply(get_price_category)
    df["signal_24h"] = df["price_change_percentage_24h"].apply(get_signal)
    df["ingested_at"] = datetime.now()

    print(f"[TRANSFORM] Done. Shape: {df.shape}")
    print(f"[TRANSFORM] Signal summary:\n{df['signal_24h'].value_counts()}")
    return df

if __name__=="__main__":
    df = extract()
    df = transform()
    print(df[["name","current_price","price_category","signal_24h","ingested_at"]])

