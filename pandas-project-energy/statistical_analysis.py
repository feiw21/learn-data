# energy_statistics.py
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

def analyze_energy_market(usep_df, merit_df):
    """
    Perform statistical analysis on energy market data
    """
    # 1. Time Series Analysis
    daily_stats = usep_df.groupby('DATE').agg({
        'DEMAND (MW)': ['mean', 'std', 'min', 'max'],
        'USEP ($/MWh)': ['mean', 'std', 'min', 'max']
    })
    
    # 2. Correlation Analysis
    correlation = usep_df[['DEMAND (MW)', 'USEP ($/MWh)']].corr()
    
    # 3. Price Elasticity Analysis
    # Calculate percentage changes
    usep_df['price_pct_change'] = usep_df['USEP ($/MWh)'].pct_change()
    usep_df['demand_pct_change'] = usep_df['DEMAND (MW)'].pct_change()
    
    # Calculate price elasticity (avoiding division by zero)
    mask = (usep_df['price_pct_change'] != 0)
    elasticity = (usep_df.loc[mask, 'demand_pct_change'] / 
                 usep_df.loc[mask, 'price_pct_change']).mean()
    
    # 4. Hypothesis Testing
    # H0: Mean demand during peak hours (9-17) = Mean demand during off-peak
    peak_hours = range(18, 34)  # Periods 18-34 (9:00-17:00)
    peak_demand = usep_df[usep_df['PERIOD'].isin(peak_hours)]['DEMAND (MW)']
    offpeak_demand = usep_df[~usep_df['PERIOD'].isin(peak_hours)]['DEMAND (MW)']
    
    t_stat, p_value = stats.ttest_ind(peak_demand, offpeak_demand)
    
    # 5. Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Price vs Demand Scatter
    sns.scatterplot(data=usep_df, x='DEMAND (MW)', y='USEP ($/MWh)', 
                   alpha=0.5, ax=axes[0,0])
    axes[0,0].set_title('Price vs Demand')
    
    # Daily Price Distribution
    sns.boxplot(data=usep_df, x='PERIOD', y='USEP ($/MWh)', 
               ax=axes[0,1])
    axes[0,1].set_title('Price Distribution by Period')
    axes[0,1].set_xticks(range(0, 48, 6))
    
    # Demand Time Series
    sns.lineplot(data=usep_df, x='PERIOD', y='DEMAND (MW)', 
                errorbar=('ci', 95), ax=axes[1,0])
    axes[1,0].set_title('Average Demand by Period')
    
    # Price Elasticity Distribution
    sns.histplot(data=usep_df[mask], x='price_pct_change', y='demand_pct_change',
                ax=axes[1,1])
    axes[1,1].set_title('Price vs Demand Changes')
    
    plt.tight_layout()
    
    # 6. Prepare results summary
    results = {
        'daily_stats': daily_stats,
        'correlation': correlation,
        'price_elasticity': elasticity,
        'peak_vs_offpeak': {
            't_statistic': t_stat,
            'p_value': p_value
        },
        'plots': fig
    }
    
    return results

def print_analysis_results(results):
    """Print formatted analysis results"""
    print("\n=== Energy Market Statistical Analysis ===")
    
    print("\n1. Daily Statistics:")
    print(results['daily_stats'].round(2))
    
    print("\n2. Correlation Matrix:")
    print(results['correlation'].round(4))
    
    print("\n3. Price Elasticity of Demand:")
    print(f"Average elasticity: {results['price_elasticity']:.4f}")
    
    print("\n4. Peak vs Off-Peak Demand Test:")
    print(f"t-statistic: {results['peak_vs_offpeak']['t_statistic']:.4f}")
    print(f"p-value: {results['peak_vs_offpeak']['p_value']:.4f}")
    
    if results['peak_vs_offpeak']['p_value'] < 0.05:
        print("Conclusion: Significant difference between peak and off-peak demand")
    else:
        print("Conclusion: No significant difference between peak and off-peak demand")