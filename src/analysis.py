import pandas as pd
import os
import matplotlib.pyplot as plt
from prophet import Prophet


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "cleaned")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(os.path.join(OUTPUT_DIR, "tables"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "charts"), exist_ok=True)

# Data loading
enrol = pd.read_csv(os.path.join(DATA_DIR, "enrolment_cleaned.csv"))
enrol["total_enrolment"] = (
    enrol["age_0_5"] +
    enrol["age_5_17"] +
    enrol["age_18_greater"]
)

demo = pd.read_csv(os.path.join(DATA_DIR, "demographic_cleaned.csv"))
biometric = pd.read_csv(os.path.join(DATA_DIR, "biometric_cleaned.csv"))

print("Data loaded successfully")

# ---------------------------------
# Lifecycle-based Aadhaar Analysis
# ---------------------------------

lifecycle_summary = pd.DataFrame({
    "Lifecycle Stage": ["Childhood (0–5)", "Adolescence (5–17)", "Adulthood (18+)"],
    "Total Enrolments": [
        enrol["age_0_5"].sum(),
        enrol["age_5_17"].sum(),
        enrol["age_18_greater"].sum()
    ]
})

# Save table
lifecycle_summary.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "lifecycle_enrolment_summary.csv"),
    index=False
)

print("\nLifecycle-wise Aadhaar Enrolment:")
print(lifecycle_summary)

plt.figure(figsize=(8, 6))

bars = plt.bar(
    lifecycle_summary["Lifecycle Stage"],
    lifecycle_summary["Total Enrolments"]
)

plt.xlabel("Lifecycle Stage")
plt.ylabel("Total Enrolments")
plt.title("Aadhaar Enrolment by Lifecycle Stage")

# Data labels
for bar in bars:
    h = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        h,
        f"{int(h/1_000_000)}M",
        ha="center",
        va="bottom",
        fontsize=10
    )

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "lifecycle_enrolment.png")
)

plt.close()

# ---------------------------------
# Biometric Update Stress (State-wise)
# ---------------------------------

biometric_stress = (
    biometric
    .groupby("state", as_index=False)
    .size()
    .rename(columns={"size": "biometric_updates"})
    .sort_values("biometric_updates", ascending=False)
)

# Save table
biometric_stress.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "biometric_update_stress_statewise.csv"),
    index=False
)

print("\nTop 5 states with highest biometric update stress:")
print(biometric_stress.head())

# Plot top 10 stressed states
top_bio = biometric_stress.head(10)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    top_bio["state"],
    top_bio["biometric_updates"]
)

plt.xlabel("State")
plt.ylabel("Biometric Updates")
plt.title("Top 10 States by Biometric Update Stress")
plt.xticks(rotation=60)

for bar in bars:
    h = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        h,
        f"{int(h/1000)}K",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "biometric_update_stress_statewise.png")
)
plt.close()

# Monthly Aadhaar Enrolment Trend

enrol["date"] = pd.to_datetime(enrol["date"], dayfirst=True, errors="coerce")
enrol["month"] = enrol["date"].dt.to_period("M")

monthly_enrolment = (
    enrol
    .groupby("month")["total_enrolment"]
    .sum()
    .reset_index()
)

monthly_enrolment.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "monthly_enrolment.csv"),
    index=False
)

print(monthly_enrolment.head())

monthly_enrolment["month_str"] = monthly_enrolment["month"].astype(str)

plt.figure()

bars = plt.bar(
    monthly_enrolment["month_str"],
    monthly_enrolment["total_enrolment"]
)

plt.xlabel("Month")
plt.ylabel("Total Enrolment")
plt.title("Monthly Aadhaar Enrolment Trend")
plt.xticks(rotation=45)
# ---- ADD DATA LABELS ----
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height/1000)}K",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "monthly_enrolment_trend.png")
)
plt.close()
# ------------------------------------
# State-wise Aadhaar Enrolment Ranking
# ------------------------------------

# Clean state names
enrol["state"] = (
    enrol["state"]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace("&", "AND", regex=False)
    .str.replace(" ", "", regex=False)
)

# Remove leading 'THE'
enrol["state"] = enrol["state"].str.replace("^THE", "", regex=True)

