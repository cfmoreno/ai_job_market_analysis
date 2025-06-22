# scripts/01_data_cleaning.py

import pandas as pd
import numpy as np
import os

# Define file paths
RAW_DATA_PATH = os.path.join("data", "raw", "ai_job_dataset.csv")
CLEANED_DATA_PATH = os.path.join("data", "processed", "cleaned_ai_jobs_data.csv")

def clean_data(df):
    """
    Cleans the raw AI job market data.
    - Handles missing values.
    - Corrects data types.
    - Standardizes text fields.
    - Removes potential duplicates.
    """
    print("Starting data cleaning...")
    
    # Make a copy to avoid SettingWithCopyWarning
    df_cleaned = df.copy()

    # 1. Handle Missing Values
    # Example: For categorical, fill with 'Unknown' or mode. For numerical, fill with mean/median or drop.
    # Let's inspect missing values first (this would typically be informed by EDA)
    print("\nMissing values before cleaning:")
    print(df_cleaned.isnull().sum())

    # For 'Company Name', 'Job Description', 'Industry', 'Company Size': fill with 'Unknown'
    for col in ['Company Name', 'Job Description', 'Industry', 'Company Size']:
        if col in df_cleaned.columns:
            df_cleaned[col].fillna('Unknown', inplace=True)
    
    # For 'Skills Required': fill with 'Not Specified'
    if 'Skills Required' in df_cleaned.columns:
        df_cleaned['Skills Required'].fillna('Not Specified', inplace=True)

    # For 'Salary': This is critical. If missing, we might drop or impute carefully.
    # For now, let's see how many are missing. If too many, simple imputation might be bad.
    # If 'Salary' is object type, it needs conversion first.
    # Let's assume 'Salary' column exists and might have non-numeric characters like '$' or 'K'
    if 'Salary' in df_cleaned.columns:
        # Convert salary to numeric, removing non-numeric characters
        # This is a common pattern, adjust if salary format is different
        if df_cleaned['Salary'].dtype == 'object':
            df_cleaned['Salary'] = df_cleaned['Salary'].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df_cleaned['Salary'] = pd.to_numeric(df_cleaned['Salary'], errors='coerce') # Coerce errors will turn problematic parses into NaT/NaN

        # Now handle NaNs in salary (e.g., impute with median, or drop)
        # For simplicity in this script, we'll impute with median. EDA would inform this better.
        median_salary = df_cleaned['Salary'].median()
        df_cleaned['Salary'].fillna(median_salary, inplace=True)
        print(f"\nImputed missing 'Salary' values with median: {median_salary}")

    # 2. Correct Data Types (example, 'Year' if it's read as float)
    if 'Year' in df_cleaned.columns and df_cleaned['Year'].notnull().all():
        if df_cleaned['Year'].dtype != 'int64':
             # Check if all values can be integers (e.g. no 2023.5)
            if (df_cleaned['Year'] == df_cleaned['Year'].round()).all():
                df_cleaned['Year'] = df_cleaned['Year'].astype(int)
            else:
                print("Warning: 'Year' column contains non-integer values after attempting conversion.")


    # 3. Standardize Text Fields (e.g., lowercase, strip whitespace)
    categorical_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df_cleaned[col] = df_cleaned[col].str.strip().str.lower()
        # Replace multiple spaces with a single space
        df_cleaned[col] = df_cleaned[col].str.replace(r'\s+', ' ', regex=True)

    # 4. Remove Duplicates
    initial_rows = len(df_cleaned)
    df_cleaned.drop_duplicates(inplace=True)
    print(f"\nRemoved {initial_rows - len(df_cleaned)} duplicate rows.")

    print("\nMissing values after cleaning:")
    print(df_cleaned.isnull().sum())
    
    print("\nCleaned data info:")
    df_cleaned.info()

    print("\nData cleaning finished.")
    return df_cleaned

def main():
    print(f"Loading raw data from: {RAW_DATA_PATH}")
    try:
        df_raw = pd.read_csv(RAW_DATA_PATH)
    except FileNotFoundError:
        print(f"Error: Raw data file not found at {RAW_DATA_PATH}. Please ensure it's downloaded and placed correctly.")
        return
    
    df_cleaned = clean_data(df_raw)
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    
    print(f"\nSaving cleaned data to: {CLEANED_DATA_PATH}")
    df_cleaned.to_csv(CLEANED_DATA_PATH, index=False)
    print("Cleaned data saved successfully.")

if __name__ == "__main__":
    main()