import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Debugging / Spreadsheet Connection
# -----------------------------
st.set_page_config(page_title="Marketing Dashboard", layout="wide")

st.title("📊 Marketing Dashboard")

try:
    creds = Credentials.from_service_account_info(
        st.secrets["service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet_url = st.secrets["spreadsheet_url"]
    spreadsheet = client.open_by_url(sheet_url)
    st.success("✅ Connected successfully to Google Sheet!")
    st.write("Sheets available:", [s.title for s in spreadsheet.worksheets()])
except Exception as e:
    st.error(f"❌ Could not open spreadsheet: {e}")
    st.stop()

# -----------------------------
# Load Data
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
# Matching Vendors
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

    for _, row in matched_rows.iterrows():
        report_rows.append({
            "Vendor": vendor_name,
            "Source Name": row[0],
            **{k: row[k] for k in row.index[1:]},
            "Color": bg_color
        })

if not report_rows:
    st.warning("No matched data for the selected date.")
else:
    report_df = pd.DataFrame(report_rows)

    # Display table with colors
    def color_row(x):
        return [f'background-color: {x["Color"]}']*len(x)
    
    st.subheader(f"Matched Report for {selected_date}")
    st.dataframe(report_df.style.apply(color_row, axis=1))

    # Totals
    total_leads = report_df.get("Leads", pd.Series([0]*len(report_df))).sum()
    total_spent = report_df.get("Spent", pd.Series([0]*len(report_df))).sum()
    st.write(f"**Total Leads:** {total_leads}   |   **Total Spent:** ${total_spent}")

