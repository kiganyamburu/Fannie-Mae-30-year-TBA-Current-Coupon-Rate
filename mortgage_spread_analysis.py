"""
Mortgage Spread Analysis
========================
This script analyzes:
- Problem 4: Spread between 30-year Primary Mortgage Rate (PMMS) and 10-year Treasury Yield
- Problem 5: Spread between 30-year PMMS and Fannie Mae 30-year TBA Current Coupon Rate

Data Sources:
- Freddie Mac PMMS: https://www.freddiemac.com/pmms
- 10-Year Treasury: FRED API (Federal Reserve Economic Data)
- Fannie Mae 30-year TBA Current Coupon: FRED API or Bloomberg
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# Try to import optional packages
try:
    import pandas_datareader as pdr
    from pandas_datareader import data as web

    HAS_DATAREADER = True
except ImportError:
    HAS_DATAREADER = False
    print(
        "Note: pandas_datareader not installed. Install with: pip install pandas-datareader"
    )

try:
    from fredapi import Fred

    HAS_FREDAPI = True
except ImportError:
    HAS_FREDAPI = False
    print("Note: fredapi not installed. Install with: pip install fredapi")

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import r2_score, mean_squared_error

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Note: scikit-learn not installed. Install with: pip install scikit-learn")

# ============================================================================
# SECTION 1: Data Download Functions
# ============================================================================


def download_pmms_data():
    """
    Download Primary Mortgage Market Survey (PMMS) data from Freddie Mac.
    The 30-year fixed rate mortgage average is available on FRED as 'MORTGAGE30US'
    """
    print("Downloading PMMS 30-Year Fixed Rate Mortgage data...")

    if HAS_DATAREADER:
        try:
            # MORTGAGE30US is the 30-Year Fixed Rate Mortgage Average in the United States
            start_date = "2000-01-01"
            end_date = datetime.today().strftime("%Y-%m-%d")

            pmms = web.DataReader("MORTGAGE30US", "fred", start_date, end_date)
            pmms.columns = ["PMMS_30Y"]
            print(
                f"Downloaded {len(pmms)} PMMS records from {pmms.index.min()} to {pmms.index.max()}"
            )
            return pmms
        except Exception as e:
            print(f"Error downloading PMMS data: {e}")
            return None
    else:
        print(
            "pandas_datareader not available. Please install it or download data manually."
        )
        return None


def download_treasury_10y_data():
    """
    Download 10-Year Treasury Constant Maturity Rate from FRED.
    Series: DGS10 (Daily) or WGS10YR (Weekly)
    """
    print("Downloading 10-Year Treasury Rate data...")

    if HAS_DATAREADER:
        try:
            start_date = "2000-01-01"
            end_date = datetime.today().strftime("%Y-%m-%d")

            # DGS10 is the daily 10-Year Treasury Constant Maturity Rate
            treasury = web.DataReader("DGS10", "fred", start_date, end_date)
            treasury.columns = ["Treasury_10Y"]
            print(
                f"Downloaded {len(treasury)} Treasury records from {treasury.index.min()} to {treasury.index.max()}"
            )
            return treasury
        except Exception as e:
            print(f"Error downloading Treasury data: {e}")
            return None
    else:
        print("pandas_datareader not available.")
        return None


def download_fannie_mae_cc30_data():
    """
    Download Fannie Mae 30-Year Current Coupon Rate.
    Note: This data may require Bloomberg terminal access.
    Alternative: Use FRED series if available, or manual download.

    The Current Coupon rate represents the yield at which a newly issued
    TBA (To-Be-Announced) mortgage-backed security would trade at par.
    """
    print("Downloading Fannie Mae 30-Year TBA Current Coupon Rate data...")

    if HAS_DATAREADER:
        try:
            start_date = "2000-01-01"
            end_date = datetime.today().strftime("%Y-%m-%d")

            # Try multiple potential FRED series for current coupon
            # Note: Exact series may vary - these are common proxies
            possible_series = [
                "OBMMIFHA30YF",  # 30-Year FHA Mortgage Rate
                "OBMMIC30YF",  # 30-Year Conventional Mortgage Rate
            ]

            for series in possible_series:
                try:
                    cc30 = web.DataReader(series, "fred", start_date, end_date)
                    cc30.columns = ["CC30"]
                    print(
                        f"Downloaded {len(cc30)} Current Coupon records using series {series}"
                    )
                    return cc30
                except:
                    continue

            # If no FRED series available, create a proxy based on PMMS with adjustment
            print(
                "Direct CC30 data not available from FRED. Creating proxy from PMMS..."
            )
            print(
                "Note: For accurate analysis, please obtain Bloomberg data for FNMA 30Y TBA Current Coupon"
            )

            # Typical spread between PMMS and CC30 is around 25-50 bps historically
            pmms = download_pmms_data()
            if pmms is not None:
                cc30_proxy = pmms.copy()
                cc30_proxy.columns = ["CC30"]
                # Approximate CC30 as PMMS minus typical primary-secondary spread
                cc30_proxy["CC30"] = pmms["PMMS_30Y"] - 0.50  # Approximate adjustment
                print(
                    "Created CC30 proxy (PMMS - 50bps). Replace with actual Bloomberg data for accuracy."
                )
                return cc30_proxy
            return None

        except Exception as e:
            print(f"Error downloading CC30 data: {e}")
            return None
    else:
        print("pandas_datareader not available.")
        return None


# ============================================================================
# SECTION 2: Data Processing Functions
# ============================================================================


def align_to_weekly_wednesday(df, column_name):
    """
    Resample data to weekly frequency, aligned to Wednesday.
    """
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Resample to weekly, using Wednesday as the end of week
    weekly = df.resample("W-WED").last()
    weekly = weekly.dropna()

    return weekly


def calculate_spread(df1, df2, col1, col2, spread_name):
    """
    Calculate spread between two series in basis points.
    """
    # Merge on index
    merged = pd.merge(
        df1[[col1]], df2[[col2]], left_index=True, right_index=True, how="inner"
    )

    # Calculate spread in basis points (multiply by 100)
    merged[spread_name] = (merged[col1] - merged[col2]) * 100

    return merged


# ============================================================================
# SECTION 3: Visualization Functions
# ============================================================================


def plot_spread_history(df, spread_col, title, ylabel, filename):
    """
    Create a time series chart of spread history.
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(df.index, df[spread_col], "b-", linewidth=0.8, alpha=0.8)
    ax.axhline(
        y=df[spread_col].mean(),
        color="r",
        linestyle="--",
        label=f"Mean: {df[spread_col].mean():.1f} bps",
    )

    ax.fill_between(df.index, df[spread_col], alpha=0.3)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    # Add recession shading for context (approximate dates)
    recessions = [
        ("2001-03-01", "2001-11-01"),  # Dot-com recession
        ("2007-12-01", "2009-06-01"),  # Great Recession
        ("2020-02-01", "2020-04-01"),  # COVID-19 recession
    ]

    for start, end in recessions:
        try:
            start_date = pd.to_datetime(start)
            end_date = pd.to_datetime(end)
            if start_date >= df.index.min() and end_date <= df.index.max():
                ax.axvspan(
                    start_date, end_date, alpha=0.2, color="gray", label="Recession"
                )
        except:
            pass

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Chart saved as: {filename}")


