SET client_encoding TO 'UTF8';

SELECT
    d.attack_category,
    d.label,
    COUNT(*) AS flow_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM fact_flows f
JOIN dim_attack_type d ON f.attack_type_id = d.attack_type_id
GROUP BY d.attack_category, d.label
ORDER BY flow_count DESC;

-- Hourly traffic breakdown (benign vs malicious)
SELECT
    d.attack_category,
    COUNT(*) AS flow_count
FROM fact_flows f
JOIN dim_attack_type d ON f.attack_type_id = d.attack_type_id
GROUP BY d.attack_category
ORDER BY flow_count DESC;

-- Suspicious flows: top 1% by flow bytes per second
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
JOIN dim_attack_type d ON f.attack_type_id = d.attack_type_id
JOIN dim_protocol p ON f.protocol_id = p.protocol_id
WHERE f.flow_bytes_per_sec > (
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY flow_bytes_per_sec)
    FROM fact_flows
)
ORDER BY f.flow_bytes_per_sec DESC
LIMIT 100;