import os
import psycopg2
import random
from datetime import datetime, timedelta

# Connection settings for local PostgreSQL
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "security_analytics"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "password")
}


# 50 simulated user accounts
USERS = [f"user_{i:03d}" for i in range(1,51)]
# IP addresses including None and empty string for missing data
IPS = [
    "192.168.1.100",
    "192.168.1.101",
    "10.0.0.50",
    "10.0.0.51",
    "172.16.0.10",
    "203.0.113.42",
    "198.51.100.7",
    "203.0.113.99",
    None,
    "",
]

# Event types with intentional mixed casing
EVENT_TYPES = [
    "LOGIN",
    "login",
    "Login",
    "LOGOUT",
    "logout",
    "FAILED_LOGIN",
    "failed_login",
    "Failed_Login",
    "PASSWORD_CHANGE",
    "MFA_CHALLENGE",
]

# Status values with incosistent casing
STATUSES = ["success", "SUCCESS", "failure", "FAILURE", "Success", "Failure"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "curl/7.88.1",
    "python-requests/2.31.0",
    None,
]

def create_database():
    # Connect to the default 'postgres' database to create our project database

    conn = psycopg2.connect(
        host = DB_CONFIG["host"],
        port = DB_CONFIG["port"],
        dbname = "postgres",
        user = DB_CONFIG["user"],
        password = DB_CONFIG["password"],
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Only create if it doesn't already exist
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],)
    )
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
        print(f"Created database: {DB_CONFIG['dbname']}")

    else:
        print(f"Database {DB_CONFIG['dbname']} already exists")

    cur.close()
    conn.close()


def create_tables(conn):
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
    cur.execute("DROP TABLE IF EXISTS raw.auth_events CASCADE")
    # Store all columns as TEXT to simulate untyped raw ingestion
    cur.execute(
        """
        CREATE TABLE raw.auth_events (
        id SERIAL PRIMARY KEY,
        event_timestamp TEXT,
        user_id TEXT,
        event_type TEXT,
        ip_address TEXT,
        status TEXT,
        user_agent TEXT
        )
        """
    )
    conn.commit()
    cur.close()
    print("Created raw.auth_events table")

def generate_events(num_events=500):
    events = []
    base_time = datetime(2026, 8, 20, 0, 0, 0)

    # Generate random events with mixed timestamp formats
    for _ in range(num_events):
        ts = base_time + timedelta(seconds=random.randint(0, 7 * 24 * 3600))

        if random.random() < 0.3:
            ts_str = ts.strftime("%m/%d/%Y %H:%M:%S")
        elif random.random() < 0.5:
            ts_str = ts.isoformat()
        else:
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

        events.append(
            (
                ts_str,
                random.choice(USERS),
                random.choice(EVENT_TYPES),
                random.choice(IPS),
                random.choice(STATUSES),
                random.choice(USER_AGENTS),
            )
        )

    # Plant a brute-force attack: 20 rapid failures from one IP
    attacker_ip = "203.0.113.42"
    target_user = "user_001"
    brute_start = base_time + timedelta(days=3, hours=2)

    for i in range(20):
        ts = brute_start + timedelta(seconds=i * 5)
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        events.append(
            (ts_str, target_user, "FAILED_LOGIN", attacker_ip, "failure", "python-requests/2.31.0")
        )

    # Add 15 exact duplicate rows to simulate dirty data
    for _ in range(15):
        events.append(random.choice(events))

    return events

def load_events(conn, events):
    cur = conn.cursor()
    # Insert all events into the raw table
    cur.executemany(
        """
        INSERT INTO raw.auth_events (event_timestamp, user_id, event_type, ip_address, status, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        events,
    )
    conn.commit()
    cur.close()
    print(f"Loaded {len(events)} events into raw.auth_events")

def main():
    create_database()
    conn = psycopg2.connect(**DB_CONFIG)
    create_tables(conn)
    events = generate_events(500)
    load_events(conn, events)
    conn.close()
    print("Done! Raw security data loaded.")

if __name__ == "__main__":
    main()    