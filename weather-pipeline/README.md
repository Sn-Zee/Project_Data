<h1 align="center"> Weather Data Engineering Pipeline </h1>

An end-to-end **ELT data engineering pipeline** that extracts live weather data from the **Open-Meteo API**, loads it into a containerized **PostgreSQL** database, transforms it using **dbt**, applies automated data quality tests, detects temperature anomalies, and produces analytical visualizations with **Python, pandas, and matplotlib**.

The project demonstrates practical data engineering concepts including **API ingestion, Docker containerization, PostgreSQL, dbt transformations, data quality testing, SQL CTEs, window functions, dimensinal analytics, and anomaly detection**

## **Project Overview**

This project processes hourly weather data from five global cities:

* London
* New York
* Tokyo
* Sydney
* Berlin

The pipeline retrieves approximately **14 days of hourly weather data per city**, resulting in roughly **1,600 records** across the five locations.

The data flows through the ELT architecture:
```
    Open-Meteo API
           │
           ▼
    Python Extraction
           │
           ▼
    PostgreSQL (Docker)
           │
           ▼
    dbt Staging Models
           │
           ├── Data Cleaning
           ├── Type Conversion 
           └── Data Quality Tests 
           │ 
           ▼
    dbt Analytics Marts
           |
           ├── Daily Weather Summary
           └── Weather Alerts / Anomaly Detection 
           │ 
           ▼
    Python + Pandas
           |
           ▼
Weather Comparison Visualization
```

## **Project Objectives**   

* Build a complete **ELT pipeline** from API ingestion to analytics.
* Containerize PostgreSQL using **Docker** for reproducible development.
* Using dbt to transform raw data into analytics-ready models.
* Implement automated data quality testing.
* Identify and resolve missing temperature values in the source data.
* Apply SQL window functions for ranking and anomaly detection.
* Create reusable analytical marts for downstream analysis.
* Visualize weather trends using **pandas and matplotlib**

## **Tech Stack**

|**Technology**|**Purpose**|
|:---:|:---:|
|**Python**|Data extraction, database loading, and analysis|
|**Open-Meteo API**|Weather data source|
|**PostgreSQL 16**|Data storage and analytical database|
|**Docker / Docker Compose**|Database containerization|
|**dbt**|Data transformation and testing|
|**SQL**|Data transformation and analysis|
|**pandas**|Data analysis and DataFrame processing|
|**matplotlib**|Datavisualization|
|**psycopg2**|PostgreSQL connectivity|

## **Pipeline Architecute**

1. **Extract**

Python retrieves hourly weather information from the Open-Meteo API.

The pipeline collects:

* Temperature 
* Relative humidity
* Wind speed
* Precipitation
* Geographic coordinates
* Observation timestamps

The extraction process covers both recent historical data and forecast data.

2. **Load**


The extracted data is loaded into a Dockerized PostgreSQL database.

```
PostgreSQL
└── raw_weather
     └── weather_observations
```
The raw layer preserves the API output before transformation.

3. **Transform**

dbt transform the raw data through multiple layers:

```
raw_weather.weather_observations
            │ 
            ▼
    stg.weather_observations
            │ 
            ├──────────────┐ 
            ▼              ▼
mart_daily_weather_summary mart_weather_alerts
```

The staging layer:

* Rename API-specific column names
* Converts timestamp strings into proper date/time types
* Creates a composite city/timestamp identifier
* Removes incomplete temperature records

## **Analyics Models**

**Daily Weather Summary**

`mart_daily_weather_summarry`

The daily mart aggregates hourly observations by city and date.

It calculates:

* Average temperature
* Minimum temperature
* Maximum temperature
* Total precipitation
* Average humidity
* Average wind speed
* Number of observations
* Daily temperature ranking

A SQL `RANK()` window function is used to rank cities by average temperature for each day/

**Weather Alerts**

`mart_weather_alerts`

The alerts mart identifies significant day-over-day temperature changes/

It uses"

`LAG()`

to compare each day's temperature against the previous day and:

`AVG() OVER(...)`

to calculate a rolling three-day average.

A weather alert is generated when the absolute temperature change exceeds **5°C**:

` |Today's Average Temperature - Previous Day's Average Temperature| > 5°C`

Alert records are categorized as"

`EXTREME_TEMP_CHANGE`


## Data Quality

Data quality is handled directly within the dbt transformation layer.

Implemented tests include:

* `not_null`
* `unique`
* `accepted_values`

Example validation rules:

city_name                   -> NOT NULL
observation_timestamp       -> NOT NULL
temperature_celsius         -> NOT NULL
city_timestamp_id           -> UNIQUE
temperature_rank            -> NOT NULL
alert_type                  -> ACCEPTED VALUES

