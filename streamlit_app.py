import pandas as pd
import streamlit as st

# -----------------------------
# 1. Load CSVs
# -----------------------------
# Campaign data (Sheet1)
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"
df = pd.read_csv(csv_url)

# Vendors sheet
vendors_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"  # replace with actual Vendors sheet CSV
vendors_df = pd.read_csv(vendors_url)

# Extract vendor names and keywords
vendors_df = vendors_df.dropna()
vendors_df['keyword'] = vendors_df['Vendor'].str.extract(r'\(([^)]+)\)')[0].str.lower()
unique_vendors = vendors_df[['Vendor', 'keyword']].to_dict('records')

# -----------------------------
# 2. Preprocess campaign data
# -----------------------------
# Convert "Total Amount Spent" to float
df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)

# Ensure dates are datetime
df['Day(date)'] = pd.to_datetime(df['Day(date)'], errors='coerce')

# -----------------------------
# 3. Streamlit App
# -----------------------------
st.title("Vendor Matched Report Dashboard")

# Select a date
dates = df['Day(date)'].dropna().sort_values().unique()
selected_date = st.selectbox("Select Date", dates)

date_df = df[df["Day(date)"] == selected_date]

# Display per vendor
for vendor in unique_vendors:
    vendor_name = vendor['Vendor']
    keyword = vendor['keyword']
    
    # Match campaigns containing the keyword
    matched = date_df[date_df['Source'].str.lower().str.contains(keyword)]
    
    if matched.empty:
        continue
    
    st.subheader(f"{vendor_name} ({len(matched)} campaigns)")
    
    # Display matched campaigns
    st.dataframe(matched)
    
    # Aggregate totals
    total_leads = matched['Number of Leads'].sum()
    total_spent = matched['Total Amount Spent'].sum()
    total_fronts = matched['Fronts'].sum()
    total_sales = matched['Sales'].sum()
    cost_per_front = total_spent / total_fronts if total_fronts else 0
    cost_per_sale = total_spent / total_sales if total_sales else 0
    
    st.markdown(f"""
    **Totals for {vendor_name}**
    - Leads: {total_leads}
    - Total Spent: ${total_spent:,.2f}
    - Fronts: {total_fronts}
    - Sales: {total_sales}
    - Cost per Front: ${cost_per_front:,.2f}
    - Cost per Sale: ${cost_per_sale:,.2f}
    """)
