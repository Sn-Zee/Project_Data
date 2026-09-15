
<h1 align="center"> Network Threat Analytics Pipeline </h1>

A Python-based ETL and threat analytics pipeline that processes 2.8M+ network flow records from the CICIDS2017 intrusion detection dataset, cleans and transforms the data into a PostgreSQL star schema, runs threat detection queries, and provides an interactive Streamlit dashboard

## Project Overview 

The project demonstrates an end-to-end data engineering and security analytics workflow:

CICIDS2017 CSV Files → Python ETL → PostgreSQL Star Schema → SQL Threat Detection → Streamlit Dashboard

The pipeline addresses common problems found in raw network security data, including:

* Messy column names
* Missing (`NaN`) values
* `Infinity` and `-Infinity` values
* Duplicate reocrds
* Flat, difficult-to-query datasets
* Incosistent attack labels

The final system provides both **known-threat analysis** and **statistical anomaly detection**


## Technologies Used
* Python
    * pandas
    * NumPy
    * SciPy
    * psycopg2
    * SQLAlchemy
* PostgreSQL
* SQL
* Streamlit
* CICIDS2017 Dataset
* Git/Github

## Project Structure

```
Threat Pipeline/ 
│ 
|── dashboard/
|   └── dashboard.py
|
├── data/ 
|   ├── .gitattributes
│   └── CICIDS2017 CSV files
| 
├── sql/
|   ├── queries.sql 
|   └── schema.sql  
|
├── src/
|   ├── load_raw.py
|   └── etl_pipeline.py
├── venv/
| 
├── .gitattributes 
├── .gitignore
├── README.md 
└── requirements.txt
```

## Pipeline Workflow
**1. Environment Setup**

Created an isolated Python virtual environment and installed the required packages

```
python -m venv venv
venv\Scripts\activate
pip install psycopg2-binary==2.9.12 streamlit==1.61.1 pandas scipy
```

Created the PostgreSQL databse:

``` CREATE DATABASE threat_analytics;```

**2. Raw Data Loading** 

The intial loading process reads all CSV file from `data/` using pandas and combines them into a single PostgreSQL table:

CSV Files
    ↓
pandas DataFrames
    ↓
Combined DataFrame
    ↓
PostgreSQL raw_flows

The raw dataset contains **2.8M+ network flow records and approxiamtely 79 columns**

This initial approach was intentionally used to identify data quality and modeling probllems before building the final ETL pipeline

**3. Data Quality Analysis**\
Exploratory SQL queries identifies several issues in the raw dataset:

* Leading/trailing spaces in column names
* Missing values in network flow metrics
* `Infinity` and `-Infinity` values
* More than 300,000 duplicate records
* Difficult-to-maintain analytical queries

For example, the origianl attack label required referencing a column such as:

" Label"

instead of the cleaner:

Label

These issues motivated the development of the cleaned ETL pipeline and star schema

**4. Star Schema Design**\
The final database uses a **star schema** consisting of two dimension tables and one central fact table.

**Dimension Tables**

`dim_attack_type`

Stores attack labels and their broader categories

Examples:

BENIGN          → Benign \
DoS Hulk        → DoS \
FTP-Patator     → Brute Force \
PortScan        → Port Scan \
DDoS            → DDoS \
Bot             → Botnet

`dim_protocol`

Maps protocol numbers to readable protocol names

Examples:

6   →   TCP \
17  →   UDP

**Fact Table**

`fact_flows`

Stores the cleaned network flow measurements, including:

* Destination port
* Flow duration
* Forward/backward packet counts
* Forward/backward packet lengths
* Flow bytes per secord
* Flow packets per second
* Packet length statistics
* Attack type ID
* Protocol ID
* Anomaly score

The resulting structure is:

            dim_attack_types
                   |
                   |
                   ▼
             fact_flows
                   ▲
                   |
                   |
             dim_protocol

This separates descriptive attributes from measurable network-flow data and makes analytical queries easier to maintain.

**5. ETL Pipeline**\
`etl_pipeline.py` performs the complete transformation process.

**Extract**

Reads all CICIDS2017 CSV files from the `data/` directory.

**Transform**

The pipeline:

1. Combines all input CSV files.
2. Strips whitespace from column names.
3. Replaces `Infinity` and `-Infinity` with `NaN`
4. Removes rows containing missing numeric values.
5. Removes duplicate records.
6. Maps attack labels to broader attack categories.
7. Maps protocol numbers to readable names.
8. Converts raw dimension values into foreign-key IDs.
9. Selects the required fact-table columns.
10. Calculates anomaly scores.

