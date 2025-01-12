# main.py
import pandas as pd
import matplotlib.pyplot as plt
from data_validation import validate_dataset, print_dataset_info, ENERGY_MARKET_BOUNDS, clean_market_data, print_cleaning_summary 
from merit_order import plot_merit_order
from price_calculator import calculate_clearing_price, calculate_all_clearing_prices, test_calculate_clearing_price


def print_domain_validation_results(validation_results, dataset_name):
    """
    Pretty print validation results with domain-specific context
    """
    print(f"\n{dataset_name} Validation Results:")
    print("="* 50)

    
    # Check if all values in validation_results are empty
    is_empty = all(not value for value in validation_results.values() if not isinstance(value, bool))
    if is_empty and not validation_results.get("issues_found"):
        print("No issues found - all data within expected bounds")
        return

    if validation_results.get("domain_violations"):
        print("\nDomain Constraint Violations:")
        for col, info in validation_results["domain_violations"].items():
            print(f"\n{col}:")
            print(f"  Description: {info.get('description', 'No description available')}")
            print(f"  Violations found: {info['violations_count']} ({info['violation_percentage']:.2f}%)")
            print(f"  Expected range: {info['bounds']['min']} to {info['bounds']['max']}")
            print(f"  Actual range: {info['summary_stats']['min']:.2f} to {info['summary_stats']['max']:.2f}")
            if info.get('violation_examples'):
                print(f"  Sample violations: {info['violation_examples'][:3]}")

    if validation_results.get("missing_values"):
        print("\nMissing Values:")
        for col, count in validation_results["missing_values"].items():
            print(f"  {col}: {count}")

    if validation_results.get("duplicates"):
        print(f"\nDuplicate rows: {validation_results['duplicates']}")

    if validation_results.get("date_violations"):
        print("\nDate Violations:")
        for col, info in validation_results["date_violations"].items():
            print(f"\n{col}:")
            print(f"  Total violations: {info['total_violations']} ({info['violation_percentage']:.2f}%)")
            if info['invalid_format']:
                print(f"  Invalid format examples: {info['invalid_format'][:3]}")
                print(f"  Invalid format rows examples: {info['invalid_format_rows'][:3]}")
            if info['out_of_range_dates']:
                print(f"  Out of range date examples: {info['out_of_range_dates'][:3]}")
                print(f"  Out of range date rows examples: {info['out_of_range_dates_rows'][:3]}")

def main():
    # Load datasets
    merit_df_path = 'DelayedOfferStacks_Energy_01-Jan-2023 to 31-Jan-2023.csv'
    usep_df_path = 'USEP_Jan-2023.csv'

    try:
        # Load merit order data with correct column names
        merit_df = pd.read_csv(merit_df_path, skiprows=2)
        merit_df.columns = ['Date', 'Period', 
                          'Lowest to Highest Offer Price ($/MWh)',
                          'Total Offer Capacity At Specified Offer Price (MW)']
        
        # Load USEP data
        usep_df = pd.read_csv(usep_df_path)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return

    # 1. Data Validation
    print("\n=== Data Validation ===")
    
    # Define custom bounds if needed
    custom_bounds = {
        'price': {
            'min': -5000,
            'max': 5000,
            'description': 'Energy price bounds based on historical market limits'
        },
        'volume': {
            'min': 0,
            'max': 2000,
            'description': 'Volume bounds based on typical generation capacity'
        },
        'period': {
            'min': 1,
            'max': 48,
            'description': 'Valid period ranges for half-hourly trading'
        }
    }
    
    # Define the valid date range for your historical data
    valid_date_range = ('01 Jan 2023', '31 Jan 2023')

    # Run validation for merit order data
    merit_validation = validate_dataset(
        merit_df,
        expected_cols=['Date', 'Period', 
                      'Lowest to Highest Offer Price ($/MWh)',
                      'Total Offer Capacity At Specified Offer Price (MW)'],
        date_cols=['Date'],
        numeric_cols=['Period', 
                     'Lowest to Highest Offer Price ($/MWh)',
                     'Total Offer Capacity At Specified Offer Price (MW)'],
        bounds_config=custom_bounds,
        date_range=valid_date_range
    )

    # Run validation for USEP data
    usep_validation = validate_dataset(
        usep_df,
        expected_cols=['INFORMATION TYPE', 'DATE', 'PERIOD', 'USEP ($/MWh)', 
                      'LCP ($/MWh)', 'DEMAND (MW)', 'TCL (MW)'],
        date_cols=['DATE'],
        numeric_cols=['PERIOD', 'USEP ($/MWh)', 'LCP ($/MWh)', 'DEMAND (MW)', 'TCL (MW)'],
        bounds_config=custom_bounds,
        date_range=valid_date_range
    )

    # Print dataset info and validation results
    print_dataset_info(merit_df, "Merit Order Data")
    print_domain_validation_results(merit_validation, "Merit Order Data")
    print_dataset_info(usep_df, "USEP Data")
    print_domain_validation_results(usep_validation, "USEP Data")

    # Clean the datasets
    print("\n=== Data Cleaning ===")
    cleaned_merit_df = clean_market_data(merit_df, dataset_type='merit')
    cleaned_usep_df = clean_market_data(usep_df, dataset_type='usep')
    
    # Print cleaning summaries
    print_cleaning_summary(merit_df, cleaned_merit_df, "Merit Order Data")
    print_cleaning_summary(usep_df, cleaned_usep_df, "USEP Data")
    
    # Use cleaned dataframes from here on
    merit_df = cleaned_merit_df
    usep_df = cleaned_usep_df

    # 2. Merit Order Analysis
    print("\n=== Merit Order Analysis ===")
    # Plot merit order for January 1st, 2023
    sample_date = '2023-01-01'
    sample_period = 1
    fig = plot_merit_order(merit_df, sample_date, sample_period)
    plt.show()

    # 3. Price Calculation
    print("\n=== Price Analysis ===")
    # Run unit tests for price calculator
    print("Running price calculator unit tests:")
    test_calculate_clearing_price()

    # Calculate clearing price for a sample demand
    sample_demand = 5400  # MW
    sample_price = calculate_clearing_price(merit_df, sample_date, sample_period, sample_demand)
    print(f"\nSample clearing price calculation:")
    print(f"Date: {sample_date}")
    print(f"Demand: {sample_demand} MW")
    print(f"Calculated clearing price: {sample_price} $/MWh")

    # # Calculate all clearing prices
    # print("\nCalculating clearing prices for all periods...")
    # all_prices = calculate_all_clearing_prices(merit_df, usep_df)
    
    # # Print summary statistics
    # print("\nPrice Comparison Summary:")
    # print(all_prices[['actual_usep', 'calculated_price']].describe())
    
    # # Calculate and print mean absolute error
    # mae = (all_prices['actual_usep'] - all_prices['calculated_price']).abs().mean()
    # print(f"\nMean Absolute Error: {mae:.2f} $/MWh")



if __name__ == "__main__":
    main()
