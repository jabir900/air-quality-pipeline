from pathlib import Path

import json
import pandas as pd

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

RAW_COLUMNS = ["time", "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "ozone"]
RENAME = {"pm2_5": "pm25", "carbon_monoxide": "co", "nitrogen_dioxide": "no2", "ozone": "o3"}
POLLUTANTS = ["pm10", "pm25", "co", "no2", "o3"]


def city_from_filename(path):
    # "port_harcourt_20261118_115611.json" -> "Port Harcourt"
    name = path.stem.rsplit("_", 2)[0]
    return name.replace("_", " ").title()


def raw_to_dataframe(path):
    with open(path) as f:
        data = json.load(f)
    df = pd.DataFrame(data["hourly"])
    df = df.reindex(columns=RAW_COLUMNS)      # older files may lack some columns
    df["city"] = city_from_filename(path)
    df["source"] = "open-meteo"
    return df


def clean(df):
    df = df.rename(columns=RENAME)
    df["time"] = pd.to_datetime(df["time"])
    for col in POLLUTANTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=POLLUTANTS, how="all")           # rows with no data at all

    now = pd.Timestamp.now(tz="Africa/Lagos").tz_localize(None)
    df = df[df["time"] <= now]                              # drop future (forecast) hours

    df = df.drop_duplicates(subset=["city", "time"], keep="last")   # newest file wins
    return df.sort_values(["city", "time"]).reset_index(drop=True)


def main():
    files = sorted(RAW_DIR.glob("*.json"))      # file names contain the fetch time, so
    frames = [raw_to_dataframe(p) for p in files]   # sorting puts the newest file last
    df = clean(pd.concat(frames, ignore_index=True))

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    out = CLEAN_DIR / "air_quality_clean.csv"
    df.to_csv(out, index=False)

    print(f"Read {len(files)} raw files -> {len(df)} clean rows")
    print(df.groupby("city").size())
    print(df.isna().sum())
    print("Saved to", out)


if __name__ == "__main__":
    main()