**Load**

Cleaned records are loaded into:

dim_attack_type
dim_protocol
fact_flows

The pipeline also produces a data quality report containing:

* Total raw rows
* Rows removed due to invalid values
* Duplicate rows removed
* Final rows loaded
* Number of attack types
* Number of protocols

Run the ETL pipeline with:

`python etl_pipeline.py`

**6. Threat Detection Queries**

`queries.sql` contains analytical SQL queries for security investigation.

**Attack Type Analysis**\
Ranks individual attack types by flow volume and calculates their percentage of total traffic.

Uses:
* `JOIN`
* `GROUP BY`
* `COUNT`
* Window functions

**Attack Category Analysis**

Groups network flows into broader categories such as:

* Benign
* DoS
* DDoS
* Brute Force
* Botnet
* Port Scan
* Web Attack

**Suspicious Flow Detection**

Uses PostgreSQL's `PERCENTILE_CONT()` to identify flows above the 99th percentile of flow bytes per second

This surfaces the highest-volume flows for further investigation.

Run the queries with:

psql -U postgres -d threat_analytics -f queries.sql

**7. Streamlit Threat Dashboard**\
`dashboard.py` provides an interactive web interface for exploring the processed data.

Run the dashboard with:

streamlit run dashboard.py

**Threat Overview**

The dashboard includes:

* Total flows analyzed
* Percentage of malicious traffic
* Number of attack types detected
* Attack category filter
* Attack distribution chart
* Attack type detail table
* High-risk flow table

The sidebar allows users to filter attack categories interactively.

**8. Anomaly Detection**

The project was extended with a statistical anomaly detection
system.

The pipeline calculates absolute z-scores across four network-flow metrics:

Flow Duration\
Total Forward Packets\
Total Backward Packets\
Flow Bytes/sec

The four z-scores are combined into a composite:

Anomaly Score = Average of the four absolute z-scores

A higher score indicates that a flow is statistically unusual across multiple network characteristics.

The anomaly score is stored directly in:

fact_flows.anomaly_score

Anomaly Detection Dashboard

A dedicated Anomaly Detection tab was added to Streamlit.

It provides:

* Scatter plot of `flow_bytes_per_sec` vs. `anomaly_score`
* Attack-type classification
* Top 20 anomalous flows
* Key network-flow metrics for investigation

This extends the project beyond detecting previously labeled attacks and demonstrates how statistical methods can identify potentially unusual behavior.

## Running the Project

**1. Activate the environment**

``venv\Scirpts\activate``

**2. Make sure PostgreSQL is running**

The project expects:

**Database**: threat_analytics\
**Host**: localhost\
**Port**: 5432\
**User**: postgres

**3. Run the ETL pipeline**

``python etl_pipeline.py``

**4. Run analytical queries**

``psql -U postgres -d threat_analytics -f queries.sql``

**5. Launch the dashboard**

``streamlit run dashboard.py``


## Key Skill Demonstrated

**Data Engineering**

* Python ETL development
* Large CSV processing
* Data cleaning and validation
* PostgreSQL data loading
* SQLAlchemy
* Database schema design
* Star schema modeling
* Dimension/fact table relationships

**Data Analytics**

* SQL aggregation
* Window functions
* Statistical percentile analysis
* Z-score anomaly detection
* Exploratory data analysis
* Security-focused metrics

**Security Analytics**

* Network traffic analysis
* Attack classification
* Brute-force detection
* DoS/DDoS analysis
* Port scan analysis
* High-volume flow detection
* Statistical anomaly detection

**Visualization**

* Streamlit dashboard development
* Interactive filters
* Metric cards
* Bar charts
* Scatter plots
* Investigative data tables

## Project Outcome

This project demonstrates an end-to-end pipeline that transforms **2.8M+ raw network-flows records** into a structured analytics system.

The final architecture combines:

```
Raw Network Data
       ↓
Python ETL
       ↓
Data Quality Cleaning
       ↓
PostgreSQL Star Schema
       ↓
SQL Threat Detection
       ↓
Statistical Anomaly Detection
       ↓
Interactive Streamlit Dashboard
```

The project showcases practical experience in **data engineering, SQL analytics, Python, PostgreSQL, security analytics, and dashboard development** while connecting cybersecurity experience with data-focused engineering skills.