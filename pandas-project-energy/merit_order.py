# merit_order.py
"""
Module for handling merit order curve visualization and related functionality.
"""
import pandas as pd
import matplotlib.pyplot as plt

def create_datetime(date_str, period):
    """
    Create datetime from date string and period number
    """
    date = pd.to_datetime(date_str)
    # Each period is 30 minutes, so multiply period-1 by 30 to get minutes offset
    minutes = (period - 1) * 30
    return date + pd.Timedelta(minutes=minutes)

def plot_merit_order(df, date, period):
    """
    Plot merit order curve for a specific date
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Merit order DataFrame with columns: Date, Period, 
        Lowest to Highest Offer Price ($/MWh),
        Total Offer Capacity At Specified Offer Price (MW)
    date : str
        Date to plot in format 'DD-MMM-YYYY'
        
    Returns:
    --------
    matplotlib.figure.Figure
        The plot figure object
    """
    # Filter data for the specified date and period
    period_data = df[(df['Date'] == date) & (df['Period'] == period)].copy()
    
    # Sort by price for cumulative volume calculation
    period_data = period_data.sort_values('Lowest to Highest Offer Price ($/MWh)')
    
    # Calculate cumulative volume
    period_data['Cumulative Volume'] = period_data['Total Offer Capacity At Specified Offer Price (MW)'].cumsum()
    
    # Create datetime for title
    datetime = create_datetime(date, period)

    # Create the plot
    fig = plt.figure(figsize=(12, 6))
    plt.plot(period_data['Cumulative Volume'], 
             period_data['Lowest to Highest Offer Price ($/MWh)'],
             'b-', label='bid_price')
    
    plt.grid(True)
    plt.xlabel('Cumulative bid volume [MW]')
    plt.ylabel('Bid price [$/MWh]')
    plt.title(f'Merit Order for {datetime}')
    plt.legend()
    
    return fig
