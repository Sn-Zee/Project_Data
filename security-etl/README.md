<h1 align="center">Security Log ETL Pipeline with dbt</h1>

End-to-end security analytics pipeline that transforms raw security logs into tested, analytics-ready threat intelligence using Python, PostgreSQL, dbt, and Streamlit.

## **Project Overview**
Security teams generate large volumes of authentication and system activity logs, but raw security data often contains inconsistent values, missing fields, invalid IP addresses, and other data-quality issues.

This project demonstrates an end-to-end ETL pipeline for security analytics that takes intentionally messy security event data and transforms it into actionable threat-detection datasets.

The pipeline:

**Python Generator --> PostgreSQL Raw Data --> dbt Staging --> dbt Mart Models --> Streamlit Dashboard**

The project processes **5,000 synthetic security events**, cleans and validates the data using dbt, detects suspicious activity using SQL analytics, and presents the results through an interactive Streamlit dashboard

## **Objectives**

* Build a complete ETL/ELT workflow using Python, PostgreSQL, and dbt
* Simulate realistic security-log data quality problems
* Clean and normalize raw security events using SQL
* Implement automated dbt data-quality tests
* Detect brute-force login patterns using SQL window functions
* Identify after-hours and weekend security activity 
* Build analytics-ready mart tables for downstream consumption
* Create an interactive dashboard for security investigation
* Demonstrate practical data engineering and security analytics skills

## **Architecture**
```
                    ┌─────────────────────┐ 
                    │ Python Generator    │ 
                    │                     │
                    │ 5,000 Security      │ 
                    │ Events              │ 
                    └──────────┬──────────┘
                               │ 
                               ▼ 
                    ┌─────────────────────┐
                    │      PostgreSQL     │
                    │                     │
                    │ raw_security_events │ 
                    └──────────┬──────────┘ 
                               │ 
                               │ dbt source
                               ▼ 
                    ┌─────────────────────┐
                    │      dbt Staging    │
                    │                     │ 
                    │ stg_security_events │ 
                    │                     │
                    │ • Normalize values  │
                    │ • Validate IPs      │
                    │ • Handle NULLs      │
                    │ • Derive time data  │
                    └──────────┬──────────┘
                               │ 
                               ▼ 
                ┌────────────────────────────────┐
                │           dbt Marts            │
                │                                │
                │ ┌────────────────────────────┐ │ 
                │ │ mart_brute_force_attempts  │ │
                │ │                            | │
                │ │ 5+ failed logins/hour      │ │
                │ └────────────────────────────┘ │
                │                                │
                │ ┌────────────────────────────┐ │
                │ │ mart_after_hours_access    │ │
                │ │                            | │
                │ │ Off-hours/weekend activity │ │
                │ └────────────────────────────┘ │ 
                └───────────────┬────────────────┘
                                │
                                ▼ 
                     ┌─────────────────────┐
                     │ Streamlit Dashboard │
                     │                     │
                     │ • KPIs              │
                     │ • Threat tables     │
                     │ • Risk charts       │
                     │ • Date filtering    │
                     │ • Event drill-down  │
                     └─────────────────────┘
```

## **Data Pipeline**

1. **Generate Security Events

A python data generator creates **5,000 synthetic security events** with intentional data-quality problems.

Examples include:

* Mixed-case usernames
* Inconsistent event-type casing
* Missing usernames and departments
* Invalid IP addresses
* Empty Strings
* Missing Boolean values
* Invalid or negative session durations
* Incosistent risk-level formatting

This simulates the types of problems that can occur in real-world security data.

2. **Load Raw Data into PostgreSQL**

The generated data is converted into a pandas DataFrmae and loaded into PostgreSQL using SQLAlchemy

`raw_security_events`

The raw layer intentionally preserves the orginal data so that transformations can be performed downstream.

3. **Transform Data with dbt**

The dbt transformation layer follows a staging -> marts structure.

**Staging**

The staging model:

* Standardizes usernames
* Normalizes event types
* Cleans department and risk-level values
* Converts invalid IP addresses to NULL
* Removes invalid session durations
* Derives event hjour
* Derives day-of-week
* Handles NULL and empty-string values

Example transformation:
```
lower(
    trim(
        coalesce(
            nullif(username, ''),
            'unknown'
        )
    )
) AS username
```

This ensures values such as:

jsmith \
JSMITH \
JSmith

are normalized before being used for analytics

## Threat Detection  Models

**Brute-Force Detection**

The `mart_brute_force_attempts` model identifies potential brute-force login activity.

Detection logic:

```
LOGIN_FAILURE events
        ↓
Group by username + source IP + hour
        ↓
Count failures using a window function
        ↓
Keep windows with ≥ 5 failures
        ↓
Return attack window and timestamps
```

The model uses PostgreSQL window functions:
```
count(*) over (
    partition by
        username,
        source_ip,
        date_trunc('hour', event_timestamp)
)
```

This preserves individual event records while calculating the number of failures occurring within each hourly window.

## After-Hours Access Detection

The `mart_after_hours_access` model identifies activity occurring:

* Before 6:00 AM
* After 8:00 PM
* On weekends

It aggregates activity by user and department and calculates:

* Total after-hours events
* Unique source IPs
* High/critical-risk events
* First and last observed activity
* Distinct event types

The models also uses PostgreSQL `FILTER` clause and `array_agg()` for analytical aggregation.

## Data Quality Testing

dbt tests are included to validate the transformation layer before the data reaches the dashboard.

Current tests include `not_null` validation for imporatant fields such as:

