WITH failed_logins AS (
    SELECT
        event_id,
        event_timestamp,
        user_id,
        ip_address,
        user_agent,
        row_number() OVER (PARTITION BY user_id, ip_address ORDER BY event_timestamp) AS attempt_number,
        COUNT(*) OVER (PARTITION BY user_id, ip_address ORDER BY event_timestamp RANGE BETWEEN interval '10 minutes' PRECEDING AND CURRENT ROW) AS failures_in_window,
        event_timestamp - lag(event_timestamp) OVER (PARTITION BY user_id, ip_address ORDER BY event_timestamp) AS time_since_last_attempt
    FROM {{ ref('stg_auth_events') }}
    WHERE event_type = 'FAILED_LOGIN' AND status = 'FAILURE'
),

brute_force_candidates AS (
    SELECT
        *,
        CASE
            WHEN failures_in_window >= 5 THEN TRUE
            else false
        END AS is_brute_force
    FROM failed_logins
)

SELECT
    event_id,
    event_timestamp,
    user_id,
    ip_address,
    user_agent,
    attempt_number,
    failures_in_window,
    time_since_last_attempt,
    is_brute_force
FROM brute_force_candidates
WHERE is_brute_force = true
ORDER BY user_id, ip_address, event_timestamp