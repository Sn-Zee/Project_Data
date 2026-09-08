import os
import pandas as pd
import matplotlib

# Use non-interactive backend so charts save to file without a GUI
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psycopg2

# Same connection details as the extract script

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ.get("DB_NAME", "weather_db"),
    "user": os.environ.get("DB_USER", "pipeline_user"),
    "password": os.environ.get("DB_PASSWORD", "pipeline_pass"),
}

def main():
    # Connect and pull data from both marts
    conn = psycopg2.connect(**DB_CONFIG)

    # Query the daily summary for chart data
    daily_df = pd.read_sql(
        "SELECT city_name, observation_date, avg_temperature "
        "FROM weather_transform.mart_daily_weather_summary "
        "ORDER BY observation_date",
        conn,
    )

    # Query the alerts mart for anomaly data
    alerts_df = pd.read_sql(
        "SELECT city_name, observation_date, avg_temperature, "
        "day_over_day_change, alert_type "
        "FROM weather_transform.mart_weather_alerts "
        "ORDER BY observation_date",
        conn,
    )

    conn.close()

    # Create a temperature line chart for all cities
    fig, ax = plt.subplots(figsize=(12,6))
    for city in daily_df["city_name"].unique():
        city_data = daily_df[daily_df["city_name"] == city]
        ax.plot(
            city_data["observation_date"],
            city_data["avg_temperature"],
            marker="o",
            label=city,
        )

    ax.set_title("Daily Average Temperature by City")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (Celsius)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig("weather_comparison.png", dpi=150)
    print("Chart saved to weather_comparison.png")

    # Print any detected weather alerts
    if not alerts_df.empty:
        print(f"\nWeather Alerts ({len(alerts_df)} found):")
        print("-" * 60)
        for _, row in alerts_df.iterrows():
            print(
                f" {row['city_name']} on {row['observation_date']}: "
                f"{row['day_over_day_change']:+.1f} C change "
                f"({row['alert_type']})"
            )
    else:
        print("\nNo extreme weather alerts detected.")

if __name__ == "__main__":
    main()

