-- Drop existing tables to start fresh
DROP TABLE IF EXISTS fact_flows CASCADE;
DROP TABLE IF EXISTS dim_attack_type CASCADE;
DROP TABLE IF EXISTS dim_protocol CASCADE;

-- Dimension table: maps attack labels to categories
CREATE TABLE dim_attack_type (
    attack_type_id SERIAL PRIMARY KEY,
    label VARCHAR(100) NOT NULL UNIQUE,
    attack_category VARCHAR(50) NOT NULL
);

-- Dimension table: maps protocol numbers to names
CREATE TABLE dim_protocol (
    protocol_id SERIAL PRIMARY KEY,
    protocol_number VARCHAR(100) NOT NULL UNIQUE,
    protocol_name VARCHAR(50) NOT NULL
);


CREATE TABLE fact_flows (
    flow_id SERIAL PRIMARY KEY,
    attack_type_id INTEGER REFERENCES dim_attack_type(attack_type_id),
    protocol_id INTEGER REFERENCES dim_protocol(protocol_id),
    destination_port INTEGER,
    flow_duration BIGINT,
    total_fwd_packets INTEGER,
    total_bwd_packets INTEGER,
    total_length_fwd_packets FLOAT,
    total_length_bwd_packets FLOAT,
    flow_bytes_per_sec FLOAT,
    flow_packets_per_sec FLOAT,
    fwd_packet_length_mean FLOAT,
    bwd_packet_length_mean FLOAT,
    packet_length_mean FLOAT,
    packet_length_std FLOAT
);