import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import glob
import numpy as np
import sys
from scipy import stats


# Database connection settings
database_url = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine for pandas operations
engine = create_engine(database_url)

# Map raw attack labels to higher-level categories
ATTACK_CATEGORIES = {
    "BENIGN": "Benign",
    "FTP-Patator": "Brute Force",
    "SSH-Patator": "Brute Force",
    "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS",
    "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS",
    "Heartbleed": "DoS",
    "Web Attack - Brute Force": "Web Attack",
    "Web Attack - XSS": "Web Attack",
    "Web Attack - Sql Injection": "Web Attack",
    "Infiltration": "Infiltration",
    "Bot": "Botnet",
    "PortScan": "Port Scan",
    "DDoS": "DDoS",
}

# Map IP protocol numbers to readable names
PROTOCOL_MAP = {
    0: "HOPOPT",
    6: "TCP",
    17: "UDP",
}

ANOMALY_COLUMNS = [
    "flow_duration", "total_fwd_packets", "total_bwd_packets", "flow_bytes_per_sec"
]

print("=== ETL Pipeline Starting ===")

# Read all CSV files from the data directory
csv_files = glob.glob(os.path.join("data", "*.csv"))
all_frames = []
for csv_file in csv_files:
    print(f"Reading {os.path.basename(csv_file)}...")
    df = pd.read_csv(csv_file, low_memory=False)
    all_frames.append(df)

combined = pd.concat(all_frames, ignore_index=True)
total_raw = len(combined)
print(f"Total raw rows: {total_raw}")

# Fix column names by stripping leading/trailing spaces
combined.columns = combined.columns.str.strip()

if "Protocol" not in combined.columns:
    print("Warning: 'Protocol' column is missing from this dataset mirror.")
    print("Dynamically adding 'Protocol' column with default value 6 (TCP)...")
    combined["Protocol"] = 6

combined["Protocol"] = pd.to_numeric(combined["Protocol"], errors="coerce").fillna(6).astype(int)

# Replace Infinity with NaN, then drop rows with missing values
numeric_cols = combined.select_dtypes(include=[np.number]).columns
combined.replace([np.inf, -np.inf], np.nan, inplace=True)
rows_before_drop = len(combined)
combined.dropna(subset=numeric_cols, inplace=True)
rows_dropped_nan = rows_before_drop - len(combined)
print(f"Rows dropped (NaN/Inf): {rows_dropped_nan}")

# Remove duplicate rows
rows_before_dedup = len(combined)
combined.drop_duplicates(inplace=True)
duplicates_removed = rows_before_dedup - len(combined)
print(f"Duplicates removed: {duplicates_removed}")

final_count = len(combined)
print(f"Final clean row count: {final_count}")

# Connect to PostgreSQL and create star schema tables
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

schema_sql = """DROP TABLE IF EXISTS fact_flows CASCADE;
DROP TABLE IF EXISTS dim_attack_type CASCADE;
DROP TABLE IF EXISTS dim_protocol CASCADE;
CREATE TABLE dim_attack_type (
    attack_type_id SERIAL PRIMARY KEY,
    label VARCHAR(100) NOT NULL UNIQUE,
    attack_category VARCHAR(50) NOT NULL
);
CREATE TABLE dim_protocol (
    protocol_id SERIAL PRIMARY KEY,
    protocol_number INTEGER NOT NULL UNIQUE,
    protocol_name VARCHAR(20) NOT NULL
);
CREATE TABLE fact_flows (
    flow_id SERIAL PRIMARY KEY,
    attack_type_id INTEGER REFERENCES dim_attack_type(attack_type_id),
    protocol_id INTEGER REFERENCES dim_protocol(protocol_id),
    destination_port INTEGER, flow_duration BIGINT,
    total_fwd_packets INTEGER, total_bwd_packets INTEGER,
    total_length_fwd_packets FLOAT, total_length_bwd_packets FLOAT,
    flow_bytes_per_sec FLOAT, flow_packets_per_sec FLOAT,
    fwd_packet_length_mean FLOAT, bwd_packet_length_mean FLOAT,
    packet_length_mean FLOAT, packet_length_std FLOAT,
    anomaly_score FLOAT
);"""
cur.execute(schema_sql)
conn.commit()

