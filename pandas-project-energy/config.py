# config.py
MERIT_ORDER_CONFIG = {
    'expected_cols': ['Date', 'Period', 'Lowest to Highest Offer Price ($/MWh)', 
                     'Total Offer Capacity At Specified Offer Price (MW)'],
    'date_cols': ['Date'],
    'numeric_cols': ['Period', 'Lowest to Highest Offer Price ($/MWh)', 
                    'Total Offer Capacity At Specified Offer Price (MW)']
}

USEP_CONFIG = {
    'expected_cols': ['INFORMATION TYPE', 'DATE', 'PERIOD', 'USEP ($/MWh)', 
                     'LCP ($/MWh)', 'DEMAND (MW)', 'TCL (MW)'],
    'date_cols': ['DATE'],
    'numeric_cols': ['PERIOD', 'USEP ($/MWh)', 'LCP ($/MWh)', 'DEMAND (MW)', 'TCL (MW)']
}

FILE_PATHS = {
    'merit_order': 'DelayedOfferStacks_Energy_01-Jan-2023 to 31-Jan-2023.csv',
    'usep': 'USEP_Jan-2023.csv'
}