# Unified mapping for all variants
state_map = {
    "DAMANANDDIU": "DADRAANDNAGARHAVELIANDDAMANDIU",
    "DADRAANDNAGARHAVELI": "DADRAANDNAGARHAVELIANDDAMANDIU",
    "DADRAANDNAGARHAVELIANDDAMANANDDIU": "DADRAANDNAGARHAVELIANDDAMANDIU",
    "WESTBANGAL": "WESTBENGAL"
}

enrol["state"] = enrol["state"].replace(state_map)

# Remove invalid state values
enrol = enrol[
    (~enrol["state"].str.isnumeric()) &
    (enrol["state"] != "")
]

# Aggregate enrolment by state
state_enrolment = (
    enrol
    .groupby("state", as_index=False)["total_enrolment"]
    .sum()
    .sort_values(by="total_enrolment", ascending=False)
)

# Add ranking column
state_enrolment["rank"] = range(1, len(state_enrolment) + 1)

# Save output
state_enrolment.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "state_wise_enrolment.csv"),
    index=False
)

# Display insights
print("Top 5 states by enrolment:")
print(state_enrolment.head(5))

print("\nBottom 5 states by enrolment:")
print(state_enrolment.tail(5))

top10 = state_enrolment.head(10)

plt.figure()

bars = plt.bar(
    top10["state"],
    top10["total_enrolment"]
)

plt.xlabel("State")
plt.ylabel("Total Enrolment")
plt.title("Top 10 States by Aadhaar Enrolment")
plt.xticks(rotation=60)

# ---- ADD DATA LABELS ----
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{int(height/1000)}K",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "top10_states_enrolment.png")
)
plt.close()

# ---------------------------------
# Update Burden Index (UBI)
# ---------------------------------

# Clean state column in demographic & biometric datasets
for df in [demo, biometric]:
    df["state"] = (
        df["state"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace("&", "AND", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("^THE", "", regex=True)
    )

    df["state"] = df["state"].replace(state_map)
    df.dropna(subset=["state"], inplace=True)

# Aggregate updates
demo_updates = demo.groupby("state", as_index=False).size()
demo_updates.rename(columns={"size": "demographic_updates"}, inplace=True)

bio_updates = biometric.groupby("state", as_index=False).size()
bio_updates.rename(columns={"size": "biometric_updates"}, inplace=True)

# Merge all data
ubi_df = (
    state_enrolment
    .merge(demo_updates, on="state", how="left")
    .merge(bio_updates, on="state", how="left")
)

# Fill missing update counts
ubi_df[["demographic_updates", "biometric_updates"]] = (
    ubi_df[["demographic_updates", "biometric_updates"]].fillna(0)
)

# Total updates
ubi_df["total_updates"] = (
    ubi_df["demographic_updates"] + ubi_df["biometric_updates"]
)

# Update Burden Index
ubi_df["update_burden_index"] = (
    ubi_df["total_updates"] / ubi_df["total_enrolment"]
)

# Sort by highest burden
ubi_df = ubi_df.sort_values("update_burden_index", ascending=False)

ubi_df.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "update_burden_index.csv"),
    index=False
)

print("Top 5 states by Update Burden Index:")
print(ubi_df[["state", "update_burden_index"]].head())

# Plot top 10 burden states
top_ubi = ubi_df.head(10)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    top_ubi["state"],
    top_ubi["update_burden_index"]
)

plt.xlabel("State")
plt.ylabel("Updates per Enrolment")
plt.title("Top 10 States by Aadhaar Update Burden Index")
plt.xticks(rotation=60)

# Data labels
for bar in bars:
    h = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        h,
        f"{h:.2f}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "top10_update_burden_index.png")
)
plt.close()

# ---------------------------------
# Migration & Mobility Indicator
# ---------------------------------

# State-wise demographic updates (proxy for migration)
migration_updates = (
    demo
    .groupby("state", as_index=False)
    .size()
    .rename(columns={"size": "demographic_updates"})
)

# Merge with enrolment data
migration_df = (
    state_enrolment
    .merge(migration_updates, on="state", how="left")
)

migration_df["demographic_updates"] = (
    migration_df["demographic_updates"].fillna(0)
)

# Mobility Index
migration_df["mobility_index"] = (
    migration_df["demographic_updates"] /
    migration_df["total_enrolment"]
)

# Sort by highest mobility
migration_df = migration_df.sort_values(
    by="mobility_index",
    ascending=False
)

