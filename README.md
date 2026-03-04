# Retail Demand Forecasting & Inventory Replenishment Planner

## Project Overview & North Star
This project aims to develop a robust forecasting and inventory planning solution for a retail business. The north star is to accurately predict store–SKU demand, identify inventory risks, and recommend replenishment actions that minimize stockouts and overstock while supporting business objectives.

## Forecasting Methods Used
1. Moving Average (7-day rolling)
2. Seasonal Naive (week-over-week)
3. Linear Regression with trend, promotional flags, holiday indicators, and weekday dummies

## How to Run ETL End-to-End
1. Execute `etl/etl_pipeline.py` from the project root. It ingests raw source files and produces curated outputs under `/data`.
2. Ensure Python environment is activated and required packages installed (`pandas`, etc.).

## Curated Outputs Generated
The ETL produces the following generated datasets in `/data`:
- `fact_sales_store_sku_daily.csv`
- `fact_inventory_store_sku_daily.csv`
- `replenishment_inputs_store_sku.csv`

These files are cleaned and feature-enhanced for downstream analysis.

## Dashboard Tool & Access
A dashboard is built using Tableau ( `.twbx` or `.twb` format ), Power BI (`.pbix`), or Excel (`.xlsx`).

- Open the dashboard file in the corresponding application to explore: sales trends, inventory risk segmentation, and forecast performance.
- Screenshots or PDF exports accompany the dashboard in `/dashboard`.

---

## Repository Structure
```
README.md
/data/                    (generated only)
    fact_sales_store_sku_daily.csv
    fact_inventory_store_sku_daily.csv
    replenishment_inputs_store_sku.csv
/etl/
    etl_pipeline.py
/analysis/
    analysis.ipynb  (or analysis.py)
/dashboard/
    *.twbx | *.twb | *.pbix | *.xlsx
    screenshots/    (PNG/PDF exports)
/final_story/
    final_deck.pdf  (or final_memo.pdf)
```

## Analysis Folder
Contains Jupyter notebook or Python script performing EDA, model training, evaluation, and inventory risk calculations.

## Dashboard Folder
Holds the dashboard workbook and any exported images or PDFs for sharing insights.

## Final Story Folder
Includes the final presentation deck or memo summarizing findings and recommendations.

---
## Name - Tej Narayan Yadav
## Roll No - Bitsom_ba_25071687 