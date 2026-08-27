import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os
import glob

database_url = os.getenv("DATABASE_URL")

#Create a SQLAlchemy engine that pandas uses for database writes
engine = create_engine(database_url)
#Find all CSV files in the data/ folder

csv_files = glob.glob(os.path.join("data", "*.csv"))
print(f"Found {len(csv_files)} CSV files")

# Read each CSV file into a pandas DataFrame
all_frames = []
for csv_file in csv_files:
    print(f"Reading {os.path.basename(csv_file)}...")
    df = pd.read_csv(csv_file, low_memory=False)
    all_frames.append(df)

# Combine all DataFrames into one and load into PostgreSQL
combined = pd.concat(all_frames, ignore_index=True)
print(f"Total rows: {len(combined)}")
print(f"Columns: {len(combined.columns)}")

combined.to_sql("raw_flows", engine, if_exists="replace", index=False, chunksize=1000)
print("Raw data loaded into PostgreSQL table 'raw_flows'")