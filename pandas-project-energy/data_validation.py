import pandas as pd
import numpy as np
from datetime import datetime

# Define domain-specific bounds for energy market data
ENERGY_MARKET_BOUNDS = {
    'price': {
        'min': -5000,    # Minimum reasonable price ($/MWh)
        'max': 5000,     # Maximum reasonable price ($/MWh)
        'description': 'Energy price bounds based on historical market limits'
    },
    'volume': {
        'min': 0,        # Minimum possible volume (MW)
        'max': 2000,     # Maximum reasonable volume (MW)
        'description': 'Volume bounds based on typical generation capacity'
    },
    'period': {
        'min': 1,        # First period of day
        'max': 48,       # Last period of day (half-hourly)
        'description': 'Valid period ranges for half-hourly trading'
    },
    'demand': {
        'min': 4000,     # Minimum expected demand (MW)
        'max': 8000,     # Maximum expected demand (MW)
        'description': 'Demand bounds based on typical system load'
    },
    'tcl': {
        'min': 0,        # Minimum transmission loss
        'max': 100,      # Maximum reasonable transmission loss
        'description': 'Transmission loss bounds'
    }
}

def validate_dataset(df, expected_cols=None, date_cols=None, numeric_cols=None, bounds_config=None, date_range=None):
    """
    Comprehensive data validation function for energy market datasets.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame to validate
    expected_cols : list
        List of expected column names
    date_cols : list
        List of columns that should contain dates
    numeric_cols : list
        List of columns that should contain numeric values
    bounds_config : dict
        Configuration for domain-specific bounds
    date_range : tuple
        (start_date, end_date) tuple for valid date range
    
    Returns:
    --------
    dict
        Dictionary containing validation results and issues found
    """

    validation_results = {
        "missing_values": {},
        "data_types": {},
        "value_ranges": {},
        "duplicates": 0,
        "issues_found": False,
        "domain_violations": {},
        "date_violations": {}
    }
    
    # Use provided bounds or default energy market bounds
    domain_bounds = bounds_config if bounds_config is not None else ENERGY_MARKET_BOUNDS

    # Column presence check
    if expected_cols:
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            validation_results["missing_columns"] = list(missing_cols)
            validation_results["issues_found"] = True
    
    # Missing values check
    missing_vals = df.isnull().sum()
    if missing_vals.any():
        validation_results["missing_values"] = missing_vals[missing_vals > 0].to_dict()
        validation_results["issues_found"] = True
    
    # Date validation
    if date_cols and date_range:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        for col in date_cols:
            if col in df.columns:
                try:
                    # ensure the date column in a consistent format of yyyy-mm-dd before the validation
                    dates = pd.to_datetime(df[col], errors='coerce').dt.normalize()
                    # date check
                    invalid_dates = df[dates.isnull()][col]
                    invalid_dates_rows = df[dates.isnull()]
                    out_of_range_dates = df[(dates < start_date) | (dates > end_date)][col]
                    out_of_range_dates_rows = df[(dates < start_date) | (dates > end_date)]
                    
                    if not invalid_dates.empty or not out_of_range_dates.empty:
                        validation_results["date_violations"][col] = {
                            "invalid_format": invalid_dates.tolist(),
                            "invalid_format_rows": invalid_dates_rows.to_dict(orient='records'),
                            "out_of_range_dates": out_of_range_dates.tolist(),
                            "out_of_range_dates_rows": out_of_range_dates_rows.to_dict(orient='records'),
                            "total_violations": len(invalid_dates) + len(out_of_range_dates),
                            "violation_percentage": ((len(invalid_dates) + len(out_of_range_dates)) / len(df)) * 100
                        }
                        validation_results["issues_found"] = True
                except Exception as e:
                    validation_results["data_types"][col] = f"Invalid date format: {str(e)}"
                    validation_results["issues_found"] = True


    # Domain-specific validation
    if numeric_cols:
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    validation_results["data_types"][col] = "Non-numeric data"
                    validation_results["issues_found"] = True
                else:
                    # Determine which bounds to use
                    bound_type = None
                    if 'price' in col.lower():
                        bound_type = 'price'
                    elif 'volume' in col.lower() or 'capacity' in col.lower():
                        bound_type = 'volume'
                    elif 'period' in col.lower():
                        bound_type = 'period'
                    elif 'demand' in col.lower():
                        bound_type = 'demand'
                    elif 'tcl' in col.lower():
                        bound_type = 'tcl'
                    
                    if bound_type and bound_type in domain_bounds:
                        bound_config = domain_bounds[bound_type]
                        violations = df[
                            (df[col] < bound_config['min']) | 
                            (df[col] > bound_config['max'])
                        ][col]
                        
                        if not violations.empty:
                            validation_results["domain_violations"][col] = {
                                "violations_count": len(violations),
                                "violation_percentage": (len(violations) / len(df)) * 100,
                                "bounds": {
                                    "min": bound_config['min'],
                                    "max": bound_config['max']
                                },
                                "description": bound_config['description'],
                                "violation_examples": violations.tolist()[:5],
                                "summary_stats": {
                                    "min": df[col].min(),
                                    "max": df[col].max(),
                                    "mean": df[col].mean(),
                                    "median": df[col].median()
                                }
                            }
    
    # Duplicate check
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        validation_results["duplicates"] = duplicates
        validation_results["issues_found"] = True
    
    return validation_results

