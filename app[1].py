import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random

# --- Authenticate with Google Sheets via Streamlit secrets ---
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)
gc = gspread.authorize(creds)

# --- Sheet setup ---
SPREADSHEET_NAME = "MarketingDashboard"
DATA_SHEET = "Matched_Report"
VENDOR_SHEET = "Vendors"

worksheet = gc.open(SPREADSHEET_NAME).worksheet(DATA_SHEET)
vendors_ws = gc.open(SPREADSHEET_NAME).worksheet(VENDOR_SHEET)

# Load data
data = worksheet.get_all_records()
vendor_data = vendors_ws.get_all_records()

df = pd.DataFrame(data)
vendor_df = pd.DataFrame(vendor_data)

# Data cleaning
df = df[df["Source Name (Vendors)"] != ""]
df = df.fillna(0)

# Extract date
def extract_date(text):
    try:
        if '(' in text and ')' in text:
            return datetime.strptime(text.split('(')[1].split(')')[0], "%m/%d/%Y").date()
    except:
        return None
    return None

df["Date"] = None
current_date = None
for i in range(len(df)):
    vendor_name = str(df.loc[i, "Source Name (Vendors)"])
    possible_date = extract_date(vendor_name)
    if possible_date:
        current_date = possible_date
    df.loc[i, "Date"] = current_date

df = df[~df["Source Name (Vendors)"].str.contains("TOTAL|GRAND TOTAL|nan", case=False, na=False)]

# Vendor colors
def color_name_to_hex(color_name):
    color_map = {
        "grey": "#d3d3d3",
        "gray": "#d3d3d3",
        "black": "#bdbdbd",
        "darkblue": "#8bb6ff",
        "indigo": "#a7b0ff",
        "mauve": "#d8b7dd",
        "tangerine": "#ffb347",
        "mustard": "#ffdb58",
        "lime": "#aee572",
        "coral": "#ff7f7f",
        "pink": "#ffb6c1",
        "apple": "#a8e4a0",
        "lilac": "#c8a2c8",
        "blue": "#87ceeb",
        "green": "#90ee90",
        "orange": "#ffb347",
        "yellow": "#ffff99",
    }
    return color_map.get(color_name.strip("()").lower(), f"#{random.randint(0,0xFFFFFF):06x}")

vendor_colors = {}
for _, row in vendor_df.iterrows():
    vendor_name = str(row[vendor_df.columns[0]])
    color_label = str(row[vendor_df.columns[1]])
    vendor_colors[vendor_name.split('(')[0].strip().lower()] = color_name_to_hex(color_label)

# Combine duplicates
group_cols = ["Date", "Source Name (Vendors)", "Matched Vendor"]
agg_dict = {
    "Number of Leads": "sum",
    "Total Amount Spent": "sum",
    "Fronts": "sum",
    "Sales": "sum",
    "Contact Rate": "mean",
    "Cost-Per-Front": "mean",
    "Cost-Per-Sale": "mean"
}
combined = df.groupby(group_cols, as_index=False).agg(agg_dict)

# Streamlit dashboard
st.set_page_config(page_title="Marketing Dashboard", layout="wide")
st.title("📊 Marketing Performance Dashboard")
st.caption("Auto-refreshing Google Sheets report — Vendor & Date wise view")

col1, col2 = st.columns(2)
with col1:
    selected_date = st.selectbox("📅 Select Date", sorted(df["Date"].dropna().unique()))
with col2:
    vendors = sorted(combined["Source Name (Vendors)"].unique())
    selected_vendor = st.selectbox("🏷️ Select Vendor", ["All"] + vendors)

filtered = combined[combined["Date"] == selected_date]
if selected_vendor != "All":
    filtered = filtered[filtered["Source Name (Vendors)"] == selected_vendor]

def color_row(row):
    name = str(row["Source Name (Vendors)"]).split("(")[0].strip().lower()
    return f"background-color: {vendor_colors.get(name, '')}"

st.markdown("### 💼 Vendor Performance Summary")
styled_df = filtered.style.apply(lambda row: [color_row(row)]*len(row), axis=1)
st.dataframe(styled_df, use_container_width=True)

st.markdown("### 📈 Summary Totals")
totals = filtered[["Number of Leads", "Total Amount Spent", "Fronts", "Sales"]].sum()
totals_df = pd.DataFrame(totals).transpose()
st.dataframe(totals_df)

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
