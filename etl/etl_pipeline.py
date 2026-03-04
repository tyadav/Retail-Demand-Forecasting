
# 1. Imports & Configuration
import pandas as pd
import numpy as np
from pathlib import Path
import json


# 2. Load Raw Data
def load_raw_data(data_dir):
    #data_dir = Path("C:/Tej/BITSoM/Projects/Capstone/data/Retail Demand Forecasting & Inventory Replenishment Planner")
    data_dir = Path(data_dir)

    sales = pd.read_csv(data_dir / "sales_daily.csv", parse_dates=["date"])
    inventory = pd.read_csv(data_dir / "inventory_daily.csv", parse_dates=["date"])
    stores = pd.read_csv(data_dir / "stores.csv")
    calendar = pd.read_csv(data_dir / "calendar.csv", parse_dates=["date"])
    purchase_orders = pd.read_csv(data_dir / "purchase_orders.csv", parse_dates=["order_date", "expected_receipt_date"])

    with open(data_dir / "products.json", "r") as f:
        products_raw = json.load(f)
    products = pd.json_normalize(products_raw)

    return sales, inventory, stores, calendar, purchase_orders, products

# 3. Key Standardization (CRITICAL)
def standardize_keys(df):
    for col in ["store_id", "sku_id"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().str.strip()
    return df

# 4. Clean Sales Data
def clean_sales_data(sales, products):
    sales = standardize_keys(sales)
    products = standardize_keys(products)

    sales = sales.drop_duplicates(subset=["date", "store_id", "sku_id"])

    sales["units_sold"] = sales["units_sold"].clip(lower=0)
    sales["units_sold"] = sales["units_sold"].fillna(0)

    sales = sales.merge(
        products[["sku_id", "price", "cost", "category"]],
        on="sku_id",
        how="left"
    )

    sales["revenue"] = sales["units_sold"] * sales["price"]
    sales["margin_proxy"] = sales["revenue"] - (sales["units_sold"] * sales["cost"])

    return sales

# 5. Clean Inventory Data
def clean_inventory_data(inventory):
    inventory = standardize_keys(inventory)
    inventory = inventory.sort_values(["store_id", "sku_id", "date"])

    inventory["on_hand_close"] = inventory["on_hand_close"].clip(lower=0)

    inventory["on_hand_close"] = inventory.groupby(
        ["store_id", "sku_id"]
    )["on_hand_close"].ffill()

    inventory["stockout_flag"] = (inventory["on_hand_close"] == 0).astype(int)

    return inventory

# 6. Lead Time Calculation (Purchase Orders)
def compute_lead_time(purchase_orders):
    purchase_orders = standardize_keys(purchase_orders)

    purchase_orders["lead_time_days"] = (
        purchase_orders["expected_receipt_date"] - purchase_orders["order_date"]
    ).dt.days

    lead_time = (
        purchase_orders
        .groupby("sku_id")["lead_time_days"]
        .median()
        .reset_index()
    )

    return lead_time

# 7. Build Fact Tables
# Fact Sales
def build_fact_sales(sales, calendar):
    calendar = calendar[["date", "promo_flag", "holiday_flag", "day_of_week"]]

    fact_sales = sales.merge(calendar, on="date", how="left")
    return fact_sales

# Fact Inventory
def build_fact_inventory(inventory, sales):
    avg_demand = (
        sales.groupby(["store_id", "sku_id"])["units_sold"]
        .rolling(28)
        .mean()
        .reset_index(level=[0,1], drop=True)
    )

    inventory = inventory.copy()
    inventory["avg_daily_demand_4w"] = avg_demand
    inventory["days_of_cover"] = inventory["on_hand_close"] / inventory["avg_daily_demand_4w"]

    return inventory

# 8. Replenishment Inputs (Core Business Logic)
def build_replenishment_inputs(sales, lead_time):
    demand_stats = (
        sales.groupby(["store_id", "sku_id"])["units_sold"]
        .agg(
            avg_daily_demand="mean",
            demand_std_dev="std"
        )
        .reset_index()
    )

    df = demand_stats.merge(lead_time, on="sku_id", how="left")

    SERVICE_LEVEL_Z = 1.65  # ~95% service level

    df["safety_stock"] = (
        SERVICE_LEVEL_Z *
        df["demand_std_dev"] *
        np.sqrt(df["lead_time_days"])
    )

    df["reorder_point"] = (
        df["avg_daily_demand"] * df["lead_time_days"]
        + df["safety_stock"]
    )

    df["recommended_order_qty"] = df["avg_daily_demand"] * 21  # 3-week cover

    return df

# 9. Orchestrator (Main Runner)
def run_etl(raw_data_dir, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sales, inventory, stores, calendar, purchase_orders, products = load_raw_data(raw_data_dir)

    sales_clean = clean_sales_data(sales, products)
    inventory_clean = clean_inventory_data(inventory)

    lead_time = compute_lead_time(purchase_orders)

    fact_sales = build_fact_sales(sales_clean, calendar)
    fact_inventory = build_fact_inventory(inventory_clean, sales_clean)

    replenishment_inputs = build_replenishment_inputs(sales_clean, lead_time)

    fact_sales.to_csv(output_dir / "fact_sales_store_sku_daily.csv", index=False)
    fact_inventory.to_csv(output_dir / "fact_inventory_store_sku_daily.csv", index=False)
    replenishment_inputs.to_csv(output_dir / "replenishment_inputs_store_sku.csv", index=False)


# Execute the pipeline
if __name__ == "__main__":
    raw_data_path = "C:/Tej/BITSoM/Projects/Capstone/data/Retail Demand Forecasting & Inventory Replenishment Planner"
    output_path = "C:/Tej/BITSoM/Projects/Capstone/output"
    
    print("Starting ETL pipeline...")
    run_etl(raw_data_path, output_path)
    print("ETL pipeline completed successfully!")
