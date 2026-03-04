Notebook Flow

Files Loaded: fact_sales_store_sku_daily.csv, fact_inventory_store_sku_daily.csv, replenishment_inputs_store_sku.csv — loaded from project root (Capstone).
Setup / Imports: pandas, numpy, matplotlib, LinearRegression from scikit-learn; environment verification prints sys.executable.
Data Preparation:
Ensure weekday exists (derived from date if missing).
Ensure promo_flag and holiday_flag exist (default 0 if absent).
EDA (Demand Understanding):
Weekly seasonality: fact_sales.groupby("weekday")["units_sold"].mean().
Promo effect: fact_sales.groupby("promo_flag")["units_sold"].mean().
Top SKUs by revenue and demand volatility calculations.
Select Single Store–SKU: pick first store_id and sku_id and build sample sorted by date.
Baselines:
7‑day moving average (ma_7).
Seasonal naive (lag-7) (seasonal_naive).
Compute MAPE for each baseline on last 28 days.
Regression Model (Baseline ML):
Feature engineering: trend (index), weekday dummies, promo_flag, holiday_flag.
Train/test split: last 28 days as test.
Fit LinearRegression on train features → predict on test.
Evaluate MAPE (with guard added later to avoid divide-by-zero).
Utility Function: evaluate_store_sku(store, sku, ...)
Runs entire pipeline for one store–sku, computes MA, seasonal and regression forecasts, returns MAPEs and test dataframe with predictions.
Contains improvements added: dummy column names cast to strings; zero-actual handling; clipping negative predictions to 0.
Inventory Risk Segmentation:
Build latest_inventory per (store_id,sku_id) from fact_inventory.
Compute avg_daily_demand from fact_sales.
Merge into risk_df; derive on_hand_units, lead_time_days (default 7), days_of_cover, reorder_point.
Compute demand_during_lt and segment into Stockout Risk, Overstock Risk, Healthy.
Create reorder_flag and other simulation fields.
Impact Estimation:
Build lost_sales_proxy in fact_inventory using stockout_flag and avg_daily_demand_4w.
Sum last 30 days to estimate lost sales.
Diagnostics & Plots:
Example forecast comparison plot (actual, MA, seasonal, regression).
Performance-sample histogram (sampled store–sku pairs) added but filtered to skip zero-only test windows.
Assumptions & Issues Observed

Working directory sensitivity — fixed by explicitly setting project root.
Many test windows contain zeros in units_sold (often due to stockouts) → MAPE becomes NaN/inf. Dataset includes true_demand_units and stockout_censored_units.
Regression produced negative forecasts (linear model). Code clips negatives to 0 — quick fix but masks bias.
Some columns duplicated (e.g., promo_flag_x, promo_flag_y) — merged/curated data may need cleaning.
Performance summary initially empty because zero-only test windows were filtered.
Suggested Next Steps

Swap modeling target from units_sold to true_demand_units (if it represents de‑censored demand) to avoid censored-zero bias.
Use a count/positive model (e.g., PoissonRegressor or tree models like LightGBM/XGBoost with non-negative constraints) instead of plain LinearRegression.
Add features: lags (1,7,14), rolling means, price, promo indicators, category embeddings, holiday flags, store-level seasonality.
Use robust metrics: MASE or RMSSE and compute MAPE only where actual>0 (or use SMAPE).
Batch evaluation: filter store–sku to minimum nonzero-days or minimum average demand before running metrics.
Data hygiene: deduplicate columns, standardize column names, and confirm true_demand_units semantics.
Optional: persist risk_df and model outputs to output as CSV for downstream dashboards.