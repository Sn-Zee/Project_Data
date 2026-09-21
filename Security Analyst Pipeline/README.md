<h1 align="center"> Security Analytics Pipeline </h1>

An end-to-end security analytics and ELT pipeline built with Python, PostgreSQL, dbt, SQL, and Docker. The project transforms messy authentication logs into clean, analytics-ready datasets and automatically detects potential brute-force login attacks using SQL window functions.

## **Project Overview**

Securtiy logs often contain incosistent timestamps, mixed casing, missing values, and duplicate records, making reliable analysis difficults.

This project demonstrates how to build a layered data pipeline that:

* Ingests raw authentication events into PostgreSQL
* Cleans and standardizes data using **dbt staging models**
* Performs security analytics using **CTEs and SQL window functions**
* Detects brute-force login patterns using a **10-minute sliding window**
* Calculates daily login and failure-rate statistics
* Applies automated **dbt data quality tests**
* Generate **dbt documentation and data lineage**
* Containerizes the pipeline using **Docker and Docker Compose**

## **Project Objectives**

The main objectives of this project are to:

1. Load simulated authentication events into a PostgreSQL database
2. Store raw data in an intentionally unclean format to represent an ingestion layer.
3. Clean, standardize, and deduplicate authentication records using dbt.
4. Build analytics models for login activity and failure-rate analysis.
5. Detect possible brute-force attacks using time-based SQL window functions.
6. Add automated data quality tests to validate transformed datasets.
7. Generate dbt documentation and view model dependencies through a lineage graph.
8. Containerize the pipleline components using Docker Compose

## **Pipeline Architecture**

```
Python Data Generator
        │ 
        ▼
PostgreSQL Raw Layer
(raw.auth_events)
        │ 
        ▼
dbt Staging Layer
(stg_auth_events)
        │ 
        ├───────────────┐
        ▼               ▼
Login Analytics     Brute-Force
                    Detection
        │               │
        ▼               ▼
fct_login_attempts   fct_brute_force_detection
        │               │
        └───────┬───────┘
                ▼
        Analytics-Ready Data
```
|**Technology**|**Purpose**|
|:---:|:---:|
|Python|Security event generation and data ingestion|
|PostgreSQL|Relational database and analytics storage
|dbt|Data transformation testing, documentation, and lineage|
|SQL|Data cleaning and security analytics|
|Docker|Pipeline containerazation|
|Docker Compose|Multi-container orchestration|
|Git/GitHub|Version control and project documentation|

## **Project Structure**
```
Security Analytics Pipeline/
│ 
├── security_analytics/
│   ├── models/
│   │    ├── staging/
│   │    │   ├── __sources.yml
│   │    │   ├── stg_auth_events.sql
│   │    │   └── schema.yml
│   │    │
│   │    └── marts/
│   │        ├── fct_login_attempts.sql
│   │        ├── fct_brute_force_detection.sql
│   │        └── schema.yml
│   │
│   └── dbt_project.yml
│
├── load_security_data.py
├── profiles.yml
├── docker-compose.yml
├── Dockerfile
├── README.md
└── logs/
```

## **Data Ingestion**

The Python loader generates simulated authentication events and inserts them into the PostgreSQL raw layer.

The generated dataset includes approximately:

* 500 base authentication events
* 20 intentionally planted failed-login events
* 15 exact duplicate records
* Approximately 535 total raw records

The planted failed-login patterns uses:

* A common source IP address
* A single targeted user account
* Multiple failed-login events
* Very short intervals between attempts

This controlled pattern makes it possible to validate whether the brute-force detection logic works as expected.

**Raw Table**

raw.auth_events

The raw table stores incoming fields as text to simulate a typical ingestion layer where data types and formats have not yet been standardized.

The raw data includes fields such as:

* Event ID
* Event timestamp
* Event type
* Authentication status
* User ID
* Source IP address

## **Data Cleaning and Standardization**

The dbt staging model transforms the raw authentication data into a consistent structure.

The staging layer performs the following operations:

**Event Type and Status Standardization**

Text fields are cleaned using trimming and uppercase conversion to ensure that values such as:

