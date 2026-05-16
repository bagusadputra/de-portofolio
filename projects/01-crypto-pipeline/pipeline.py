# pipeline.py

from datetime import datetime
from extract   import extract
from transform import transform
from load      import setup_table, load


def run_pipeline():
    print("=" * 50)
    print(f"Pipeline started : {datetime.now()}")
    print("=" * 50)

    # Jalankan semua tahap
    df           = extract()
    df           = transform(df)
    setup_table()
    rows_loaded  = load(df)

    print("=" * 50)
    print(f"Pipeline finished: {datetime.now()}")
    print(f"Total rows loaded: {rows_loaded}")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()