#Populate dim_attack_type with unique labels and categories
labels = combined["Label"].unique()
for label in labels:
    label_clean = label.strip()
    category = ATTACK_CATEGORIES.get(label_clean, "Unknown")
    cur.execute(
        "INSERT INTO dim_attack_type (label, attack_category) VALUES (%s, %s) ON CONFLICT (label) DO NOTHING", (label_clean, category)
    )
    conn.commit()

# Populate dim_protocol with protocol numbers and names
protocols = combined["Protocol"].unique()
for proto in protocols:
    proto_int = int(proto)
    proto_name = PROTOCOL_MAP.get(proto_int, f"OTHER-{proto_int}")
    cur.execute(
        "INSERT INTO dim_protocol (protocol_number, protocol_name) VALUES (%s, %s) ON CONFLICT (protocol_number) DO NOTHING", (proto_int, proto_name)
    )
    conn.commit()

# Build lookup dictionaries from dimension tables
cur.execute("SELECT attack_type_id, label FROM dim_attack_type")
attack_lookup = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT protocol_id, protocol_number FROM dim_protocol")
protocol_lookup = {int(row[1]): row[0] for row in cur.fetchall()}

# Map each flow to its dimension table IDs
combined["attack_type_id"] = combined["Label"].str.strip().map(attack_lookup)
combined["protocol_id"] = combined["Protocol"].map(protocol_lookup)
unmapped = combined["protocol_id"].isna().sum()
if unmapped:
    print(f"WARNING: {unmapped} rows failed to map to a protocol_id")

# Select and rename cloumns for the fact table
fact_df = combined[[
    "attack_type_id", "protocol_id", "Destination Port",
    "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Total Length of Fwd Packets", "Total Length of Bwd Packets",
    "Flow Bytes/s", "Flow Packets/s",
    "Fwd Packet Length Mean", "Bwd Packet Length Mean",
    "Packet Length Mean", "Packet Length Std"
]].copy()

fact_df.columns = [
    "attack_type_id", "protocol_id", "destination_port",
    "flow_duration", "total_fwd_packets", "total_bwd_packets",
    "total_length_fwd_packets", "total_length_bwd_packets",
    "flow_bytes_per_sec", "flow_packets_per_sec",
    "fwd_packet_length_mean", "bwd_packet_length_mean",
    "packet_length_mean", "packet_length_std"
]

# Compute z-scores for each anomaly column
print("Computing anomaly scores...")
z_scores_list = []

for col in ANOMALY_COLUMNS:
    col_mean = fact_df[col].mean()
    col_std = fact_df[col].std()
    if col_std > 0:
        z = ((fact_df[col] - col_mean) / col_std).abs()
    else:
        z = pd.Series(0, index=fact_df.index)
    z_scores_list.append(z)

# Average of absolute z-scores as composite anomaly score
fact_df["anomaly_score"] = pd.concat(z_scores_list, axis=1).mean(axis=1)
print(f"Anomaly scores computed. Max score: {fact_df['anomaly_score'].max():.2f}")

# Load the fact table into PostgreSQL
fact_df.to_sql("fact_flows", engine, if_exists="append", index=False, chunksize=10000)

# Print data quality summary
print(f"\n=== Data Quality Report ===")
print(f"Total raw rows: {total_raw}")
print(f"Rows dropped (NaN/Inf): {rows_dropped_nan}")
print(f"Duplicates removed: {duplicates_removed}")
print(f"Final rows loaded: {final_count}")
print(f"Attack types: {len(attack_lookup)}")
print(f"Protocols: {len(protocol_lookup)}")
print("===ETL Pipeline Complete ===")
#print(protocol_lookup)
#print(combined["Protocol"].dtype, combined["Protocol"].head().tolist())

cur.close()
conn.close()