failed_login \
FAILED_LOGIN \
 Failed_Login

are treated consistently.

**User ID Normalization**

User identifiers are trimmed and converted to lowercase to reduce inconsistencies caused by capitalization or accidental whitespace.

**Timestamp Parsing**

The staging model suppots multiple timestamp formats and converts them into a consistent timestamp reepresentation.

Records with invalid or missing timestamps are excluded from the staging model because they cannot be reliably used for time-based analysis.

**IP Address Cleaning**

Blank IP address values are converted to `NULL` so that missing values can be handled consistently during analysis.

**Duplicate Removal**

Duplicate authentication records are removed using PostgreSQL deduplication logic based on the event identifier and event ordering.

**Staging Output**

stg_auth_events

The staging model is materialized as a **view**, allowing downstream models to use a standardized representation of the raw data without duplicating the full dataset.

## **Analytics Models**

The project includes two primary dbt mart models.

1. `fct_login_attempts`

This model produces daily login activity statistics.

It focuses on login and failed-login events and calculates metrics such as:

* Total login attempts
* Successful login attempts
* Failed login attempts
* Number of unique source IP address
* Daily login failure rate
* User-level login activity

The model also generates a deterministic surrogate key for each aggregated record using an MD5-based key.

Example analytical questions supported by this model include:

* How many login attempts did a user make in one day?
* What percentage of a user's login attempts failed?
* Which users experienced unusually high login failure rates?
* How many unique IP addresses attempted to access an account?

2. `fct_brute_force_detection`

This model identifies suspicious failed-login activity using SQL window functions.

The detection logic uses:

* `ROW_NUMBER()`
* `COUNT(*) OVER(...)`
* `LAG()`
* Common table expressions
* A rolling time window

The model examines failed-login events grouped by user and source IP address. It then calculates how many failures occurred within a defined **10-minute rolling window.**

An event is flagged when the number of failed attempts within that time window reaches or exceeds the configured threshold.

The detection model produces information such as:

* Event ID
* User ID
* Source IP address
* Event timestamp
* Sequence number
* Number of failures within the rolling window
* Previous event timestamp
* Brute-force detection indicator

**Brute-Force Detection Logic**

```
Group failed-login events by user and source IP
                │ 
                ▼
Order events chronologically
                │ 
                ▼
Calculate rolling feature count
within the previous 10 minutes
                │ 
                ▼
Compare failure count against threshold
                │ 
                ▼
Return suspicious events
```

The planted test pattern contains 20 rapid failed-login events from the same source IP targeting the same user. Because these attempts occur within a short time period, the model should identify the pattern as suspicious once the rolling failure count reaches the configured threshold

## **Data Quallity Testing**

dbt tests are used to verify the reliability and consistency of the transformed data.

The project includes tests such as:

**Staging Model Tests**
* `not_null` tests for event IDs
* `not_null` tests for parsed timestamps
* `accepted_values` tests for event types

**Mart Model Tests**
* `unique` tests for generated login statistic IDs
* `not_null` tests for login statistic IDs
* `not_null` tests for brute-force detection event IDs

These tests help identify issues such as:

* Missing primary identifiers
* Invalid event categories
* Duplicate analytical records
* Incomplete timestamp values
* Unexpected transformation results

The tutorial workflow includes running the dbt test suite and validating that the configured tests pass

## dbt Documentation and Lineage

The project uses dbt documentation features to make the transformation workflow easier to understand and maintain.

The generated documentation includes:

* Model descriptions
* Source definitions
* Column-level metadata
* Data quality tests
* Model dependencies
* Transformation lineage

The lineage graph represents the flow of data from the raw PostgreSQL source through the staging model and into the analytics marts:
```
raw.auth_events
        │ 
        ▼
stg_auth_events
        │
        ├──────────────► fct_login_attempts
        |
        └──────────────► fct_brute_force_detection
```

This makes it easier to trace where analytical results originate and understand how changes to upstream models may affect downstream datasets.

## **Docker and Reproducibility**

The project includes a Docker-based deployment approach intended to make the pipeline easier to run consistently across environments.

The containerized workflows is designed to coordinate:

