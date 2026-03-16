# Fannie Mae 30-Year TBA Current Coupon Rate Analysis

This project contains analysis for **Homework Assignment #2 (Problems 4 and 5)**, focused on mortgage spread behavior since 2000.

## Project Scope

- **Problem 4:** Spread between 30-year PMMS and 10-year Treasury yield
- **Problem 5:** Spread between 30-year PMMS and Fannie Mae 30-year TBA current coupon (CC30 proxy when direct data is unavailable)
- Weekly data alignment is set to **Wednesday** for consistency
- Spreads are calculated in **basis points**

## Repository Contents

- `Mortgage_Spread_Analysis.ipynb` – notebook workflow
- `mortgage_spread_analysis.py` – script version of the full analysis
- `pmms_treasury_spread.csv` – Problem 4 spread output
- `primary_secondary_spread.csv` – Problem 5 spread output
- `create_word_doc.py` – helper script for Problems 1–3 write-up template
- `HOMEWORK_GUIDE.md` and `instruction.txt` – assignment instructions

## Data Sources

- PMMS 30-year fixed mortgage rate (`MORTGAGE30US`) via FRED
- 10-year Treasury yield (`DGS10`) via FRED
- CC30: Bloomberg is preferred; script falls back to a proxy when direct series is unavailable

## Environment Setup

Install Python dependencies:

```bash
pip install pandas numpy matplotlib pandas-datareader scikit-learn
```

Optional package:

```bash
pip install fredapi
```

## How to Run

### Option 1: Run script

```bash
python mortgage_spread_analysis.py
```

### Option 2: Run notebook

Open `Mortgage_Spread_Analysis.ipynb` and run all cells in order.

## Outputs Generated

When the script completes, it produces:

- `pmms_treasury_spread.csv`
- `primary_secondary_spread.csv`
- `pmms_treasury_spread_chart.png`
- `primary_secondary_spread_chart.png`
- `rates_comparison.png`
- `regression_analysis.png`

## Methodology Summary

1. Download PMMS and Treasury data from FRED (daily/weekly source series)
2. Resample both to weekly `W-WED`
3. Compute spread:
   - `PMMS_Treasury_Spread = (PMMS_30Y - Treasury_10Y) * 100`
   - `PSS30 = (PMMS_30Y - CC30) * 100`
4. Export tables and charts
5. Run linear and polynomial regressions (degree 2 and 3) for PSS30 vs CC30

## Important Limitation

The script may use a **CC30 proxy** (`PMMS - 0.50`) if direct current coupon data is not available from configured sources. For assignment-grade accuracy, replace proxy input with Bloomberg CC30 history (e.g., FNMA 30Y TBA current coupon series).

## Notes

- The script suppresses non-critical warnings for cleaner output
- If `pandas-datareader` or `scikit-learn` is missing, the script prints install guidance
- Dates run from `2000-01-01` to current date
