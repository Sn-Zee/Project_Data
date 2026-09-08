import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Connection string for local PostgreSQL
DB_URL = os.getenv("DATABASE_URL")

ANALYTICS_SCHEMA = "analytics"

# Cache the engine so it's shared across Streamlit reruns
@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

# Cache query results for 60 seconds
@st.cache_data(ttl=60)
def load_data(query, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)

# Page configuration and title
st.set_page_config(page_title="Security Threat Dashboard", layout="wide")
st.title("Security Threat Detection Dashboard")

st.sidebar.header("Filters")

# Query the staging view for the earliest and latest dates
date_range = load_data(f"""
    SELECT MIN(event_timestamp)::date AS min_date,
           MAX(event_timestamp)::date AS max_date
    FROM {ANALYTICS_SCHEMA}.stg_security_events
""")
min_date = date_range["min_date"].iloc[0]
max_date = date_range["max_date"].iloc[0]

# Date pickers default to the full data range
start_date = st.sidebar.date_input(
    "Start date", value=min_date, min_value=min_date, max_value=max_date
)

end_date = st.sidebar.date_input(
    "End date", value=max_date, min_value=min_date, max_value=max_date
)

# Populate the multi-select with all distinct event types
event_types_list = load_data(f"""
    SELECT DISTINCT event_type
    FROM {ANALYTICS_SCHEMA}.stg_security_events
    ORDER BY event_type
""")
selected_events = st.sidebar.multiselect(
    "Event types",
    options=event_types_list["event_type"].tolist(),
    default=event_types_list["event_type"].tolist(),
)

# Stop the app if the learner deselects everything
if not selected_events:
    st.sidebar.warning("Select at least one event type.")
    st.stop()

# Build reusable filter fragments and a params dict
event_type_list_str = ", ".join([f"'{e}'" for e in selected_events])

date_filter = f"""
    event_timestamp >= CAST(:start_date AS DATE)
    AND event_timestamp < CAST(:end_date AS DATE) + interval '1 day'
"""

event_filter = f"event_type IN ({event_type_list_str})"
combined_filter = f"{date_filter} AND {event_filter}"
filter_params = {"start_date": str(start_date), "end_date":str(end_date)}

# Show how many events match the current filters
filtered_count = load_data(f"""
    SELECT COUNT(*) AS total
    FROM {ANALYTICS_SCHEMA}.stg_security_events
    WHERE {combined_filter}
""", params=filter_params)
st.sidebar.metric("Matching Events", f"{filtered_count['total'].iloc[0]:,}")

col1, col2, col3 = st.columns(3)

total_events = load_data(f"""
    SELECT COUNT(*) AS total
    FROM {ANALYTICS_SCHEMA}.stg_security_events
    WHERE {combined_filter}
""", params=filter_params)

brute_force_count = load_data(f"""
    SELECT COUNT(*) AS total
    FROM {ANALYTICS_SCHEMA}.mart_brute_force_attempts
    WHERE attack_window >= CAST(:start_date AS DATE)
            AND attack_window < CAST(:end_date AS DATE) + interval '1 day'
""", params=filter_params)

after_hours_count = load_data(f"""
    SELECT COUNT(*) AS total
    FROM {ANALYTICS_SCHEMA}.mart_after_hours_access
    WHERE first_event >= CAST(:start_date AS DATE)
            AND first_event < CAST(:end_date AS DATE) + interval '1 day'
""", params=filter_params)

# Display each metric in its column
col1.metric("Total Cleaned Events", f"{total_events['total'].iloc[0]:,}")
col2.metric("Brute Force Incidents", brute_force_count["total"].iloc[0])
col3.metric("After-Hours Users", after_hours_count["total"].iloc[0])

st.divider()

# Brute force attempts table
st.subheader("Brute Force Login Attempts")
bf_data = load_data(f"""
    SELECT username, source_ip, failure_count, attack_window, first_attempt, last_attempt
    FROM {ANALYTICS_SCHEMA}.mart_brute_force_attempts
    WHERE attack_window >= CAST(:start_date AS DATE)
            AND attack_window < CAST(:end_date AS DATE) + interval '1 day'
    ORDER BY failure_count DESC
    LIMIT 20
""", params=filter_params)
st.dataframe(bf_data, use_container_width=True)

# After-hours access table
st.subheader("After-Hours Access Activity")
ah_data = load_data(f"""
    SELECT username, department, after_hours_events, high_risk_count, unique_ips, first_event, last_event
    FROM {ANALYTICS_SCHEMA}.mart_after_hours_access
    WHERE first_event >= CAST(:start_date AS DATE)
        AND first_event < CAST(:end_date AS DATE) + interval '1 day'
    ORDER BY high_risk_count DESC
    LIMIT 20
""", params=filter_params)
st.dataframe(ah_data, use_container_width=True)


st.divider()

chart_col1, chart_col2 = st.columns(2)

# Hourly event distribution chart
with chart_col1:
    st.subheader("Events by Hour of Day")
    hourly = load_data(f"""
        SELECT event_hour, COUNT(*) AS event_count
        FROM {ANALYTICS_SCHEMA}.stg_security_events
        WHERE {combined_filter}
        GROUP BY event_hour
        ORDER BY event_hour    
""", params=filter_params)
    st.bar_chart(hourly.set_index("event_hour"))

# Risk level distribution chart
with chart_col2:
    st.subheader("Events by Risk Level")
    risk = load_data(f"""
        SELECT risk_level, COUNT(*) AS event_count
        FROM {ANALYTICS_SCHEMA}.stg_security_events
        WHERE {combined_filter} AND risk_level != 'unknown'
        GROUP BY risk_level
        ORDER BY event_count DESC    
""", params=filter_params)
    st.bar_chart(risk.set_index("risk_level"))