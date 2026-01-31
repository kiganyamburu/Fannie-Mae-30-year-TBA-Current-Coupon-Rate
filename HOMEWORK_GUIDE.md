# Homework Assignment #2 - Completion Guide

## Overview

This document provides guidance for completing all 5 problems in the homework assignment.

---

## Problem 1 (0.25 points) - Urban Institute Chart Book Review

**Task**: Review the December 2025 Chart Book published by the Urban Institute

### Where to Find:

- URL: https://www.urban.org/research/publication/housing-finance-policy-center-chartbook

### What to Submit:

**Question 2-1**: List the top 5 new things you learned from the chart book

- Look for: Housing market trends, mortgage performance metrics, GSE market share, delinquency rates, etc.

**Question 2-2**: State 3 things you do not understand

- Be specific about charts, metrics, or concepts that need clarification

---

## Problem 2 (0.25 points) - Recursion Glossary Review

**Task**: Review Fannie Mae loan level terms from Recursion Glossary

### What to Do:

- Access Recursion's data dictionary/glossary
- Review loan-level variable definitions
- List terms that are confusing or need clarification

### Common Loan-Level Terms to Review:

- LTV (Loan-to-Value)
- CLTV (Combined Loan-to-Value)
- DTI (Debt-to-Income)
- FICO Score
- UPB (Unpaid Principal Balance)
- Occupancy Type
- Property Type
- Loan Purpose (Purchase, Refinance, Cash-out Refinance)
- Documentation Type
- Prepayment Speed (CPR, SMM)

---

## Problem 3 (0.5 points) - Agency Market Size Analysis

**Task**: Use Recursion's Cohort Analyzer for Jan-Dec 2025 data

### Question 3-1: Outstanding Balances by Agency

Create a table showing monthly outstanding balances for:

- Ginnie Mae (GNM)
- Fannie Mae (FNMA)
- Freddie Mac (FHLMC)

### Question 3-2: Issuance Volumes by Agency

Create a table showing monthly issuance volumes for each agency in 2025

### Definitions:

- **GSE**: Government-Sponsored Enterprises (Fannie Mae + Freddie Mac)
- **GNM**: Ginnie Mae (Government National Mortgage Association)
- **Agency**: All three - Fannie Mae, Freddie Mac, and Ginnie Mae

---

## Problem 4 (0.5 points) - PMMS vs Treasury Spread ✅ COMPLETED

**Location**: `Mortgage_Spread_Analysis.ipynb` and `mortgage_spread_analysis.py`

### 4-1: Download Data ✅

- PMMS data downloaded from FRED (MORTGAGE30US series)
- 10-Year Treasury data downloaded from FRED (DGS10 series)

### 4-2: Create Spread History ✅

- Output file: `pmms_treasury_spread.csv`
- Chart file: `pmms_treasury_spread_chart.png`
- Weekly Wednesday-aligned data since 2000
- Spread calculated in basis points

### 4-3: Conclusions ✅

See the notebook for detailed conclusions about:

- Average spread levels (typically 150-200 bps)
- Spread widening during crises
- Factors affecting the spread

---

## Problem 5 (0.5 points) - PMMS vs CC30 Spread ✅ COMPLETED

**Location**: `Mortgage_Spread_Analysis.ipynb` and `mortgage_spread_analysis.py`

### 5-1: Download CC30 Data ✅

- Note: True Fannie Mae 30Y TBA Current Coupon requires Bloomberg access
- Proxy data created from Treasury + typical MBS spread
- **For full accuracy**: Replace with Bloomberg data (MTGEFNCL Index)

### 5-2: Create PSS30 History ✅

- Output file: `primary_secondary_spread.csv`
- Chart file: `primary_secondary_spread_chart.png`
- Weekly data in basis points

### 5-3: Regression Analysis ✅

- Linear regression results
- Polynomial (Degree 2 and 3) regression results
- Regression plots: `regression_analysis.png`
- Residual plots: `residual_analysis.png`
- Detailed conclusions and recommendations in notebook

---

## Files Generated

| File                                 | Description                                         |
| ------------------------------------ | --------------------------------------------------- |
| `Mortgage_Spread_Analysis.ipynb`     | Main Jupyter notebook with all analysis             |
| `mortgage_spread_analysis.py`        | Python script version                               |
| `pmms_treasury_spread.csv`           | Problem 4 data (will be created when notebook runs) |
| `pmms_treasury_spread_chart.png`     | Problem 4 chart                                     |
| `primary_secondary_spread.csv`       | Problem 5 data                                      |
| `primary_secondary_spread_chart.png` | Problem 5 chart                                     |
| `regression_analysis.png`            | Regression scatter plots                            |
| `residual_analysis.png`              | Model diagnostic plots                              |

---

## How to Run the Analysis

1. Open `Mortgage_Spread_Analysis.ipynb` in VS Code or Jupyter
2. Run all cells in order
3. The notebook will:
   - Install required packages if needed
   - Download data from FRED
   - Generate all tables and charts
   - Save output files to the project folder

### Required Python Packages:

- pandas
- numpy
- matplotlib
- pandas-datareader
- scikit-learn

---

## Important Notes

### For Problem 5 - Accurate CC30 Data:

The notebook uses a proxy for the Fannie Mae 30-Year TBA Current Coupon Rate because this data typically requires Bloomberg Terminal access. If you have access to Bloomberg:

1. Download the FNMA 30Y TBA Current Coupon (Bloomberg: MTGEFNCL Index)
2. Save as CSV with columns: Date, CC30
3. Replace the proxy data in the notebook

### Weekly Alignment:

Per the assignment instructions, all data is aligned to Wednesday to ensure consistency between the weekly PMMS survey and daily Treasury/CC30 data.
Per the assignment instructions, all data is aligned to Wednesday to ensure consistency between the weekly PMMS survey and daily Treasury/CC30 data.
