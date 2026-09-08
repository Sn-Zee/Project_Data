{{ config(materialized='table') }}

WITH daily_aggregates AS (
    SELECT
        city_name,
        observation_date,
        ROUND(AVG(temperature_celsius)::numeric, 1) AS avg_temperature,
        ROUND(MIN(temperature_celsius)::numeric, 1) AS min_temperature,
        ROUND(MAX(temperature_celsius)::numeric, 1) AS max_temperature,
        ROUND(SUM(precipitation_mm)::numeric, 2) AS total_precipitation_mm,
        ROUND(AVG(humidity_percent)::numeric, 1) AS avg_humidity_percent,
        ROUND(AVG(wind_speed_kmh)::numeric, 1) AS avg_wind_speed_kmh,
        COUNT(*) AS observation_count
    FROM {{ ref('stg_weather_observations') }}
    GROUP BY city_name, observation_date
),

ranked AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY observation_date
            ORDER BY avg_temperature DESC
        ) AS temperature_rank
    FROM daily_aggregates
)

SELECT * 
FROM ranked
ORDER BY observation_date, temperature_rank