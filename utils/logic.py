notepad utils\logic.py
import pandas as pd
import numpy as np

def calculate_inventory_metrics(df):
    """
    Calculates the Reorder Point (ROP) and status based on a 3-6 month early warning logic.
    Formula: ROP = Avg_Monthly_Usage * (Lead_Time_Months + Safety_Stock_Months)
    """
    usage = df['Avg_Monthly_Usage'].replace(0, 0.1)
    df['Months_Left'] = df['Current_Stock'] / usage
    df['Reorder_Point'] = df['Avg_Monthly_Usage'] * (df['Lead_Time_Months'] + df['Safety_Stock_Months'])
    
    conditions = [
        (df['Current_Stock'] <= df['Avg_Monthly_Usage'] * df['Lead_Time_Months']),
        (df['Current_Stock'] <= df['Reorder_Point']),
        (df['Current_Stock'] > df['Reorder_Point'])
    ]
    choices = ['CRITICAL STOCKOUT RISK', 'ORDER NOW (3-6 MO ALERT)', 'OK']
    df['Status'] = np.select(conditions, choices, default='OK')
    
    return df