# scripts/02_data_transformation.py

import pandas as pd
import numpy as np # <--- ADD THIS LINE
import os

# Define file paths
CLEANED_DATA_PATH = os.path.join("data", "processed", "cleaned_ai_jobs_data.csv")
TRANSFORMED_DATA_PATH = os.path.join("data", "processed", "transformed_ai_jobs_data.csv")

# Placeholder exchange rates to USD (Update with more accurate/current rates)
# These are purely illustrative. In a real scenario, use an API or a reliable source.
EXCHANGE_RATES_TO_USD = {
    'usd': 1.0,
    'eur': 1.08, # Example rate
    'gbp': 1.27, # Example rate
    'inr': 0.012, # Example rate
    'cad': 0.73, # Example rate
    'aud': 0.66, # Example rate
    'sgd': 0.74, # Example rate
    'jpy': 0.0067, # Example rate
    # Add other currencies present in your dataset
    'unknown': np.nan # Handle cases where currency is unknown or not in this dict
}

def transform_data(df):
    """
    Transforms cleaned data for analysis and Power BI.
    - Converts salaries to a common currency (USD).
    - Extracts primary skill (example).
    - Creates salary bins (example).
    """
    print("Starting data transformation...")
    df_transformed = df.copy()

    # 1. Currency Conversion
    if 'salary' in df_transformed.columns and 'currency' in df_transformed.columns:
        print("\nConverting salaries to USD...")
        # Ensure currency column is lowercase to match keys in EXCHANGE_RATES_TO_USD
        df_transformed['currency'] = df_transformed['currency'].astype(str).str.lower()
        
        # Map currency to exchange rate
        df_transformed['exchange_rate_to_usd'] = df_transformed['currency'].map(EXCHANGE_RATES_TO_USD)
        
        # Handle currencies not in our dict (e.g., fill with NaN or a default)
        # For now, if a currency is not found, its exchange rate will be NaN, and salary_usd will be NaN
        unknown_currencies = df_transformed[df_transformed['exchange_rate_to_usd'].isnull()]['currency'].unique()
        if len(unknown_currencies) > 0:
            # Filter out 'nan' string if it appears due to astype(str) on actual NaN values
            unknown_currencies_to_report = [curr for curr in unknown_currencies if curr != 'nan']
            if unknown_currencies_to_report:
                print(f"Warning: The following currencies were not found in the exchange rate dictionary and will result in NaN salaries: {unknown_currencies_to_report}")

        df_transformed['salary_usd'] = df_transformed['salary'] * df_transformed['exchange_rate_to_usd']
        
        print(f"Salaries converted. Check 'salary_usd'. NaN values may exist if currency was unknown or salary was NaN.")
    else:
        print("Warning: 'salary' or 'currency' column not found. Skipping currency conversion.")


    # 2. Feature Engineering Example: Extract Primary Skill
    # Assumes 'skills required' is a comma-separated string.
    if 'skills required' in df_transformed.columns:
        print("\nExtracting primary skill...")
        df_transformed['primary_skill'] = df_transformed['skills required'].astype(str).apply(
            lambda x: x.split(',')[0].strip() if pd.notnull(x) and x != 'not specified' and x != 'nan' and ',' in x else x
        )
        # If no comma, take the whole string as primary skill (if not 'not specified' or 'nan')
        df_transformed['primary_skill'] = df_transformed.apply(
            lambda row: row['skills required'] if pd.notnull(row['skills required']) and row['skills required'] not in ['not specified', 'nan'] and ',' not in str(row['skills required']) else row['primary_skill'],
            axis=1
        )
        # Clean up cases where primary_skill might still be 'nan' or 'not specified' from original single value
        df_transformed.loc[df_transformed['primary_skill'].isin(['nan', 'not specified']), 'primary_skill'] = 'not specified'
        print("Primary skill extracted into 'primary_skill' column.")

    # 3. Feature Engineering Example: Create Salary Bins (using salary_usd)
    if 'salary_usd' in df_transformed.columns:
        print("\nCreating salary bins...")
        # Ensure salary_usd is numeric before binning
        df_transformed['salary_usd'] = pd.to_numeric(df_transformed['salary_usd'], errors='coerce')
        
        bins = [0, 50000, 100000, 150000, 200000, np.inf]
        labels = ['<50k', '50k-100k', '100k-150k', '150k-200k', '>200k']
        df_transformed['salary_usd_bin'] = pd.cut(df_transformed['salary_usd'], bins=bins, labels=labels, right=False)
        print("Salary bins created in 'salary_usd_bin' column.")

    print("\nTransformed data info:")
    df_transformed.info()
    
    print("\nData transformation finished.")
    return df_transformed

def main():
    print(f"Loading cleaned data from: {CLEANED_DATA_PATH}")
    try:
        df_cleaned = pd.read_csv(CLEANED_DATA_PATH)
    except FileNotFoundError:
        print(f"Error: Cleaned data file not found at {CLEANED_DATA_PATH}. Please run the cleaning script first.")
        return

    df_transformed = transform_data(df_cleaned)
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(TRANSFORMED_DATA_PATH), exist_ok=True)

    print(f"\nSaving transformed data to: {TRANSFORMED_DATA_PATH}")
    df_transformed.to_csv(TRANSFORMED_DATA_PATH, index=False)
    print("Transformed data saved successfully.")

if __name__ == "__main__":
    main()