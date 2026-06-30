notepad app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.logic import calculate_inventory_metrics

st.set_page_config(page_title="ICMC Cathlab Inventory", layout="wide")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv('data/inventory.csv')
    return calculate_inventory_metrics(df)

df_clean = load_data()

st.title("🏥 ICMC Cathlab Inventory Control Portal")
st.markdown("Predictive Supply Chain & Stock Optimization Engine")
st.write("---")

tab1, tab2, tab3 = st.tabs(["📊 Live Stock Dashboard", "📦 Log Item Consumption", "🚨 Procurement Alerts"])

with tab1:
    st.subheader("Current Stock Allocation")
    critical_count = len(df_clean[df_clean['Status'] == 'CRITICAL STOCKOUT RISK'])
    alert_count = len(df_clean[df_clean['Status'] == 'ORDER NOW (3-6 MO ALERT)'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Line Items Tracked", len(df_clean))
    col2.metric("Urgent Reorders Pending (3-6 Mo Alert)", alert_count, delta_color="inverse")
    col3.metric("Critical Stockout Risks", critical_count, delta_color="inverse")
    
    def style_status(val):
        if val == 'CRITICAL STOCKOUT RISK': return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
        elif val == 'ORDER NOW (3-6 MO ALERT)': return 'background-color: #ffe6cc; color: #cc6600; font-weight: bold;'
        return 'background-color: #e2f0d9; color: #385723;'

    st.dataframe(
        df_clean[['SKU', 'Item_Name', 'Category', 'Current_Stock', 'Months_Left', 'Status']].style.applymap(style_status, subset=['Status']),
        use_container_width=True
    )

with tab2:
    st.subheader("Log Used Items (End of Procedure)")
    with st.form("usage_form", clear_on_submit=True):
        selected_item = st.selectbox("Select Consumed Equipment", options=df_clean['Item_Name'].tolist())
        qty_used = st.number_input("Quantity Consumed", min_value=1, value=1, step=1)
        nurse_initials = st.text_input("Nurse Initials / Case ID")
        submit_btn = st.form_submit_button("Deduct From Stock")
        
        if submit_btn:
            raw_df = pd.read_csv('data/inventory.csv')
            raw_df.loc[raw_df['Item_Name'] == selected_item, 'Current_Stock'] -= qty_used
            raw_df.to_csv('data/inventory.csv', index=False)
            
            try:
                log_entry = pd.DataFrame([{
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Item_Name': selected_item,
                    'Quantity_Deducted': qty_used,
                    'Logged_By': nurse_initials
                }])
                log_entry.to_csv('data/usage_logs.csv', mode='a', header=not pd.io.common.file_exists('data/usage_logs.csv'), index=False)
            except Exception:
                pass
                
            st.success(f"Successfully deducted {qty_used} units of {selected_item}. Inventory updated.")
            st.cache_data.clear()
            st.annotation_tracker = None
            st.rerun()

with tab3:
    st.subheader("Predictive Procurement Action Plan")
    procurement_needed = df_clean[df_clean['Status'].isin(['CRITICAL STOCKOUT RISK', 'ORDER NOW (3-6 MO ALERT)'])]
    if not procurement_needed.empty:
        st.warning("⚠️ Attention Required: The following elements crossed their predictive safety threshold.")
        st.table(procurement_needed[['SKU', 'Item_Name', 'Current_Stock', 'Months_Left', 'Reorder_Point', 'Status']])
    else:
        st.success("✅ All stock configurations are healthy. No orders required for the next 6 months.")