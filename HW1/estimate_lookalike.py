"""Step 3-4: estimate Bass parameters (p, q, M) for the look-alike innovation.

Look-alike: Fitbit connected fitness trackers, devices sold per year 2011-2019
(SEC filings). Two estimation methods from the lecture are used and compared.
Outputs: data/lookalike_parameters.csv, data/fitbit_fitted.csv, img/fitbit_*.png
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from helper_functions import (bass_a, bass_F, fit_nls, fit_ols, peak_time,
                              r_squared)

df = pd.read_csv("data/fitbit_devices_sold.csv")
sales = df["devices_sold_mln"].values
t = np.arange(1, len(sales) + 1)

# Method 1: non-linear least squares (like nls() in R)
nls_par, nls_se = fit_nls(sales)
# Method 2: Bass's original linear regression
ols_par, betas = fit_ols(sales)

rows = []
for name, par in [("NLS", nls_par), ("OLS (Bass 1969)", ols_par)]:
    pred = bass_a(t, par["M"], par["p"], par["q"])
    rows.append({
        "method": name,
        "p": par["p"], "q": par["q"], "M_mln": par["M"],
        "q_over_p": par["q"] / par["p"],
        "peak_t": peak_time(par["p"], par["q"]),
        "peak_year": df["year"].iloc[0] - 1 + peak_time(par["p"], par["q"]),
        "R2": r_squared(sales, pred),
    })
params = pd.DataFrame(rows)
params.to_csv("data/lookalike_parameters.csv", index=False)

print("Standard errors (NLS):", {k: round(v, 4) for k, v in nls_se.items()})
print("OLS betas b0, b1, b2:", [round(b, 5) for b in betas])
print(params.round(4).to_string(index=False))

df["fitted_nls_mln"] = bass_a(t, nls_par["M"], nls_par["p"], nls_par["q"])
df["fitted_ols_mln"] = bass_a(t, ols_par["M"], ols_par["p"], ols_par["q"])
df["cum_actual_mln"] = df["devices_sold_mln"].cumsum()
df["cum_fitted_nls_mln"] = nls_par["M"] * bass_F(t, nls_par["p"], nls_par["q"])
df.round(3).to_csv("data/fitbit_fitted.csv", index=False)

# ---- plots ----
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(df["year"], sales, color="#9fb7d1", label="Actual devices sold")
ax.plot(df["year"], df["fitted_nls_mln"], "o-", color="#c0392b",
        label="Bass fit (NLS)")
ax.plot(df["year"], df["fitted_ols_mln"], "s--", color="#2c3e50",
        label="Bass fit (OLS)", alpha=0.8)
ax.set_title("Fitbit devices sold per year vs. Bass model fit")
ax.set_ylabel("Million devices")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("img/fitbit_fit.png", dpi=160)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(df["year"], df["cum_actual_mln"], "o-", color="#2c3e50",
        label="Actual cumulative")
ax.plot(df["year"], df["cum_fitted_nls_mln"], "--", color="#c0392b",
        label="Bass cumulative (NLS)")
ax.set_title("Fitbit cumulative devices sold")
ax.set_ylabel("Million devices")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("img/fitbit_cumulative.png", dpi=160)
print("saved plots")