def plot_rates_comparison(df, rate_cols, title, filename):
    """
    Plot multiple rates on the same chart for comparison.
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    colors = ["blue", "red", "green", "orange"]
    for i, col in enumerate(rate_cols):
        if col in df.columns:
            ax.plot(
                df.index,
                df[col],
                color=colors[i % len(colors)],
                linewidth=1,
                label=col,
                alpha=0.8,
            )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Rate (%)", fontsize=12)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Chart saved as: {filename}")


# ============================================================================
# SECTION 4: Regression Analysis Functions (Problem 5-3)
# ============================================================================


def run_regression_analysis(df, x_col, y_col):
    """
    Run linear and non-linear regressions of PSS30 on CC30.
    """
    if not HAS_SKLEARN:
        print("scikit-learn not available. Please install it for regression analysis.")
        return None

    # Remove any NaN values
    df_clean = df[[x_col, y_col]].dropna()

    X = df_clean[[x_col]].values
    y = df_clean[y_col].values

    results = {}

    # -------------------------
    # Linear Regression
    # -------------------------
    print("\n" + "=" * 60)
    print("LINEAR REGRESSION RESULTS")
    print("=" * 60)

    lr = LinearRegression()
    lr.fit(X, y)
    y_pred_linear = lr.predict(X)

    r2_linear = r2_score(y, y_pred_linear)
    rmse_linear = np.sqrt(mean_squared_error(y, y_pred_linear))

    print(f"Equation: PSS30 = {lr.intercept_:.4f} + {lr.coef_[0]:.4f} * CC30")
    print(f"R-squared: {r2_linear:.4f}")
    print(f"RMSE: {rmse_linear:.2f} basis points")

    results["linear"] = {
        "model": lr,
        "r2": r2_linear,
        "rmse": rmse_linear,
        "predictions": y_pred_linear,
        "intercept": lr.intercept_,
        "coefficient": lr.coef_[0],
    }

    # -------------------------
    # Polynomial Regression (Degree 2)
    # -------------------------
    print("\n" + "=" * 60)
    print("POLYNOMIAL REGRESSION (DEGREE 2) RESULTS")
    print("=" * 60)

    poly2 = PolynomialFeatures(degree=2)
    X_poly2 = poly2.fit_transform(X)
    lr_poly2 = LinearRegression()
    lr_poly2.fit(X_poly2, y)
    y_pred_poly2 = lr_poly2.predict(X_poly2)

    r2_poly2 = r2_score(y, y_pred_poly2)
    rmse_poly2 = np.sqrt(mean_squared_error(y, y_pred_poly2))

    print(
        f"Coefficients: {lr_poly2.intercept_:.4f}, {lr_poly2.coef_[1]:.4f}, {lr_poly2.coef_[2]:.4f}"
    )
    print(f"R-squared: {r2_poly2:.4f}")
    print(f"RMSE: {rmse_poly2:.2f} basis points")

    results["poly2"] = {
        "model": lr_poly2,
        "transformer": poly2,
        "r2": r2_poly2,
        "rmse": rmse_poly2,
        "predictions": y_pred_poly2,
    }

    # -------------------------
    # Polynomial Regression (Degree 3)
    # -------------------------
    print("\n" + "=" * 60)
    print("POLYNOMIAL REGRESSION (DEGREE 3) RESULTS")
    print("=" * 60)

    poly3 = PolynomialFeatures(degree=3)
    X_poly3 = poly3.fit_transform(X)
    lr_poly3 = LinearRegression()
    lr_poly3.fit(X_poly3, y)
    y_pred_poly3 = lr_poly3.predict(X_poly3)

    r2_poly3 = r2_score(y, y_pred_poly3)
    rmse_poly3 = np.sqrt(mean_squared_error(y, y_pred_poly3))

    print(f"R-squared: {r2_poly3:.4f}")
    print(f"RMSE: {rmse_poly3:.2f} basis points")

    results["poly3"] = {
        "model": lr_poly3,
        "transformer": poly3,
        "r2": r2_poly3,
        "rmse": rmse_poly3,
        "predictions": y_pred_poly3,
    }

    # -------------------------
    # Plot Regression Results
    # -------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Scatter plot with linear fit
    axes[0].scatter(X, y, alpha=0.3, s=10, label="Actual")
    sort_idx = np.argsort(X.flatten())
    axes[0].plot(
        X[sort_idx], y_pred_linear[sort_idx], "r-", linewidth=2, label="Linear Fit"
    )
    axes[0].set_xlabel("CC30 (%)")
    axes[0].set_ylabel("PSS30 (bps)")
    axes[0].set_title(f"Linear Regression\nR² = {r2_linear:.4f}")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Scatter plot with polynomial degree 2 fit
    axes[1].scatter(X, y, alpha=0.3, s=10, label="Actual")
    axes[1].plot(
        X[sort_idx], y_pred_poly2[sort_idx], "g-", linewidth=2, label="Poly2 Fit"
    )
    axes[1].set_xlabel("CC30 (%)")
    axes[1].set_ylabel("PSS30 (bps)")
    axes[1].set_title(f"Polynomial (Degree 2)\nR² = {r2_poly2:.4f}")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Scatter plot with polynomial degree 3 fit
    axes[2].scatter(X, y, alpha=0.3, s=10, label="Actual")
    axes[2].plot(
        X[sort_idx], y_pred_poly3[sort_idx], "m-", linewidth=2, label="Poly3 Fit"
    )
    axes[2].set_xlabel("CC30 (%)")
    axes[2].set_ylabel("PSS30 (bps)")
    axes[2].set_title(f"Polynomial (Degree 3)\nR² = {r2_poly3:.4f}")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("regression_analysis.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("\nRegression plots saved as: regression_analysis.png")

    return results


def print_conclusions():
    """
    Print conclusions and recommendations for the analysis.
    """
    conclusions = """
    ============================================================================
    CONCLUSIONS AND RECOMMENDATIONS
    ============================================================================
    
    PROBLEM 4: PMMS vs 10-Year Treasury Spread
    -------------------------------------------
    Key Observations:
    1. The spread between 30-year mortgage rates and 10-year Treasury rates 
       typically ranges from 150-300 basis points historically.
    
    2. Spread widening often occurs during:
       - Financial crises (2008-2009 saw spreads exceed 300 bps)
       - Periods of market uncertainty
       - Federal Reserve policy changes
    
    3. Spread compression typically occurs during:
       - Periods of economic stability
       - Strong housing market demand
       - Fed MBS purchase programs (QE)
    
    PROBLEM 5: Primary-Secondary Spread (PSS30) Analysis
    -----------------------------------------------------
    Key Observations:
    1. The primary-secondary spread represents the difference between what 
       consumers pay (PMMS) and the secondary market rate (CC30).
    
    2. This spread covers:
       - Origination costs and lender margins
       - Servicing rights value
       - Credit and prepayment risk premium
       - Pipeline hedging costs
    
    Regression Analysis Limitations:
    1. Historical relationships may not hold in different market regimes
    2. Omitted variable bias - many factors affect the spread beyond CC30
    3. Non-stationarity - spread dynamics change over time
    4. Structural breaks during crisis periods
    
    Recommendations to Improve Predictions:
    1. Include additional explanatory variables:
       - Mortgage application volume (MBA index)
       - Volatility (MOVE index or VIX)
       - Yield curve slope
       - Prepayment speeds (CPR)
    
    2. Use regime-switching models to capture different market states
    
    3. Apply time-series techniques (ARIMA, GARCH) for temporal patterns
    
    4. Consider machine learning approaches (Random Forest, XGBoost) 
       for non-linear relationships
    
    5. Use rolling window regressions to capture time-varying relationships
    
    6. Include lagged variables to capture delayed market reactions
    ============================================================================
    """
    print(conclusions)


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """
    Main function to run the complete analysis.
    """
    print("=" * 70)
    print("MORTGAGE SPREAD ANALYSIS")
    print("=" * 70)
    print(f"Analysis Date: {datetime.today().strftime('%Y-%m-%d')}")
    print("=" * 70)

    # -------------------------
    # Problem 4: PMMS vs Treasury Spread
    # -------------------------
    print("\n" + "=" * 70)
    print("PROBLEM 4: PMMS vs 10-Year Treasury Spread")
    print("=" * 70)

    # Download data
    pmms_data = download_pmms_data()
    treasury_data = download_treasury_10y_data()

    if pmms_data is not None and treasury_data is not None:
        # Align to weekly Wednesday
        pmms_weekly = align_to_weekly_wednesday(pmms_data, "PMMS_30Y")
        treasury_weekly = align_to_weekly_wednesday(treasury_data, "Treasury_10Y")

        # Calculate spread
        spread_df = calculate_spread(
            pmms_weekly,
            treasury_weekly,
            "PMMS_30Y",
            "Treasury_10Y",
            "PMMS_Treasury_Spread",
        )

        # Display summary statistics
        print("\n--- Spread Summary Statistics (basis points) ---")
        print(spread_df["PMMS_Treasury_Spread"].describe())

        # Save to CSV
        spread_df.to_csv("pmms_treasury_spread.csv")
        print("\nData saved to: pmms_treasury_spread.csv")

        # Create visualization
        plot_spread_history(
            spread_df,
            "PMMS_Treasury_Spread",
            "30-Year PMMS vs 10-Year Treasury Spread",
            "Spread (basis points)",
            "pmms_treasury_spread_chart.png",
        )

        # Plot rates comparison
        plot_rates_comparison(
            spread_df,
            ["PMMS_30Y", "Treasury_10Y"],
            "30-Year PMMS vs 10-Year Treasury Rate",
            "rates_comparison.png",
        )

        # Display recent data table
        print("\n--- Recent Weekly Data (Last 20 weeks) ---")
        print(spread_df.tail(20).to_string())

    # -------------------------
    # Problem 5: PMMS vs Fannie Mae CC30 Spread
    # -------------------------
    print("\n" + "=" * 70)
    print("PROBLEM 5: PMMS vs Fannie Mae 30-Year TBA Current Coupon Spread")
    print("=" * 70)

    cc30_data = download_fannie_mae_cc30_data()

    if pmms_data is not None and cc30_data is not None:
        # Align to weekly Wednesday
        cc30_weekly = align_to_weekly_wednesday(cc30_data, "CC30")

        # Calculate Primary-Secondary Spread (PSS30)
        pss30_df = calculate_spread(
            pmms_weekly, cc30_weekly, "PMMS_30Y", "CC30", "PSS30"
        )

        # Display summary statistics
        print("\n--- Primary-Secondary Spread Summary Statistics (basis points) ---")
        print(pss30_df["PSS30"].describe())

        # Save to CSV
        pss30_df.to_csv("primary_secondary_spread.csv")
        print("\nData saved to: primary_secondary_spread.csv")

        # Create visualization
        plot_spread_history(
            pss30_df,
            "PSS30",
            "Primary-Secondary Spread (PSS30): PMMS vs Fannie Mae CC30",
            "Spread (basis points)",
            "primary_secondary_spread_chart.png",
        )

        # Display recent data table
        print("\n--- Recent Weekly Data (Last 20 weeks) ---")
        print(pss30_df.tail(20).to_string())

        # -------------------------
        # Problem 5-3: Regression Analysis
        # -------------------------
        print("\n" + "=" * 70)
        print("PROBLEM 5-3: Regression Analysis of PSS30 on CC30")
        print("=" * 70)

        regression_results = run_regression_analysis(pss30_df, "CC30", "PSS30")

    # Print conclusions
    print_conclusions()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
