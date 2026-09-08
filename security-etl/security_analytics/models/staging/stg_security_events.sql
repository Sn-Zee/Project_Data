WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_security_events') }}
),

cleaned AS (
    SELECT
        event_timestamp,
        LOWER(TRIM(COALESCE(NULLIF(username, ''), 'unknown'))) AS username,
        UPPER(TRIM(COALESCE(NULLIF(event_type, ''), 'UNKNOWN'))) AS event_type,
        CASE
            WHEN source_ip ~ '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
                THEN source_ip
            ELSE null
        END AS source_ip,
        LOWER(TRIM(COALESCE(NULLIF(department, ''), 'unknown'))) AS department,
        LOWER(TRIM(COALESCE(NULLIF(risk_level, ''), 'unknown'))) AS risk_level,
        success,
        CASE
            WHEN session_duration_sec IS NOT NULL
                AND session_duration_sec > 0
                THEN session_duration_sec
            ELSE NULL
        END AS session_duration_sec,
        EXTRACT(HOUR FROM event_timestamp)::int AS event_hour,
        EXTRACT(dow FROM event_timestamp)::int AS day_of_week
    FROM source

)

SELECT * FROM cleaned