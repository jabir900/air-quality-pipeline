import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

CITIES_PATH = Path("config/cities.json")
SCHEMA_PATH = Path("load/schema.sql")
CLEAN_CSV = Path("data/clean/air_quality_clean.csv")


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def create_tables(cur):
    cur.execute(SCHEMA_PATH.read_text())


def upsert_cities(cur):
    with open(CITIES_PATH) as f:
        cities = json.load(f)
    rows = [(c["name"], c["latitude"], c["longitude"]) for c in cities]
    execute_values(
        cur,
        """
        INSERT INTO cities (name, latitude, longitude) VALUES %s
        ON CONFLICT (name) DO UPDATE
        SET latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude
        """,
        rows,
    )


def load_measurements(cur):
    cur.execute("SELECT name, city_id FROM cities")
    city_ids = dict(cur.fetchall())

    df = pd.read_csv(CLEAN_CSV)
    df["city_id"] = df["city"].map(city_ids)
    if df["city_id"].isna().any():
        unknown = df.loc[df["city_id"].isna(), "city"].unique()
        raise ValueError(f"Cities missing from the cities table: {list(unknown)}")

    df = df.astype(object).where(df.notna(), None)   # NaN -> None, which becomes NULL
    rows = [
        (int(r.city_id), r.time, r.source, r.pm10, r.pm25, r.co, r.no2, r.o3)
        for r in df.itertuples(index=False)
    ]
    execute_values(
        cur,
        """
        INSERT INTO measurements
            (city_id, measured_at, source, pm10, pm25, co, no2, o3)
        VALUES %s
        ON CONFLICT (city_id, measured_at, source) DO UPDATE SET
            pm10 = EXCLUDED.pm10, pm25 = EXCLUDED.pm25, co = EXCLUDED.co,
            no2 = EXCLUDED.no2, o3 = EXCLUDED.o3
        """,
        rows,
    )
    return len(rows)


def main():
    conn = get_connection()
    try:
        with conn:                       # commits on success, rolls back on error
            with conn.cursor() as cur:
                create_tables(cur)
                upsert_cities(cur)
                n = load_measurements(cur)
                cur.execute("SELECT COUNT(*) FROM measurements")
                total = cur.fetchone()[0]
        print(f"Loaded {n} rows. measurements table now has {total} rows.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