def print_dataset_info(df, name):
    """
    Print summary information about a dataset
    """
    print(f"\n{name} Dataset Summary:")
    print("------------------------")
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}" 
          if 'Date' in df.columns else f"Date range: {df['DATE'].min()} to {df['DATE'].max()}")
    print("\nColumn Statistics:")
    print(df.describe())

# Add to data_validation.py

def clean_market_data(df, dataset_type='merit'):
    """
    Clean market data by handling invalid dates, periods, and values
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame to clean
    dataset_type : str
        Type of dataset ('merit' or 'usep')
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned DataFrame
    """
    cleaned_df = df.copy()
    
    # Convert date column
    date_col = 'Date' if dataset_type == 'merit' else 'DATE'

    # Clean dates
    def is_valid_date(date_str):
        """Helper function to validate date string"""
        try:
            # Convert to datetime using mixed format
            date = pd.to_datetime(date_str, format='mixed')
            # Basic validation for day
            return 1 <= date.day <= 31
        except:
            return False
   
    # Create a boolean column for valid/invalid dates
    valid_dates_mask = cleaned_df[date_col].apply(is_valid_date)  

    # Filter out invalid dates first (e.g., '40 Jan 2023')
    cleaned_df = cleaned_df[valid_dates_mask]

    try:
        cleaned_df[date_col] = pd.to_datetime(cleaned_df[date_col], format='mixed')
        # Keep only January 2023 data
        cleaned_df = cleaned_df[
            (cleaned_df[date_col].dt.year == 2023) & 
            (cleaned_df[date_col].dt.month == 1)
        ]
    except Exception as e:
        print(f"Error cleaning dates: {str(e)}")
        return pd.DataFrame()
    
    # Clean periods (should be 1-48)
    period_col = 'Period' if dataset_type == 'merit' else 'PERIOD'
    cleaned_df = cleaned_df[
        (cleaned_df[period_col] >= 1) & 
        (cleaned_df[period_col] <= 48)
    ]
    
    if dataset_type == 'merit':
        # Clean price and volume data
        price_col = 'Lowest to Highest Offer Price ($/MWh)'
        volume_col = 'Total Offer Capacity At Specified Offer Price (MW)'
        
        # Remove rows with invalid prices or volumes
        cleaned_df = cleaned_df[
            (cleaned_df[price_col] >= ENERGY_MARKET_BOUNDS['price']['min']) &
            (cleaned_df[price_col] <= ENERGY_MARKET_BOUNDS['price']['max']) &
            (cleaned_df[volume_col] >= ENERGY_MARKET_BOUNDS['volume']['min']) &
            (cleaned_df[volume_col] <= ENERGY_MARKET_BOUNDS['volume']['max'])
        ]
    
    elif dataset_type == 'usep':
        # Clean USEP price and demand data
        cleaned_df = cleaned_df[
            (cleaned_df['USEP ($/MWh)'] >= ENERGY_MARKET_BOUNDS['price']['min']) &
            (cleaned_df['USEP ($/MWh)'] <= ENERGY_MARKET_BOUNDS['price']['max']) &
            (cleaned_df['DEMAND (MW)'] >= ENERGY_MARKET_BOUNDS['demand']['min']) &
            (cleaned_df['DEMAND (MW)'] <= ENERGY_MARKET_BOUNDS['demand']['max'])
        ]
    
    return cleaned_df

def print_cleaning_summary(original_df, cleaned_df, dataset_name):
    """
    Print summary of data cleaning results
    """
    removed_rows = len(original_df) - len(cleaned_df)
    removed_percentage = (removed_rows / len(original_df)) * 100
    
    print(f"\n{dataset_name} Cleaning Summary:")
    print(f"Original rows: {len(original_df)}")
    print(f"Cleaned rows: {len(cleaned_df)}")
    print(f"Removed rows: {removed_rows} ({removed_percentage:.2f}%)")
    print(f"Sample data after cleaning: {cleaned_df.sample(5)}")