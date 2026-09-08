WITH source AS (
    SELECT *
    FROM {{ source('raw_weather', 'weather_observations') }}
),

cleaned AS (
    SELECT
        city_name,
        latitude,
        longitude,
        CAST(timestamp as timestamp) AS observation_timestamp,
        CAST(timestamp as date ) AS observation_date,
        temperature_2m AS temperature_celsius,
        relative_humidity_2m AS humidity_percent,
        wind_speed_10m AS wind_speed_kmh,
        precipitation AS precipitation_mm,
        city_name || '_' || timestamp AS city_timestamp_id
    FROM source
    WHERE temperature_2m IS NOT NULL
)

SELECT * FROM cleaned