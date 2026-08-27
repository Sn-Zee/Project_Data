import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configure the dashboard page
st.set_page_config(page_title="Threat Analytics Dashboard", layout="wide")

# Database connection settings
DB_CONFIG = {
    "dbname": "threat_analytics",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

# Create a cached database engine
@st.cache_resource
def get_engine():
    return create_engine(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# Query attack type counts from the star schema
@st.cache_data
def load_attack_summary():
    query = """
        SELECT
            d.attack_category,
            d.label,
            COUNT(*) AS flow_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
        FROM fact_flows f
        JOIN dim_attack_type d ON f.attack_type_id = d.attack_type_id
        GROUP BY d.attack_category, d.label
        ORDER BY flow_count DESC;
    """
    return pd.read_sql(query, get_engine())

# Query the top 1% highest-traffic flows
@st.cache_data
def load_high_risk_flows():
    query = """
       SELECT 
            f.flow_id, 
            d.label AS attack_type, 
            p.protocol_name,
            f.destination_port,
            f.flow_bytes_per_sec,
            f.total_fwd_packets,
            f.total_bwd_packets,
            f.flow_duration
        FROM fact_flows f
        JOIN dim_attack_type d
        ON f.attack_type_id = d.attack_type_id
        JOIN dim_protocol p
        ON f.protocol_id = p.protocol_id
        WHERE f.flow_bytes_per_sec > (
            SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY flow_bytes_per_sec)
            FROM fact_flows
        )
        ORDER BY f.flow_bytes_per_sec DESC
        LIMIT 100 
    """

    return pd.read_sql(query, get_engine())

@st.cache_data
def load_anomaly_data():
    # Query the top 5000 flows by anomaly score
    query = """
        SELECT
            f.flow_id,
            d.label AS attack_type,
            f.flow_bytes_per_sec,
            f.anomaly_score,
            f.total_fwd_packets,
            f.total_bwd_packets,
            f.flow_duration,
            f.packet_length_mean
        FROM fact_flows f
        JOIN dim_attack_type d
        ON f.attack_type_id = d.attack_type_id
        WHERE f.anomaly_score is NOT NULL
        ORDER BY f.anomaly_score DESC
        LIMIT 5000
    """

    return pd.read_sql(query, get_engine())

# Dashboard heading
st.title("Network Threat Analytics Dashboard")
st.markdown("Analyzing CICIDS2017 network intrusion detection data")

# Load data and compute summary metrics
summary = load_attack_summary()
total_flows = summary["flow_count"].sum()
malicious_flows = summary[summary["attack_category"] != "Benign"]["flow_count"].sum()
pct_malicious = round(malicious_flows / total_flows * 100, 2)
unique_attacks = summary[summary["attack_category"] != "Benign"]["label"].nunique()

# Display metric cards in three columns
st.sidebar.header("Filters")
categories = summary["attack_category"].unique().tolist()
selected = st.sidebar.multiselect(
    "Attack Categories",
    options = categories,
    default = categories 
)

filtered = summary[summary["attack_category"].isin(selected)]

# Create two tabs for the dashboard layout
tab1, tab2 = st.tabs(["Threat Overview", "Anomaly Detection"])

with tab1:
    st.subheader("Attack Distribution")
    chart_data = filtered.groupby("attack_category")["flow_count"].sum().reset_index()
    chart_data = chart_data.set_index("attack_category")
    st.bar_chart(chart_data)

    st.subheader("Attack Types Detail")
    st.dataframe(filtered, use_container_width=True)

    st.subheader("High-Risk Flows (Top 1% by Bytes/sec)")
    high_risk = load_high_risk_flows()
    st.dataframe(high_risk, use_container_width=True)

with tab2:
    st.subheader("Anomaly Detection")
    st.markdown("Flows scored by statistical deviation across packet metrics (z-score)")

    # Load and display the top anomalous flows
    anomaly_data = load_anomaly_data()

    st.scatter_chart(
        anomaly_data,
        x="flow_bytes_per_sec",
        y="anomaly_score",
        color="attack_type"
    )

    st.subheader("Top 20 Anomalous Flows")
    st.dataframe(anomaly_data.head(20), use_container_width=True)