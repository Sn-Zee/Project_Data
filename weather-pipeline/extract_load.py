import os
import requests
import psycopg2

# Database connection settings for Dockerized PostgreSQL

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ.get("DB_NAME", "weather_db"),
    "user": os.environ.get("DB_USER", "pipeline_user"),
    "password": os.environ.get("DB_PASSWORD", "pipeline_pass"),
}


# Five Global Cities to fetch weather data for
CITIES = [
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050}
]

# Weather variables to request from the API
HOURLY_VARIABLES = "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
API_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(city):
    # Build the API request parameters
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": HOURLY_VARIABLES,
        "past_days": 7,
        "forecast_days": 7,
        "timezone": "auto",
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Parse each hourly timestamp into a row
    rows = []
    hourly = data["hourly"]
    times = hourly["time"]
    for i in range(len(times)):
        rows.append((
            city["name"],
            city["latitude"],
            city["longitude"],
            times[i],
            hourly["temperature_2m"][i],
            hourly["relative_humidity_2m"][i],
            hourly["wind_speed_10m"][i],
            hourly["precipitation"][i]
        ))
    return rows

def create_table(conn):
    # Create the raw_weather schema and observations table
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw_weather;")
        cur.execute("DROP TABLE IF EXISTS raw_weather.weather_observations;")
        cur.execute("""
            CREATE TABLE raw_weather.weather_observations (
                city_name TEXT,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                timestamp TEXT,
                temperature_2m DOUBLE PRECISION,
                relative_humidity_2m DOUBLE PRECISION,
                wind_speed_10m DOUBLE PRECISION,
                precipitation DOUBLE PRECISION
                );
        """)
    conn.commit()

def load_data(conn, rows):
    # Insert all weather rows into the table
    with conn.cursor() as cur:
        insert_query = """
            INSERT INTO raw_weather.weather_observations(city_name, latitude, longitude, timestamp, temperature_2m, relative_humidity_2m, wind_speed_10m, precipitation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.executemany(insert_query, rows)
    conn.commit()

def main():
    # Fetch weather data for all cities
    all_rows = []
    for city in CITIES:
        print(f"Fetching weather data for {city['name']}...")
        rows = fetch_weather(city)
        all_rows.extend(rows)
        print(f" Got {len(rows)} hourly records")
    print(f"\nTotal records: {len(all_rows)}")

    # Connect to PostgreSQL and load the data
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        create_table(conn)
        load_data(conn, all_rows)
        print("Data loaded successfully into raw_weather.weather_observations")
    finally:
        conn.close()

if __name__ == "__main__":
    main()