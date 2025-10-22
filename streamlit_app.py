import streamlit as st
import pandas as pd

# -----------------------------
# 1️⃣ Load Data
# -----------------------------

# Google Sheet CSV URLs (published CSVs)
SHEET1_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"
VENDORS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"  # Replace with Vendors tab CSV if separate

# Read CSVs
df = pd.read_csv(SHEET1_URL)
vendors_df = pd.read_csv(VENDORS_URL)  # Assuming Vendors are in column 'Vendor' or 'A'

# Clean Vendors
unique_vendors = vendors_df.iloc[:, 0].dropna().unique()

# -----------------------------
# 2️⃣ Color Map (like Apps Script)
# -----------------------------
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

# -----------------------------
# 3️⃣ Preprocess Dates
# -----------------------------
df["Day(date)"] = pd.to_datetime(df["Day(date)"], errors="coerce")
df = df.dropna(subset=["Day(date)"])  # Remove invalid dates
dates = df["Day(date)"].sort_values().unique()

# -----------------------------
# 4️⃣ Streamlit Dashboard
# -----------------------------
st.title("Vendor Matched Report Dashboard")

for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    
    date_df = df[df["Day(date)"] == date]
    
    all_matched_rows = []

    for vendor_name in unique_vendors:
        # Extract keyword from vendor like in Apps Script
        import re
        match = re.search(r"\(([^)]+)\)", str(vendor_name))
        if not match:
            continue
        keyword = match.group(1).lower()
        bg_color = "#e7e6e6"  # default grey
        for c in color_map:
            if c in keyword:
                bg_color = color_map[c]
                break

        # Match rows for this vendor
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword, na=False)]
        if matched_rows.empty:
            continue
        
        all_matched_rows.append(matched_rows)
        
        # Display matched rows with color
        st.markdown(f"**Vendor: {vendor_name}**")
        st.dataframe(matched_rows.style.set_properties(**{"background-color": bg_color}))
        
        # Totals per vendor
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = matched_rows["Fronts"].sum()
        total_sales = matched_rows["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
        cost_per_sale = total_spent / total_sales if total_sales > 0 else 0

        st.markdown(f"**TOTAL ({keyword})**: Leads: {num_leads}, Spent: ${total_spent:.2f}, Fronts: {total_fronts}, Sales: {total_sales}, Cost/Front: ${cost_per_front:.2f}, Cost/Sale: ${cost_per_sale:.2f}")
    
    # Grand totals
    if all_matched_rows:
        combined = pd.concat(all_matched_rows)
        total_leads = combined["Number of Leads"].sum()
        total_spent = combined["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = combined["Fronts"].sum()
        total_sales = combined["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
        cost_per_sale = total_spent / total_sales if total_sales > 0 else 0
        st.markdown(f"**GRAND TOTAL ({date.strftime('%A (%m/%d/%Y)')})**: Leads: {total_leads}, Spent: ${total_spent:.2f}, Fronts: {total_fronts}, Sales: {total_sales}, Cost/Front: ${cost_per_front:.2f}, Cost/Sale: ${cost_per_sale:.2f}")
