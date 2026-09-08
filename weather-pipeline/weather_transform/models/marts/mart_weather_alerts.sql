{{ config(materialized='table') }}

WITH daily_temps AS (
    SELECT 
        city_name,
        observation_date,
        avg_temperature,
        -- Compare each day's temp to the previous day
        LAG(avg_temperature) OVER (
            PARTITION BY city_name
            ORDER BY observation_date
        ) AS prev_day_temperature,
        -- Compute a 3-day rolling average for trend context
        AVG(avg_temperature) OVER (
            PARTITION BY city_name
            ORDER BY observation_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3day_avg
    FROM {{ ref('mart_daily_weather_summary') }}
),

alerts AS (
    SELECT
        city_name,
        observation_date,
        avg_temperature,
        prev_day_temperature,
        -- Calculate the day-over-day temperature difference
        ROUND((avg_temperature - prev_day_temperature)::numeric, 1) AS day_over_day_change,
        ROUND(rolling_3day_avg::numeric, 1) AS rolling_3day_avg,
        -- Flag extreme swings exceeding 5 degrees
        CASE
            WHEN abs(avg_temperature - prev_day_temperature) > 5
            THEN 'EXTREME_TEMP_CHANGE'
            ELSE NULL
        END AS alert_type
    FROM daily_temps
    WHERE prev_day_temperature IS NOT NULL
)

SELECT * FROM alerts
WHERE alert_type IS NOT NULL
ORDER BY observation_date, city_name