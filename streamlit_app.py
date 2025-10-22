import pandas as pd
import streamlit as st

# --- 1️⃣ Load Google Sheet ---
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pubhtml"

# Read all tables
tables = pd.read_html(url)

# Assign tables manually
df_sheet1 = tables[0]  # Sheet1
df_vendors = tables[1]  # Vendors

# Clean columns
df_sheet1.columns = [c.strip() for c in df_sheet1.columns]
df_vendors.columns = [c.strip() for c in df_vendors.columns]

# --- 2️⃣ Preprocess ---
# Convert Day(date) to datetime
df_sheet1["Day(date)"] = pd.to_datetime(df_sheet1["Day(date)"], errors='coerce')

# Extract unique vendors from Vendors tab
vendors_list = df_vendors.iloc[:, 0].dropna().unique()

# Define color map
color_map = {
    "darkblue": "#b8cce4",
    "tangerine": "#ffe699",
    "mustard": "#fff2cc",
    "mauve": "#e4dfec",
    "lime": "#d8e4bc",
    "indigo": "#c5d9f1",
    "black": "#d9d9d9",
    "coral": "#f8cbad",
    "violet": "#e6b8b7",
    "crimson": "#f4b084",
    "sepia": "#e2c5a3",
    "lilac": "#d9d2e9",
    "purple": "#d9c3e8",
    "saffron": "#fce4d6",
    "grey": "#e7e6e6",
    "monarch media": "#f2dcdb",
    "pink": "#f4cccc"
}

# --- 3️⃣ Streamlit Dashboard ---
st.title("Vendor Matched Report Dashboard")

# Filter by date
dates = df_sheet1["Day(date)"].dropna().sort_values().unique()

for date in dates:
    st.subheader(f"📅 {pd.to_datetime(date).strftime('%A (%m/%d/%Y)')}")
    
    date_df = df_sheet1[df_sheet1["Day(date)"] == date]
    
    for vendor in vendors_list:
        match = pd.Series(vendor).str.extract(r'\(([^)]+)\)')[0]
        if match.empty or pd.isna(match[0]):
            continue
        keyword = match[0].lower()
        bg_color = color_map.get(keyword, "#e7e6e6")
        
        # Filter campaigns that match vendor keyword
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword)]
        if matched_rows.empty:
            continue
        
        # Display vendor header
        st.markdown(f"**{vendor}**", unsafe_allow_html=True)
        
        # Display campaigns table
        st.dataframe(
            matched_rows.style.set_properties(**{'background-color': bg_color, 'text-align': 'center'})
        )
        
        # Calculate totals per vendor
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = matched_rows["Fronts"].sum()
        total_sales = matched_rows["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts else 0
        cost_per_sale = total_spent / total_sales if total_sales else 0
        
        st.markdown(f"""
        **TOTAL ({keyword})**  
        Leads: {num_leads} | Spent: ${total_spent:.2f} | Fronts: {total_fronts} | Sales: {total_sales} | 
        Cost/Front: ${cost_per_front:.2f} | Cost/Sale: ${cost_per_sale:.2f}
        """)
    
    # Grand totals for the date
    total_leads = date_df["Number of Leads"].sum()
    total_spent = date_df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
    total_fronts = date_df["Fronts"].sum()
    total_sales = date_df["Sales"].sum()
    cost_per_front_all = total_spent / total_fronts if total_fronts else 0
    cost_per_sale_all = total_spent / total_sales if total_sales else 0
    
    st.markdown(f"""
    **GRAND TOTAL ({pd.to_datetime(date).strftime('%m/%d/%Y')})**  
    Leads: {total_leads} | Spent: ${total_spent:.2f} | Fronts: {total_fronts} | Sales: {total_sales} | 
    Cost/Front: ${cost_per_front_all:.2f} | Cost/Sale: ${cost_per_sale_all:.2f}
    """)