* Username
* Event type
* Event timestamp
* Brute-force failure count
* After-hours event count

The pipeline can be validated using:

dbt test

This helps prevent incomplete or invalid data from reaching downstream analytics.

## Streamlit Dashboard

The Streamlit dashboard provides a user-friendly interface for investigatng the processed security dta.

**Dashboard Features**

KPI Metrics

* Total cleaned events
* Brute-force incidents
* After-hours users

Threat Investigation Tables

* Brute-force login attempts
* Source IP Addresses
* Failure counts
* Attack windows
* After-hours activity
* High-risk event counts
* Unique IPs

Visual Analytics

* Events by hour of day
* Events by risk level

Interactive Investigation

The dashboard also supports:

* Date-range filtering
* Event-type drill-down
* Dynamic query filtering

This turns the dashboard from a static reporting interface into a basic security invetigation tool.

## **Technology Stack**

| **Technology** | **Purpose** |
| :---: | :---: |
| Python | Data generation and pipeline scripting |
| Pandas | Data manipulation and preparation |
| SQLAlchemy | PostgreSQL database connectivity |
| PostgreSQL | Raw data storage and analytical database |
| SQL | Data transformation and threat detection |
| dbt | Transformation, modeling, testing, and analytics layer |
| Streamlit | Interactive security dashboard |
| psycopg2 | PostgreSQL connectivity |

## **Project Structure**
```
security-etl/
│ 
├── generate_logs.py 
│ 
├── dashboard.py
│ 
├── security_analytics/ 
│ ├── dbt_project.yml 
│ │ 
│ ├── models/ 
│ │     ├── staging/ 
│ │     │       ├── _sources.yml 
│ │     │       ├── schema.yml 
│ │     │       └── stg_security_events.sql 
│ │     |
| |     └── marts/
| |             ├── schema.yml
| |             ├── mart_brute_force_attempts.sql
| |             └── mart_after_hours_access.sql
| |
| ├── macros/
| ├── seeds/
| ├── snapshots/
| └── tests/
|
├── .gitignore
├── .gitattributes
└── README.md
```


## Setup

**Prerequisites
* Python 3.10+
* PostgreSQL
* Git
* Basic SQL Knowledge

1. Clone the Repository

        git clone <repository-url> \
        cd security-etl

2. Create a Virtual Environment

        Windows:

        python -m venv .venv \
        .venv\Scripts\activate

3. Install Dependencies 
        
        pip install pandas psycopg2-binary SQLAlchemy streamlit
        pip install "dbt-core<2.0" dbt-postgres

4. Create the PostgreSQL Database

        CREATE DATABASE security_logs;

        \c security_logs

        CREATE SCHEMA analytics;

5. Configure dbt

        Create your local dbt profile at:

        ~/.dbt/profiles.yml

        Windows:
        
        %USERPROFILE%\.dbt\profiles.yml

        Configure the PostgreSQL connection for the `security_logs` database and `analytics` schema

6. Verify dbt

        cd security_analytics
        dbt debug

7. Generate and Load Data

        From the project root:

        python generate_logs.py

        This creates and loads 5,000 records into:

        raw_security_events

8. Build dbt Models

        cd security_analytics

        dbt run
        dbt test

9. Launch the Dashboard

        From the project root:

        streamlit run dashboard.py

        The dashboard will be available locally through Streamlit.

## Example Analytical Questions

The pipeline can be used to answer questions such as:

* Which users experienced repeated failed login attempts?
* Which source IP addresses generated the most login failures?
* Which users exceeded the five-failure hourly threshold?
* Which users were active outside normal business hours?
* Which departments had the most after-hours activity?
* How many high-risk events occurred outside business hours?
* When during the day to security events occur most frequently?
* How are security events distributed by risk level?

## **Key Technical Concepts Demonstrated**

**Data Engineering**

* ETL/ELT pipeline design
* Raw -> staging -> mart architecture
* Relational database modeling
* Data quality handling
* SQL transformations
* Reproducible transformations with dbt


**SQL**

* CTEs
* Window functions
* `COUNT(*) FILTER`
* `GROUP BY`
* `DATE_TRUNC`
* `EXTRACT`
* Regular Expressions
* Conditional logic
* Array aggregation

**Analytics Engineering**

* dbt sources
* dbt models
* Model materialization
* Data-quality tests
* Staging and mart layers
* Dependency-based transformations

**Security Analytics**

* Authentication-event analysis
* Brute-force detection
* Risk-level analysis
* After-hours activity detection
* Source-IP analysis
* Security investigation workflows

**Data Visualization**

* KPI dashboards
* Interactive tables
* Distribution charts
* Date-range filtering
* Event-type drill-down

## **Skills Demonstrated**

This project demonstrates practical experience across **Data Analytics, Data Engineering, and Security Analytics**:

```
Python
    |
    ├── Data Generation
    ├── Data Processing
    └── PostgreSQL Integration
            │ 
            ▼
           dbt
    ┌───────┴────────┐ 
    │                │
 Staging           Marts
    |                |
Data Quality    Threat Detection
    |                |
    └───────┬────────┘
            ▼
        Streamlit
            |
            ▼
   Security Analytics
        Dashboard
```

## **Future Improvements**
Potential extensions include:

* Containerize the application with Docker
* Add CI/CD for dbt testing
* Add automated pipeline scheduling
* Add more threat-detection rules
* Integrate real security-log sources
* Add historical trend analysis
* Add authentication to the dashboard
* Add more granular investigations filters
* Add automated alerting for detected threats
* Deploy the pipeline and dashboard to a cloud environment