# Save table
migration_df.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "migration_mobility_index.csv"),
    index=False
)

print("\nTop 5 states by Migration & Mobility Index:")
print(migration_df[["state", "mobility_index"]].head())

# Plot top 10 migration-heavy states
top_migration = migration_df.head(10)

plt.figure(figsize=(10, 6))

bars = plt.bar(
    top_migration["state"],
    top_migration["mobility_index"]
)

plt.xlabel("State")
plt.ylabel("Mobility Index")
plt.title("Top 10 States by Aadhaar Migration & Mobility Indicator")
plt.xticks(rotation=60)

# Data labels
for bar in bars:
    h = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        h,
        f"{h:.2f}",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "migration_mobility_index.png")
)
plt.close()

# Month-on-Month Growth (%) of Aadhaar Enrolment

monthly_enrolment = monthly_enrolment.sort_values("month")

monthly_enrolment["growth_pct"] = (
    monthly_enrolment["total_enrolment"]
    .pct_change() * 100
)

plt.figure()

bars = plt.bar(
    monthly_enrolment["month_str"],
    monthly_enrolment["growth_pct"]
)

plt.xlabel("Month")
plt.ylabel("Growth (%)")
plt.title("Month-on-Month Aadhaar Enrolment Growth")
plt.xticks(rotation=45)

# Data labels
for bar in bars:
    height = bar.get_height()
    if not pd.isna(height):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}%",
            ha="center",
            va="bottom" if height >= 0 else "top",
            fontsize=9
        )

plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "charts", "monthly_growth_pct.png")
)
plt.close()

# ---------------------------------
# Predictive Insights: Forecast next 12 months
# ---------------------------------

# Convert 'month' to timestamp (if it's Period)
monthly_enrolment["month_ts"] = monthly_enrolment["month"].dt.to_timestamp()

# Prophet requires columns 'ds' (datetime) and 'y' (target)
prophet_df = monthly_enrolment[["month_ts", "total_enrolment"]].rename(
    columns={"month_ts": "ds", "total_enrolment": "y"}
)

# Initialize Prophet model
model = Prophet(
    yearly_seasonality=True,  # Capture annual seasonal spikes
    weekly_seasonality=False, # Not needed for monthly data
    daily_seasonality=False
)

# Fit model
model.fit(prophet_df)

# Create future dataframe for 12 months
future = model.make_future_dataframe(periods=12, freq='MS')  # MS = Month Start

# Predict future enrolments
forecast = model.predict(future)

# Save forecast table
forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(12).rename(
    columns={'ds': 'month', 'yhat': 'predicted_enrolment', 
             'yhat_lower': 'lower_bound', 'yhat_upper': 'upper_bound'}
)
forecast_df.to_csv(os.path.join(OUTPUT_DIR, "tables", "monthly_enrolment_forecast.csv"), index=False)

print("Prophet forecast for next 12 months saved:")
print(forecast_df)

# Plot Historical + Forecast
plt.figure(figsize=(10, 6))

# Historical data (use month_ts, not month)
plt.plot(monthly_enrolment["month_ts"], monthly_enrolment["total_enrolment"],
         label="Historical", marker='o')

# Add labels for historical points
for x, y in zip(monthly_enrolment["month_ts"], monthly_enrolment["total_enrolment"]):
    plt.text(x, y, f"{int(y/1000)}K", ha="center", va="bottom", fontsize=8)

# Forecasted data
plt.plot(forecast_df["month"], forecast_df["predicted_enrolment"],
         label="Forecast (Next 12 months)", linestyle='--', marker='x', color='red')

for x, y in zip(forecast_df["month"], forecast_df["predicted_enrolment"]):
    plt.text(x, y, f"{int(y/1000)}K", ha="center", va="bottom", fontsize=8, color='red')


plt.xlabel("Month")
plt.ylabel("Total Enrolment")
plt.title("Monthly Aadhaar Enrolment Forecast (Prophet)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

plt.savefig(os.path.join(OUTPUT_DIR, "charts", "monthly_enrolment_forecast_prophet.png"))
plt.close()


forecast_df.to_csv(
    os.path.join(OUTPUT_DIR, "tables", "monthly_enrolment_forecast.csv"),
    index=False
)
print("Forecast for next 12 months saved:")
print(forecast_df)