1. PostgreSQL startup
2. Raw authentication data loading
3. dbt staging transformations
4. dbt mart transformations
5. Data quality testing

Environment variables are used for database configuration, including values such as:

DB_HOST \
DB_PORT \
DB_NAME \
DB_USER \
DB_PASSWORD 

This approach avoids hardcoding environment-specific database settings directly into the application code.

The Docker setup also supports a more reproducible development workflow by reducing differences between local environments.

## **Running the Project**

1. **Create and activate a Python virtual environment**

`python -m venv .venv`

2. **Install dependencies**

`pip install dbt-postgres psycopg2-binary`

Install any additional dependencies required by the project configuration.

3. **Configure PostgreSQL**

Create or configure a PostgreSQL database with the following general settings:

**Host**: localhost \
**Port**: 5432 \
**Database**: security_analytics \
**Schema**: analytics

4. **Load the raw security data

`python load_security_data.py`

This creates the raw authentication table and inserts the simulated event records.

5. **Run dbt transformations**

`dbt run`

6. **Run data quality tests**

`dbt test`

7. **Generate dbt documentation**

`dbt docs generate`

8. **Start the dbt documentation server**

`dbt docs serve`

9. Run with Docker Compose

If the Docker configuration is available:

`docker compose up --build`

The exact command sequence may depend on the final Docker Compose service configuration.

## **Example Analytical Use Cases**

The resulting models can support security and operational analysis such as:

* Identifying accounts with repeated failed-login attempts
* Detecting possible credential-stuffing or brute-force behavior
* Monitoring daily authentication failures rates
* Investigating suspicious source IP addresses
* Comparing successful and failed login activity
* Building dashboards for authentication monitoring
* Supporting security operations investigations
* Providing structured data for downstream reporting and alerting systems


## **Key Technical Features**

**Data Engineering**

* Raw, staging, and mart-style data layers
* Python-based data ingestion
* PostgreSQL data storage
* Data cleaning and transformation workflows
* Reproducible pipeline execution

**SQL and Analytics**

* Common table expressions
* Aggregations and calculated metrics
* PostgreSQL-specific timestamp handling
* Deduplicaiton logig
* MD5-based surrogate keys
* Window functions
* Rolling time-window analysis
* Event sequencing with `ROW_NUMBER()` and `LAG()`

**dbt**

* Source configuration
* Staging models
* Analytical mart models
* View and table materializations
* Schema tests
* Data documentation
* Model lineage

**Security Analytics**

* Authentication event analysis
* Login failure-rate calculations
* Suspicious login pattern detection
* Brute-force attack identification
* Source IP and user-based event grouping

**DevOps and Deployment**

* Environment-variable configuration
* Dockerfile-based containerization
* Docker Compose orchestration
* Reproducible development environments

##  **Project Outcome**

This project demonstrates how raw and incosistent security event data can be transformed into structured, analytics-ready datasets using a modern ELT workflows.

It combines security domain knowledge with practical data engineering techniques to produces:

* Cleaned authentication data
* Daily login analytics
* Failure-rate metrics
* Brute-force detection results
* Automated data quality validation
* Documented dbt model dependencies
* A foundation for containerized execution

The project is designed as a practical example of applying **Python, SQL, PostgreSQL, dbt, and Docker** to security monitoring and data analytics problems.

## **Future Improvements**

Potential future enhancements include:

* Connecting the pipeline to real authentication log sources
* Adding incremental dbt models for larger datasets
* Implementing more advanced anomaly detection
* Adding additional attack-pattern models
* Creating a Streamlit or Power BI dashboard
* Adding automated pipeline scheduling
* Integrating alert notificaitons for detected threats
* Adding CI/CD validation for dbt tests
* Introducing data freshness and source-volume tests
* Extending the pipeline to support cloud data warehouses

## **Skills Demonstrated**

* Python data ingestion
* SQL development
* PostgreSQL database management
* ELT pipeline design
* Data cleaning and transformation
* dbt model development
* SQL window functions
* Security analytics
* Brute-force attack detection
* Data quality testing
* Data documentations and lineage
* Docker containerization
* Environment-based configuration
* Git and GitHub project management



