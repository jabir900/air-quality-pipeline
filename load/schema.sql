CREATE TABLE IF NOT EXISTS cities (
    city_id   SERIAL PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    latitude  DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS measurements (
    city_id     INTEGER NOT NULL REFERENCES cities (city_id),
    measured_at TIMESTAMP NOT NULL,
    source      TEXT NOT NULL,
    pm10        DOUBLE PRECISION,
    pm25        DOUBLE PRECISION,
    co          DOUBLE PRECISION,
    no2         DOUBLE PRECISION,
    o3          DOUBLE PRECISION,
    PRIMARY KEY (city_id, measured_at, source)
);

