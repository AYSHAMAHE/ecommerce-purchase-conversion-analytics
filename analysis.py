"""
E-Commerce Purchase Conversion Analytics
Data Analytics with AI Internship Capstone

Dataset:
UCI Online Shoppers Purchasing Intention Dataset
https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)

def load_data():
    """Load the UCI dataset through ucimlrepo."""
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=468)
    X = ds.data.features.copy()
    y = ds.data.targets.copy()
    df = pd.concat([X, y], axis=1)
    return df

def prepare_data(df):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    df["Revenue"] = df["Revenue"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["Weekend"] = df["Weekend"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["Purchase"] = df["Revenue"].astype(int)

    # Business-friendly labels
    df["Visitor_Group"] = df["VisitorType"].replace({
        "Returning_Visitor": "Returning Visitor",
        "New_Visitor": "New Visitor",
        "Other": "Other"
    })
    return df

def save_bar(series, title, xlabel, ylabel, filename, rotation=0):
    ax = series.plot(kind="bar", figsize=(9, 5))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    plt.savefig(OUTPUT / filename, dpi=180)
    plt.close()

def run_analysis(df):
    summary = {
        "sessions": len(df),
        "purchases": int(df["Purchase"].sum()),
        "conversion_rate_pct": round(df["Purchase"].mean() * 100, 2),
        "avg_product_pages": round(df["ProductRelated"].mean(), 2),
        "avg_product_duration_min": round(df["ProductRelated_Duration"].mean() / 60, 2),
        "avg_page_value": round(df["PageValues"].mean(), 2),
    }

    # 1. Conversion by visitor type
    visitor_conv = (df.groupby("Visitor_Group")["Purchase"]
                      .agg(["count", "sum", "mean"])
                      .sort_values("mean", ascending=False))
    visitor_conv["conversion_rate_pct"] = visitor_conv["mean"] * 100
    save_bar(visitor_conv["conversion_rate_pct"],
             "Conversion Rate by Visitor Type",
             "Visitor Type", "Conversion Rate (%)",
             "conversion_by_visitor.png")

    # 2. Conversion by month
    month_order = ["Feb","Mar","May","June","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_conv = df.groupby("Month")["Purchase"].mean().reindex(month_order).dropna() * 100
    save_bar(month_conv, "Conversion Rate by Month", "Month",
             "Conversion Rate (%)", "conversion_by_month.png")

    # 3. Conversion by weekend
    weekend_conv = df.groupby("Weekend")["Purchase"].mean() * 100
    weekend_conv.index = ["Weekday" if x is False else "Weekend" for x in weekend_conv.index]
    save_bar(weekend_conv, "Conversion Rate: Weekday vs Weekend",
             "Visit Timing", "Conversion Rate (%)", "conversion_weekend.png")

    # 4. Page-value bands
    bins = [-0.001, 0, 5, 20, 50, np.inf]
    labels = ["0", "0–5", "5–20", "20–50", "50+"]
    df["PageValueBand"] = pd.cut(df["PageValues"], bins=bins, labels=labels)
    pv_conv = df.groupby("PageValueBand", observed=False)["Purchase"].mean() * 100
    save_bar(pv_conv, "Conversion Rate by Page Value Band",
             "Page Value Band", "Conversion Rate (%)", "conversion_page_value.png")

    # 5. Traffic type
    traffic_conv = (df.groupby("TrafficType")["Purchase"].mean() * 100).sort_values(ascending=False).head(10)
    save_bar(traffic_conv, "Top Traffic Types by Conversion Rate",
             "Traffic Type", "Conversion Rate (%)", "conversion_traffic.png")

    # 6. Exit rate vs conversion
    df["ExitRateBand"] = pd.qcut(df["ExitRates"], 5, duplicates="drop")
    exit_conv = df.groupby("ExitRateBand", observed=False)["Purchase"].mean() * 100
    save_bar(exit_conv, "Conversion Rate across Exit-Rate Segments",
             "Exit Rate Segment", "Conversion Rate (%)",
             "conversion_exit_rate.png", rotation=25)

    pd.DataFrame([summary]).to_csv(OUTPUT / "kpi_summary.csv", index=False)
    visitor_conv.to_csv(OUTPUT / "visitor_conversion.csv")
    month_conv.to_csv(OUTPUT / "month_conversion.csv")
    weekend_conv.to_csv(OUTPUT / "weekend_conversion.csv")
    pv_conv.to_csv(OUTPUT / "page_value_conversion.csv")
    traffic_conv.to_csv(OUTPUT / "traffic_conversion.csv")
    exit_conv.to_csv(OUTPUT / "exit_rate_conversion.csv")

    return summary

if __name__ == "__main__":
    df = prepare_data(load_data())
    summary = run_analysis(df)
    print("\nPROJECT KPIs")
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("\nAnalysis complete. Charts and tables are in ./outputs/")
