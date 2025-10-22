import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re

st.title("Vendor Matched Report Dashboard")

# URLs
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv&gid={gid}"

# Load Sheet1
sheet1_csv = requests.get(SHEET_URL.format(gid=0)).text  # Assuming Sheet1 has gid=0
df = pd.read_csv(StringIO(sheet1_csv))

# Load Vendors tab
vendors_csv = requests.get(SHEET_URL.format(gid=1234567)).text  # Replace with actual gid for Vendors tab
vendors_df = pd.read_csv(StringIO(vendors_csv))
vendors_list = vendors_df.iloc[:, 0].dropna().tolist()  # Column A

# Convert Day(date) to datetime
df["Day(date)"] = pd.to_datetime(df["Day(date)"], errors="coerce")
df = df.dropna(subset=["Day(date)"])

# Color map
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

# Group by date
dates = df["Day(date)"].sort_values().unique()

for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    date_df = df[df["Day(date)"] == date]
    
    all_matched_rows = []
    
    for vendor in vendors_list:
        match = re.search(r"\(([^)]+)\)", vendor)
        if not match:
            continue
        keyword = match.group(1).lower()
        bg_color = color_map.get(keyword, "#e7e6e6")
        
        # Match campaigns in Sheet1 with keyword
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword, na=False)]
        if matched_rows.empty:
            continue
        
        all_matched_rows.append(matched_rows)
        
        st.markdown(f"**Vendor: {vendor}**")
        st.dataframe(matched_rows.style.set_properties(**{"background-color": bg_color}))
        
        # Totals per vendor
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        fronts = matched_rows["Fronts"].sum()
        sales = matched_rows["Sales"].sum()
        cost_per_front = total_spent / fronts if fronts > 0 else 0
        cost_per_sale = total_spent / sales if sales > 0 else 0
        
        st.markdown(f"**TOTAL ({vendor}): Leads={num_leads}, Spend=${total_spent:.2f}, Fronts={fronts}, Sales={sales}, CPF=${cost_per_front:.2f}, CPS=${cost_per_sale:.2f}**")
    
    # Grand total per date
    if all_matched_rows:
        grand_df = pd.concat(all_matched_rows)
        total_leads = grand_df["Number of Leads"].sum()
        total_spent = grand_df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        fronts = grand_df["Fronts"].sum()
        sales = grand_df["Sales"].sum()
        cost_per_front = total_spent / fronts if fronts > 0 else 0
        cost_per_sale = total_spent / sales if sales > 0 else 0
        st.markdown(f"**GRAND TOTAL ({date.strftime('%A')}): Leads={total_leads}, Spend=${total_spent:.2f}, Fronts={fronts}, Sales={sales}, CPF=${cost_per_front:.2f}, CPS=${cost_per_sale:.2f}**")
