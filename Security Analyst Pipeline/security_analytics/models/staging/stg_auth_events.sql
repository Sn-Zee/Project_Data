WITH source AS (
    SELECT * FROM {{ source('raw', 'auth_events') }}

),

cleaned as (

    SELECT
        id as event_id,
        CASE
            WHEN event_timestamp ~ '^\d{2}/\d{2}/\d{4}'
                THEN to_timestamp(event_timestamp, 'MM/DD/YYYY HH24:MI:SS')
            ELSE event_timestamp::timestamp
        END AS event_timestamp,
        LOWER(TRIM(user_id)) AS user_id,
        UPPER(TRIM(event_type)) AS event_type,
        CASE
            WHEN TRIM(ip_address) = '' THEN null
            ELSE TRIM(ip_address)
        END AS ip_address,
        UPPER(TRIM(status)) AS status,
        TRIM(user_agent) AS user_agent
    FROM source
    WHERE event_timestamp IS NOT NULL
),

deduplicated as (

    SELECT DISTINCT ON (event_timestamp, user_id, event_type, ip_address)
        event_id,
        event_timestamp,
        user_id,
        event_type,
        ip_address,
        status,
        user_agent
    FROM cleaned
    ORDER BY event_timestamp, user_id, event_type, ip_address, event_id

)

SELECT * FROM deduplicated