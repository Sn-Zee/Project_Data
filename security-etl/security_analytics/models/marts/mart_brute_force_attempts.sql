WITH login_failures AS (
    SELECT
        username,
        source_ip,
        event_timestamp,
        COUNT(*) OVER (PARTITION BY username, source_ip, date_trunc('hour', event_timestamp)) AS failures_per_hour
        FROM {{ ref ('stg_security_events') }}
        WHERE event_type = 'LOGIN_FAILURE'
),

brute_force_windows AS (
    SELECT
        username,
        source_ip,
        date_trunc('hour', event_timestamp) AS attack_window,
        failures_per_hour AS failure_count,
        MIN(event_timestamp) AS first_attempt,
        MAX(event_timestamp) AS last_attempt
    FROM login_failures
    WHERE failures_per_hour >= 5
    GROUP BY
        username,
        source_ip,
        date_trunc('hour', event_timestamp),
        failures_per_hour
)

SELECT * FROM brute_force_windows
ORDER BY failure_count DESC