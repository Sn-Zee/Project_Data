WITH login_events AS (
    SELECT *
    FROM {{ ref('stg_auth_events') }}
    WHERE event_type IN ('LOGIN', 'FAILED_LOGIN')
),

user_daily_stats AS (
    SELECT
        user_id,
        date_trunc('day', event_timestamp)::date AS event_date,
        COUNT(*) AS total_attempts,
        COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_logins,
        COUNT(*) FILTER (WHERE status = 'FAILURE') AS failed_logins,
        COUNT(DISTINCT ip_address) AS unique_ips,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'FAILURE')::numeric / NULLIF(COUNT(*), 0) * 100, 2
        ) AS failure_rate_pct
    FROM login_events
    GROUP BY user_id, date_trunc('day', event_timestamp)::date
)

SELECT
    md5(user_id || '|' || event_date::text) AS login_stat_id,
    user_id,
    event_date,
    total_attempts,
    successful_logins,
    failed_logins,
    unique_ips,
    failure_rate_pct
FROM user_daily_stats