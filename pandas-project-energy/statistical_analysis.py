# energy_statistics.py
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

def initial_data_check(data, column_name):
    """Basic normality check for a data column"""
    # 1. Visual Checks
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Histogram
    sns.histplot(data=data, x=column_name, ax=ax1)
    ax1.set_title('Histogram')
    
    # Q-Q Plot
    stats.probplot(data[column_name], dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot')
    
    # Box Plot
    sns.boxplot(y=data[column_name], ax=ax3)
    ax3.set_title('Box Plot')
    
    # 2. Statistical Tests
    # D'Agostino and Pearson's test
    stat, p_value = stats.normaltest(data[column_name])

    # Shapiro-Wilk test
    # If dataset is too large, take a random sample for the Shapiro-Wilk test
    sample_size = min(5000, len(data))
    if len(data) > 5000:
        sample_data = data[column_name].sample(n=sample_size, random_state=42)
    else:
        sample_data = data[column_name]
    
    stat_shapiro, p_value_shapiro = stats.shapiro(sample_data)
    
    print(f"Normality Test Results for {column_name}:")
    print(f"p-value: {p_value:.4f}")
    print("Skewness:", stats.skew(data[column_name]))
    print("Kurtosis:", stats.kurtosis(data[column_name]))

    print(f"Shapiro-Wilk test p-value: {p_value_shapiro:.4f}")
    if len(data) > 5000:
        print(f"(Based on random sample of {sample_size} observations)")
    
    return fig

def analyze_energy_market(usep_df, merit_df):
    """
    Perform statistical analysis on energy market data
    """

    for column in ['DEMAND (MW)', 'USEP ($/MWh)']:
        fig = initial_data_check(usep_df, column)
        plt.show()

    # 1. Time Series Analysis
    daily_stats = usep_df.groupby('DATE').agg({
        'DEMAND (MW)': ['mean', 'std', 'min', 'max'],
        'USEP ($/MWh)': ['mean', 'std', 'min', 'max']
    })
    
    # 2. Correlation Analysis
    # correlation = usep_df[['DEMAND (MW)', 'USEP ($/MWh)']].corr()
    correlation = usep_df[['DEMAND (MW)', 'USEP ($/MWh)']].corr(method='spearman')
    
    # 3. Price Elasticity Analysis
    # Calculate percentage changes
    usep_df['price_pct_change'] = usep_df['USEP ($/MWh)'].pct_change()
    usep_df['demand_pct_change'] = usep_df['DEMAND (MW)'].pct_change()
    
    # Calculate price elasticity (avoiding division by zero)
    mask = (usep_df['price_pct_change'] != 0)
    # elasticity = (usep_df.loc[mask, 'demand_pct_change'] / 
    #              usep_df.loc[mask, 'price_pct_change']).mean()
    elasticity = (usep_df.loc[mask, 'demand_pct_change'] / 
                 usep_df.loc[mask, 'price_pct_change']).median()
    
    # 4. Hypothesis Testing
    # H0: Mean demand during peak hours (9-17) = Mean demand during off-peak
    peak_hours = range(18, 34)  # Periods 18-34 (9:00-17:00)
    peak_demand = usep_df[usep_df['PERIOD'].isin(peak_hours)]['DEMAND (MW)']
    offpeak_demand = usep_df[~usep_df['PERIOD'].isin(peak_hours)]['DEMAND (MW)']
    
    # t_stat, p_value = stats.ttest_ind(peak_demand, offpeak_demand)
    u_stat, u_pvalue = stats.mannwhitneyu(peak_demand, offpeak_demand, alternative='two-sided')
    
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
        # 'peak_vs_offpeak': {
        #     't_statistic': t_stat,
        #     'p_value': p_value
        # },
        'peak_vs_offpeak': {
            'u_statistic': u_stat,
            'u_pvalue': u_pvalue
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
    # print(f"t-statistic: {results['peak_vs_offpeak']['t_statistic']:.4f}")
    # print(f"p-value: {results['peak_vs_offpeak']['p_value']:.4f}")
    print(f"u-statistic: {results['peak_vs_offpeak']['u_statistic']:.4f}")
    print(f"u-pvalue: {results['peak_vs_offpeak']['u_pvalue']:.4f}")
    
    # if results['peak_vs_offpeak']['p_value'] < 0.05:
    if results['peak_vs_offpeak']['u_pvalue'] < 0.05:
        print("Conclusion: Significant difference between peak and off-peak demand")
    else:
        print("Conclusion: No significant difference between peak and off-peak demand")