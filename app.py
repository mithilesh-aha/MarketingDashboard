import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Marketing Dashboard", layout="wide")
st.title("📊 Marketing Dashboard")

# -----------------------------
# Connect to Google Sheet
# -----------------------------
try:
    creds = Credentials.from_service_account_info(
        st.secrets["service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet_url = st.secrets["spreadsheet_url"]
    spreadsheet = client.open_by_url(sheet_url)
    st.success("✅ Connected successfully to Google Sheet!")
except Exception as e:
    st.error(f"❌ Could not open spreadsheet: {e}")
    st.stop()

# -----------------------------
# Load Data from Sheet1 and Vendors only
# -----------------------------
sheet1 = spreadsheet.worksheet("Sheet1")
vendors_sheet = spreadsheet.worksheet("Vendors")

data1 = pd.DataFrame(sheet1.get_all_records())
vendors_list = [v[0] for v in vendors_sheet.get_all_values()[1:] if v[0].strip() != ""]

# -----------------------------
# Date Filter
# -----------------------------
if "Date" not in data1.columns:
    st.error("❌ Column 'Date' not found in Sheet1")
    st.stop()

data1["Date"] = pd.to_datetime(data1["Date"])
unique_dates = data1["Date"].dt.date.sort_values().unique()
selected_date = st.selectbox("Select Date", unique_dates)
filtered_data = data1[data1["Date"].dt.date == selected_date]

# -----------------------------
# Color Map for Vendors
# -----------------------------
color_map = {
    "darkblue": "#b8cce4", "tangerine": "#ffe699", "mustard": "#fff2cc",
    "mauve": "#e4dfec", "lime": "#d8e4bc", "indigo": "#c5d9f1", "black": "#d9d9d9",
    "coral": "#f8cbad", "violet": "#e6b8b7", "crimson": "#f4b084", "sepia": "#e2c5a3",
    "lilac": "#d9d2e9", "purple": "#d9c3e8", "saffron": "#fce4d6", "grey": "#e7e6e6",
    "monarch media": "#f2dcdb", "pink": "#f4cccc"
}

# -----------------------------
# Matching Vendors and Calculations
# -----------------------------
report_rows = []

for vendor_name in vendors_list:
    match = None
    if "(" in vendor_name and ")" in vendor_name:
        match = vendor_name.split("(")[1].replace(")", "").strip().lower()
    if not match:
        continue

    matched_rows = filtered_data[filtered_data.iloc[:,0].str.lower().str.contains(match)]
    if matched_rows.empty:
        continue

    color_key = next((c for c in color_map if c in match), "grey")
    bg_color = color_map[color_key]

    # Add per-row data with color
    for _, row in matched_rows.iterrows():
        report_rows.append({
            "Vendor": vendor_name,
            "Source Name": row[0],
            **{k: row[k] for k in row.index[1:]},
            "Color": bg_color
        })

# -----------------------------
# Convert to DataFrame
# -----------------------------
if not report_rows:
    st.warning("No matched data for the selected date.")
    st.stop()

report_df = pd.DataFrame(report_rows)

# -----------------------------
# KPIs
# -----------------------------
st.subheader(f"Summary for {selected_date}")
total_leads = report_df.get("Leads", pd.Series([0]*len(report_df))).sum()
total_spent = report_df.get("Spent", pd.Series([0]*len(report_df))).sum()
total_fronts = report_df.get("Fronts", pd.Series([0]*len(report_df))).sum()
total_sales = report_df.get("Sales", pd.Series([0]*len(report_df))).sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", total_leads)
col2.metric("Total Spent ($)", f"{total_spent:.2f}")
col3.metric("Total Fronts", total_fronts)
col4.metric("Total Sales", total_sales)

# -----------------------------
# Calculate per-vendor totals
# -----------------------------
vendor_summary = []
for vendor in report_df["Vendor"].unique():
    df = report_df[report_df["Vendor"] == vendor]
    leads = df.get("Leads", pd.Series([0]*len(df))).sum()
    spent = df.get("Spent", pd.Series([0]*len(df))).sum()
    fronts = df.get("Fronts", pd.Series([0]*len(df))).sum()
    sales = df.get("Sales", pd.Series([0]*len(df))).sum()
    cost_per_front = spent/fronts if fronts>0 else 0
    cost_per_sale = spent/sales if sales>0 else 0
    color = df["Color"].iloc[0]
    vendor_summary.append({
        "Vendor": vendor,
        "Leads": leads,
        "Spent": spent,
        "Fronts": fronts,
        "Sales": sales,
        "Cost/Front": f"{cost_per_front:.2f}",
        "Cost/Sale": f"{cost_per_sale:.2f}",
        "Color": color
    })

vendor_summary_df = pd.DataFrame(vendor_summary)

# -----------------------------
# Display Matched Report Table
# -----------------------------
def color_row(x):
    return [f'background-color: {x["Color"]}']*len(x)

st.subheader("Matched Report by Vendor")
st.dataframe(vendor_summary_df.style.apply(color_row, axis=1))

# -----------------------------
# Optional Charts
# -----------------------------
st.subheader("Leads and Spent by Vendor")
chart_data = vendor_summary_df[["Vendor", "Leads", "Spent"]].set_index("Vendor")
st.bar_chart(chart_data)
