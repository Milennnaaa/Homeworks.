# Bass Model Homework – Oura Ring 4

DS 223 Marketing Analytics (AUA) · Milena Margaryan

Innovation from TIME's Best Inventions 2025: **Oura Ring 4**
<https://time.com/collections/best-inventions-2025/7318554/oura-ring-4/>

Look-alike innovation: **Fitbit fitness trackers** (devices sold 2011–2019, from Fitbit's SEC filings).

You can find the full report in [`report/report.pdf`](report/report.pdf). The Markdown version is [`report/report_source.md`](report/report_source.md).

## Main results

| | p | q | M |
|---|---|---|---|
| Fitbit (look-alike, NLS fit, R² = 0.82) | 0.0087 | 0.670 | 122.4 million |
| Oura Ring 4 (main forecast, global) | 0.104 (calibrated on 2025 sales) | 0.670 (from Fitbit) | 22.1 million (Fermi estimate) |

My forecast is that Oura Ring 4 adoption peaks in **2027 with about 4.9 million new adopters**, and reaches about 20.6 million total adopters by 2030.

## Project structure

```
├── README.md
├── requirements.txt
├── helper_functions.py        # Bass formulas: F(t), f(t), adopters per period, NLS and OLS fitting, peak time
├── estimate_lookalike.py      # Steps 3–4: estimates p, q, M on the Fitbit data, makes Fitbit plots
├── forecast_innovation.py     # Steps 5–7: Fermi estimate of M, Oura Ring 4 forecast, scenarios, sensitivity, plots
├── data/
│   ├── fitbit_devices_sold.csv     # input: Fitbit devices sold per year 2011–2019, with sources
│   ├── oura_reference_points.csv   # input: reported Oura / smart ring sales numbers, with sources
│   ├── fermi_inputs.csv            # input: numbers used for the market potential (Fermi) estimate
│   ├── lookalike_parameters.csv    # output: p, q, M for Fitbit (NLS and OLS)
│   ├── fitbit_fitted.csv           # output: actual vs fitted Fitbit sales
│   ├── oura_forecast.csv           # output: Oura Ring 4 new and cumulative adopters per year 2025–2036
│   ├── oura_scenarios.csv          # output: parameters and peak for scenarios A and B
│   └── oura_sensitivity.csv        # output: forecast with different market potential assumptions
├── img/
│   ├── fitbit_fit.png              # Fitbit devices sold vs Bass fit (NLS and OLS)
│   ├── fitbit_cumulative.png       # Fitbit cumulative actual vs Bass
│   ├── oura_new_adopters.png       # predicted new Oura Ring 4 adopters per year
│   └── oura_cumulative.png         # predicted cumulative Oura Ring 4 adopters
├── report/
│   ├── report_source.md            # report source (Markdown)
│   └── report.pdf                  # final report
└── references/
    └── references.md               # full reference list with links
```

## How to run

Install the packages and run the two scripts in this order:

```bash
pip install -r requirements.txt
python estimate_lookalike.py      # writes data/lookalike_parameters.csv and Fitbit plots
python forecast_innovation.py     # writes the Oura forecast tables and plots
```

If you want to rebuild the PDF, you need pandoc and xelatex:

```bash
cd report
pandoc report_source.md -o report.pdf --pdf-engine=xelatex -V fontfamily=fontspec -V mainfont="DejaVu Serif"
```

## Method in short

First I fitted the Bass model `a(t) = M·f(t)` to Fitbit's yearly sales using non-linear least squares (like `nls()` in R), and compared it with Bass's original OLS regression. Then I took q from Fitbit (and also p, for Scenario A). For Oura's market potential M, I made a Fermi estimate: high-income population × people who use wearables × people who would buy a ring × Oura's market share. In Scenario B, my main one, I chose p so that the model matches the ~3 million rings Oura sold in 2025. New adopters per year are `M·[F(t) − F(t−1)]`, with t = 1 being 2025.
