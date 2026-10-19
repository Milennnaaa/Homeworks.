"""Steps 5-7: predict the diffusion of Oura Ring 4 (TIME Best Inventions 2025).

- p and q come from the look-alike (Fitbit, NLS fit).
- M (global market potential) comes from a Fermi estimate (data/fermi_inputs.csv).
- t = 1 is 2025, the first full year Oura Ring 4 was on sale (launched Oct 2024).

Two scenarios:
  A. Pure look-alike: p and q both from Fitbit.
  B. Calibrated (main forecast): q from Fitbit, p set so that 2025 adopters
     match the ~3.0M rings Oura reported selling in 2025.
Plus a sensitivity check on M.
Outputs: data/oura_forecast.csv, data/oura_sensitivity.csv, img/oura_*.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from helper_functions import adopters_by_period, bass_F, calibrate_p, peak_time

START_YEAR = 2025
N_YEARS = 12                 # 2025-2036
ADOPTERS_2025 = 3.0          # million rings sold in 2025 (Fierce Healthcare)

# ---- look-alike parameters ----
par = pd.read_csv("data/lookalike_parameters.csv").set_index("method")
p_fit, q_fit = par.loc["NLS", "p"], par.loc["NLS", "q"]

# ---- Fermi estimate of M ----
f = pd.read_csv("data/fermi_inputs.csv").set_index("input")["value"]
pop_hi = f["Population of high-income countries (2025)"]
wear_share = f["Share of adults who regularly wear a smartwatch or fitness tracker"]
ring_share = f["Share of wearable users who would buy a smart ring"]
oura_share = f["Oura share of smart ring market"]

wearable_users = pop_hi * wear_share
ring_market = wearable_users * ring_share
M = ring_market * oura_share / 1e6          # million people
print(f"Fermi: {pop_hi/1e6:.0f}M x {wear_share} = {wearable_users/1e6:.0f}M wearable "
      f"users; x {ring_share} = {ring_market/1e6:.1f}M ring buyers; "
      f"x {oura_share} Oura share = M = {M:.1f}M")

years = np.arange(START_YEAR, START_YEAR + N_YEARS)
k = np.arange(1, N_YEARS + 1)

p_cal = calibrate_p(ADOPTERS_2025, M, q_fit)
scen = {
    "A_lookalike": (p_fit, q_fit),
    "B_calibrated": (p_cal, q_fit),
}

out = pd.DataFrame({"year": years, "t": k})
for name, (p, q) in scen.items():
    new = adopters_by_period(k, M, p, q)
    out[f"{name}_new_mln"] = new
    out[f"{name}_cum_mln"] = np.cumsum(new)
    out[f"{name}_cum_share_of_M"] = bass_F(k, p, q)
    print(f"{name}: p={p:.4f}, q={q:.4f}, peak t*={peak_time(p, q):.2f}, "
          f"year with most new adopters = {years[np.argmax(new)]}")
out.round(3).to_csv("data/oura_forecast.csv", index=False)
print(out.round(2).to_string(index=False))

summary = pd.DataFrame([
    {"scenario": n, "p": p, "q": q, "M_mln": M, "peak_t_star": peak_time(p, q),
     "peak_year": years[np.argmax(out[f"{n}_new_mln"])],
     "peak_adopters_mln": out[f"{n}_new_mln"].max()}
    for n, (p, q) in scen.items()])
summary.to_csv("data/oura_scenarios.csv", index=False)

# ---- sensitivity of the main scenario to the ring-share assumption ----
sens_rows = []
for share in [0.05, 0.10, 0.15]:
    M_s = pop_hi * wear_share * share * oura_share / 1e6
    p_s = calibrate_p(ADOPTERS_2025, M_s, q_fit)
    new = adopters_by_period(k, M_s, p_s, q_fit)
    sens_rows.append({
        "ring_share": share, "M_mln": M_s, "p": p_s,
        "peak_year": years[np.argmax(new)],
        "adopters_2026_mln": new[1], "cum_2030_mln": new[:6].sum(),
        "cum_2036_mln": new.sum(),
    })
sens = pd.DataFrame(sens_rows)
sens.round(3).to_csv("data/oura_sensitivity.csv", index=False)
print(sens.round(3).to_string(index=False))

# ---- plots ----
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(7, 4))
w = 0.38
ax.bar(years - w / 2, out["B_calibrated_new_mln"], w, color="#c0392b",
       label="B: calibrated (main)")
ax.bar(years + w / 2, out["A_lookalike_new_mln"], w, color="#9fb7d1",
       label="A: pure look-alike")
ax.scatter([2025], [ADOPTERS_2025], color="black", zorder=5,
           label="Reported 2025 sales (~3.0M)")
ax.set_title(f"Oura Ring 4: predicted new adopters per year (M = {M:.1f}M)")
ax.set_ylabel("Million new adopters")
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("img/oura_new_adopters.png", dpi=160)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(years, out["B_calibrated_cum_mln"], "o-", color="#c0392b",
        label="B: calibrated (main)")
ax.plot(years, out["A_lookalike_cum_mln"], "s--", color="#2c3e50",
        label="A: pure look-alike")
ax.axhline(M, color="grey", lw=0.8, ls=":")
ax.text(years[0], M * 1.02, f"Market potential M = {M:.1f}M", color="grey")
ax.set_title("Oura Ring 4: predicted cumulative adopters")
ax.set_ylabel("Million adopters")
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45)
ax.legend(frameon=False, loc="center right")
fig.tight_layout()
fig.savefig("img/oura_cumulative.png", dpi=160)
print("saved plots")