**Real Data Quality Issue Detected**

During development, dbt identified missing temperature values returned by the weather API.

The failing `not_null` test exposed incomplete forecast records.

Instead of allowing the issue to propagate downstream, the staging model was updated to filter incomplete records:

`WHERE temperature_2m IS NOT NULL`

The pipeline was then validated again using:

`dbt build`

This demonstrates a practical **detect → investigate → fix → validate** data-quality workflow.

## Data Analysis & Visualization

The `analyze.py` script queries the dbt marts using PostgreSQL and pandas.

It produces a multi-city temperature comparison chart:

`weather_comparison.png`

The visualization compares daily average temperates across:

* London
* New York
* Tokyo
* Sydney
* Berline

The script also prints detected temperature alerts directly to the terminal.

## **Project Structure**

```
weather-pipeline/
│ 
├── extract_load.py
├── analyze.py
├── weather_comparison.png
├── docker-compose.yml
│
└── weather_transform/
    ├── dbt_project.yml
    │
    └── models/
    │   ├── staging/
    │       ├── schema.yml
    │       └── stg_weather_observations.sql
    │
    └── marts/
        ├── schema.yml
        ├── mart_daily_weather_summary.sql
        └── mart_weather_alerts.sql
```

## Setup

**Prerequisites**

* Python 3.11+
* Docker Desktop
* Git
* Internet connection 


1. **Clone the Repository**

    git clone <repository-url>
    cd weather-pipeline

2. **Create a Virrtual Environment**

    python -m venv venv

    Windows:
     
    venv\Scripts\activate

3. **Install Dependencies**

    pip install dbt-postgres==1.11.0
    pip install pandas matplotlib

4. **Start PostgreSQL**

    docker compose up -d

    Verify the container:

    docker compose ps

5. **Run the Data Extraction & Loading Pipeline**

    python extract_load.py

    This retrieves the weather data and loads it into:

    raw_weather.weather_observations

6. **Run dbt**

    Navigate into the dbt project:

    `cd weather_transform`

    Run the transformation:

    `dbt build`

    This builds the satging and mart models while executing while executing the configured data quality tests.

7. **Run Analysis**

    Return to the project root:

    cd ..
    python analyze.py

    The script generates:

    weather_comparison.png


## Key Data Engineering Concepts Demonstrated

**ELT Architecture**

The project separates extraction/loading from transformation, allowing raw data to be retained before analytical transformations are applied.

**Data Layering**

The pipeline uses distinct raw, staging, and mart layers:

    RAW → STAGING → MART

This separation makes transformations easier to maintain and debug.

**SQL Transformations**

* CTEs
* Aggregations
* Type casting
* Conditional logic
* `RANK()`
* `LAG()`
* Rolling averages
* `GROUP BY`
* `ORDER BY`

**Automated Data Validation**

dbt tests are integrated into the transformation workflow so data issues can be detected before reaching downstream analytical models.

**Containerization**

PostgreSQL runs inside Docker, providing an isolated and reproducible database environment.

**Anomaly Detection**

Window functions are used to identify unusual temperature changes rather than simply reporting historical aggregates.


## What This Project Demonstrates

This project demonstrates the ability to:

* Build an end-to-end data pipeline from an external API
* Work with relational databases and PostgreSQL
* Develop SQL transformation models with dbt
* Implement automated data quality checks
* Diagnose and resolve data integrity issues
* Use window functions for analytical processing
* Containerize development infrastructure with Docker
* Analyze transformed datasets using Python and pandas
* Produce data visualizations for analytical insights

## Potential Future Improvements

Possible extensions include:

* Add additional cities and weather variables.
* Schedule automated pipeline execution
* Store historical API snapshots instead of replacing raw data
* Add incremental dbt models
* Introduce Airflow or another orchestration platform
* Add a BI dashboard using Power BI or Tableau
* Add CI/CD validation for dbt models
* Add more sophisticated anomaly-dimension rules
* Deploy the pipelines to a cloud data platform

## Skills Demonstrated

**Data Engineering**: 
* ETL pipelines
* ETL/ELT architecture
* API ingestion
* Data transformation
* Data quality
* Data modeling

**Programming**:
* Python
* SQL
* pandas

**Database**:
* PostgreSQL
* psycopg2

**Data Transformation**:
* dbt
* CTEs
* Window Functions
* Aggregations
* Testing

**Infrastructe**:
* Docker
* Docker Compose
* Containerized PostgreSQL

**Analytics & Visualization**:
* pandas
* matplotlib
* Anomaly Detection
* Data Analysis






