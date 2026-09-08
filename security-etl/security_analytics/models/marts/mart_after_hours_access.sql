WITH after_hours_events AS (
    SELECT
        username,
        event_type,
        source_ip,
        department,
        event_timestamp,
        event_hour,
        day_of_week,
        risk_level
    FROM {{ ref('stg_security_events') }}
    WHERE event_hour < 6
        OR event_hour > 20
        OR day_of_week IN (0, 6)
)

SELECT
    username,
    department,
    COUNT(*) AS after_hours_events,
    COUNT(DISTINCT source_ip) AS unique_ips,
    COUNT(*) FILTER (
            WHERE risk_level IN ('high', 'critical')
    ) AS high_risk_count,
    MIN(event_timestamp) AS first_event,
    MAX(event_timestamp) AS last_event,
    ARRAY_AGG(DISTINCT event_type) AS event_types
FROM after_hours_events
GROUP BY username, department
ORDER BY high_risk_count DESC, after_hours_events DESC