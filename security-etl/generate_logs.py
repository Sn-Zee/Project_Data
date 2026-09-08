import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Connection string for your local PostgreSQL database
DB_URL = os.getenv("DATABASE_URL")
NUM_RECORDS = 5000

random.seed(42)

# Usernames with intentional quality issues: mixed casing, empty strings, None
usernames = [
    "jsmith", "JSMITH", "j.smith", "admin", "Admin", "ADMIN",
    "mgarcia", "MGarcia", "lchen", "lChen", "root", "svc_backup",
    "deploy_bot", "null_user", "", None,
]

# Event types with inconsistent casing
event_types = [
    "LOGIN_SUCCESS", "login_success", "LOGIN_FAILURE", "login_failure",
    "PRIVILEGE_ESCALATION", "privilege_escalation",
    "FILE_ACCESS", "file_access", "LOGOUT", "logout",
    "PASSWORD_CHANGE", "ACCOUNT_LOCKED",
]

# Source IPs including invalid entries
source_ips = [
    "192.168.1.100", "192.168.1.101", "10.0.0.50", "10.0.0.51",
    "172.16.0.10", "203.0.113.42", "198.51.100.7", "192.0.2.1",
    "UNKNOWN", "", None, "not_an_ip"
]

# Deperatments with mixed casing, None, and empty strings
departments = [
    "Engineering", "engineering", "ENGINEERING", "Finance", "finance",
    "HR", "hr", "Security", "IT", None, "",
]

risk_levels = [
    "low", "LOW", "Low", "medium", "MEDIUM", "Medium",
    "high", "HIGH", "High", "critical", "CRITICAL", None,
]


# Generate a random timestamp within the first half of 2024
def generate_timestamp():
    base = datetime(2024, 1, 1)
    offset = timedelta(
        days=0,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    return base + offset

def generate_records(n):
    records = []
    for _ in range(n):
        records.append(
            {
                "event_timestamp": generate_timestamp(),
                "username": random.choice(usernames),
                "event_type": random.choice(event_types),
                "source_ip": random.choice(source_ips),
                "department": random.choice(departments),
                "risk_level": random.choice(risk_levels),
                "success": random.choice([True, False, None]),
                "session_duration_sec": random.choice([random.randint(1, 28800), -1, 0, None]),
            }
        )
    return records

# Generate the data, preview it,  and load into PostgreSQL
def main():
    print("Generating security log data...")
    records = generate_records(NUM_RECORDS)
    df = pd.DataFrame(records)

    print(f"Generated {len(df)} records")
    print(f"\nSample data:")
    print(df.head(10).to_string())
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nNull counts:\n{df.isnull().sum()}")

    # Connect to PostgreSQL and write the DataFrame as a table
    engine = create_engine(DB_URL)

    with engine.begin() as connection:
        connection.exec_driver_sql("TRUNCATE TABLE public.raw_security_events")

    df.to_sql("raw_security_events", engine, if_exists="append", index=False)
    print(f"\nLoaded {len(df)} records into 'raw_security_events' table.")

if __name__ == "__main__":
    main()