here's a concise diagnosis and suggested next steps based on the run & plots.

What I fixed so far

Data load path and cwd corrected so CSVs load reliably.
Derived weekday, defaulted promo_flag/holiday_flag.
Created risk_df from latest inventory + avg demand.
Fixed dummy column name types so sklearn accepts them.
Added an evaluate_store_sku() utility to compute MA, seasonal and regression forecasts and return test predictions.
Added guards so MAPE ignores zero actuals and clipped negative forecasts to 0 for plotting.
What the outputs show / current problems

Many test windows contain only zeros (or mostly zeros). That caused MAPE to be NaN or inf (division by zero). I added checks to skip/handle such series — which is why the sample performance run returned an empty table (we skipped series with zero-only test windows).
Regression initially produced negative forecasts (linear model output) — I clipped to 0 to avoid negative forecasts in plots. That can hide model bias; it's a quick fix, not a modeling solution.
The dataset contains columns true_demand_units and stockout_censored_units — the zeros in units_sold may be censored by stockouts. Evaluating against observed units_sold without correcting for censoring yields misleading metrics and many zero test windows.
Recommended next steps (pick one or more)

Use true_demand_units as the modeling target (if it represents de‑censored demand). This will remove artificial zeros due to stockouts and produce meaningful metrics.
Replace LinearRegression with a non‑negative/count model (e.g., sklearn.linear_model.PoissonRegressor) or a tree model (e.g., LightGBM) configured for non‑negative outputs.
Use robust metrics: MASE or RMSSE (scale‑independent) or exclude zero actuals as appropriate. If you must use percentage metrics, compute them only where actual>0.
For forecasting counts consider log1p transform on target with back‑transform and bias correction.
Expand features: include price, promo_flag, category encodings, recent lags, rolling means; that should improve regression quality.
When evaluating across many store–SKU pairs, filter to SKUs with sufficient historical volume (min nonzero days) before computing metrics.
Suggested immediate action (I can implement)

Swap the target to true_demand_units in evaluate_store_sku(), switch the regressor to PoissonRegressor (or LGBM), compute MASE plus MAPE (where applicable), and re-run the sample performance summary and plots.
Would you like me to implement the true_demand_units + PoissonRegressor change and re-run the performance sample now?
GPT-5 mini • 1x
