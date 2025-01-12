# price_calculator.py
"""
Module for calculating clearing prices based on merit order and demand data.
"""
import pandas as pd
import numpy as np

def calculate_clearing_price(df, date, period, demand):
    """
    Calculate the clearing price for a given demand level
    
    Parameters:
    -----------
    order_df : pandas.DataFrame
        Merit order DataFrame with price and volume columns
    demand : float
        Demand level in MW
        
    Returns:
    --------
    float
        Clearing price in $/MWh
    """

    order_df = df[(df['Date'] == date) & (df['Period'] == period)].copy()

    # Sort by price
    sorted_df = order_df.sort_values('Lowest to Highest Offer Price ($/MWh)')
    
    # Calculate cumulative volume
    sorted_df['Cumulative Volume'] = sorted_df['Total Offer Capacity At Specified Offer Price (MW)'].cumsum()
    
    # Find the first price where cumulative volume exceeds demand
    clearing_price_row = sorted_df[sorted_df['Cumulative Volume'] >= demand].iloc[0]
    
    return clearing_price_row['Lowest to Highest Offer Price ($/MWh)']

def calculate_all_clearing_prices(order_df, usep_df):
    """
    Calculate clearing prices for all demands in the USEP data
    
    Parameters:
    -----------
    order_df : pandas.DataFrame
        Merit order DataFrame
    usep_df : pandas.DataFrame
        USEP DataFrame with demand data
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with datetime, actual USEP, calculated price, and demand
    """
    results = []
    
    for _, row in usep_df.iterrows():
        date = row['DATE']
        period = row['PERIOD']
        demand = row['DEMAND (MW)']
        
        # Get merit order data for this date
        daily_merit = order_df[order_df['Date'] == date]
        
        try:
            calculated_price = calculate_clearing_price(daily_merit, demand)
            results.append({
                'datetime': pd.to_datetime(f"{date} {(period-1)*0.5:02.1f}"),
                'actual_usep': row['USEP ($/MWh)'],
                'calculated_price': calculated_price,
                'demand': demand
            })
        except Exception as e:
            print(f"Error calculating price for {date} period {period}: {str(e)}")
    
    return pd.DataFrame(results)

def test_calculate_clearing_price():
    """
    Unit tests for the calculate_clearing_price function
    """
    # Create test data
    test_data = pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01'],
        'Period': [1, 1, 1, 1, 1],
        'Lowest to Highest Offer Price ($/MWh)': [-100, 0, 50, 100, 200],
        'Total Offer Capacity At Specified Offer Price (MW)': [100, 200, 300, 400, 500]
    })
    
    # Test cases
    test_cases = [
        (50, -100),    # Demand below first threshold
        (250, 0),      # Demand between first and second threshold
        (1500, 200),   # Demand above last threshold
    ]
    
    passed = True
    for demand, expected_price in test_cases:
        result = calculate_clearing_price(test_data, '2023-01-01', 1, demand)
        if result != expected_price:
            print(f"Test failed: Demand {demand}, Expected {expected_price}, Got {result}")
            passed = False
    
    if passed:
        print("All tests passed!")
    
    return passed

if __name__ == "__main__":
    # Run unit tests
    test_calculate_clearing_price()