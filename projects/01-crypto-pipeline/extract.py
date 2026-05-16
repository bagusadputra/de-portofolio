import requests
import pandas as pd
from config import API_URL, API_PARAMS, KOLOM

def extract()-> pd.DataFrame :
    print("[EXTRACT] Mengambil data dari CoinGecko...")

    response = requests.get(API_URL, params=API_PARAMS)

    if response.status_code != 200:
        raise Exception (f"Gagal:{response.status_code}")
    
    data = response.json()
    print(f"data sudah dikirim: {len(data)} coins")

    df = pd.DataFrame(data)
    df = df[KOLOM]
    print(f"[EXTRACT] Shape:{df.shape}")
    return df

if __name__=="__main__":
    df = extract()
    print(df.head())
    
