import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import plotly.express as px
from datetime import datetime
from io import StringIO

st.set_page_config(page_title="Marketing Dashboard", layout="wide")

st.title("📊 Matched Vendor Report")

# --- Google Sheets connection ---
def get_gs_client():
    try:
        creds_json = st.secrets["service_account"]
    except Exception:
        # Local fallback: load local file if present
        try:
            with open("service_account.json", "r") as f:
                creds_json = json.load(f)
        except Exception as e:
            st.error("Google service account credentials not found. Add them to Streamlit Secrets as 'service_account' or place 'service_account.json' locally for testing.")
            st.stop()
    try:
        SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_info(creds_json, scopes=SCOPE)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to authorize Google Sheets API: {e}")
        st.stop()

# Replace with your spreadsheet ID or URL in README; app will prompt if not set in secrets
SPREADSHEET_URL = st.secrets.get("spreadsheet_url", None)
if not SPREADSHEET_URL:
    st.info("No spreadsheet URL found in Streamlit secrets under key 'spreadsheet_url'. Please add it (see README).")
    # continue to allow user to add via secrets
    #st.stop()

client = get_gs_client()

# Try to open the spreadsheet
try:
    if SPREADSHEET_URL:
        sh = client.open_by_url(SPREADSHEET_URL)
    else:
        st.warning("Spreadsheet URL not set. Set 'spreadsheet_url' in Streamlit Secrets and rerun.")
        st.stop()
except Exception as e:
    st.error(f"Could not open spreadsheet: {e}")
    st.stop()

# Sheet names (as confirmed)
DATA_SHEET = "Sheet1"
VENDORS_SHEET = "Vendors"

try:
    sheet1 = sh.worksheet(DATA_SHEET)
    vendors_sheet = sh.worksheet(VENDORS_SHEET)
except Exception as e:
    st.error(f"Could not open required sheets ('{DATA_SHEET}', '{VENDORS_SHEET}'). Error: {e}")
    st.stop()

# Load data into pandas
try:
    data = pd.DataFrame(sheet1.get_all_records())
except Exception as e:
    st.error(f"Failed to read Sheet1 data: {e}")
    st.stop()

try:
    vendors = vendors_sheet.col_values(1)[1:]  # skip header
except Exception as e:
    st.error(f"Failed to read Vendors sheet: {e}")
    st.stop()

if data.empty:
    st.warning("Sheet1 appears empty. Make sure Boberdoo is populating data.")
    st.stop()

# Ensure a Date column exists and is parsed
date_col = None
for candidate in ["Date", "date", "Created", "created", "created_at"]:
    if candidate in data.columns:
        date_col = candidate
        break
if date_col is None:
    st.error("No Date column found in Sheet1. Expected a 'Date' column. Please rename or update README.")
    st.stop()

data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
data = data.dropna(subset=[date_col]).copy()
data["date_only"] = data[date_col].dt.date

# Basic columns expected (attempt to find common names)
def find_col(possible):
    for p in possible:
        if p in data.columns:
            return p
    return None

source_col = find_col(["Source Name", "source name", "Source", "source", "source_name", "Source Name (Vendors)"])
leads_col = find_col(["Leads", "leads", "Lead Count", "lead_count"])
spend_col = find_col(["Spend", "spend", "Amount", "amount"])
fronts_col = find_col(["Fronts", "fronts", "Front", "front"])
sales_col = find_col(["Sales", "sales", "Sale", "sale"])

if not source_col:
    st.error("Could not find a 'Source Name' column in Sheet1. Expected one of common variants. Columns found: " + ", ".join(data.columns))
    st.stop()

# UI: Filters
st.sidebar.header("Filters")
unique_dates = sorted(data["date_only"].unique(), reverse=True)
selected_date = st.sidebar.selectbox("Select Date", unique_dates, index=0)

# Vendor multiselect
vendors = [v for v in vendors if str(v).strip() != ""]
selected_vendors = st.sidebar.multiselect("Vendors (from Vendors sheet)", vendors, default=vendors)

# Filter data by date
filtered = data[data["date_only"] == selected_date].copy()

# Color map (from your script)
color_map = {
    "darkblue": "#b8cce4", "tangerine": "#ffe699", "mustard": "#fff2cc", "mauve": "#e4dfec",
    "lime": "#d8e4bc", "indigo": "#c5d9f1", "black": "#d9d9d9", "coral": "#f8cbad",
    "violet": "#e6b8b7", "crimson": "#f4b084", "sepia": "#e2c5a3", "lilac": "#d9d2e9",
    "purple": "#d9c3e8", "saffron": "#fce4d6", "grey": "#e7e6e6", "monarch media": "#f2dcdb",
    "pink": "#f4cccc"
}

# Helper: extract keyword from vendor entry like "Media Alpha (grey)"
import re
def keyword_from_vendor(v):
    m = re.search(r"\(([^)]+)\)", v)
    return m.group(1).lower().strip() if m else v.lower().strip()

# Build matched results
results = []
all_matched = []
for vendor in selected_vendors:
    kw = keyword_from_vendor(vendor)
    matched = filtered[filtered[source_col].astype(str).str.lower().str.contains(kw)]
    if matched.empty:
        continue
    # compute totals
    def to_num(col, df=matched):
        if col is None:
            return 0
        s = df[col].astype(str).replace(r'[^0-9.-]', '', regex=True)
        s = s.replace('', '0')
        try:
            return pd.to_numeric(s, errors='coerce').fillna(0).sum()
        except:
            return 0
    num_leads = to_num(leads_col)
    total_spent = to_num(spend_col)
    total_fronts = to_num(fronts_col)
    total_sales = to_num(sales_col)
    cost_per_front = (total_spent / total_fronts) if total_fronts else 0
    cost_per_sale = (total_spent / total_sales) if total_sales else 0
    color_key = next((c for c in color_map.keys() if c in kw), "grey")
    bg = color_map.get(color_key, "#e7e6e6")
    results.append({
        "Vendor": vendor,
        "Keyword": kw,
        "Rows": matched,
        "Leads": int(num_leads),
        "Spend": float(total_spent),
        "Fronts": int(total_fronts),
        "Sales": int(total_sales),
        "Cost/Front": float(cost_per_front),
        "Cost/Sale": float(cost_per_sale),
        "Color": bg
    })
    all_matched.append(matched)

# Summary metrics
st.header(f"Matched Vendor Report — {selected_date}")
if not results:
    st.info("No vendor matches found for this date with the selected vendors.")
else:
    total_spend = sum(r["Spend"] for r in results)
    total_leads = sum(r["Leads"] for r in results)
    total_sales = sum(r["Sales"] for r in results)
    total_fronts = sum(r["Fronts"] for r in results)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Spend", f"${total_spend:,.2f}")
    c2.metric("📈 Total Leads", f"{total_leads:,}")
    c3.metric("🏆 Total Sales", f"{total_sales:,}")
    c4.metric("⚙️ Cost / Sale", f"${(total_spend / total_sales) if total_sales else 0:,.2f}")

    # Show per-vendor sections
    for r in results:
        st.subheader(r["Vendor"])
        # show styled table using dataframe; Streamlit doesn't support cell background per row natively,
        # so we display the raw rows then show totals underneath.
        st.dataframe(r["Rows"], use_container_width=True)
        cols = st.columns(4)
        cols[0].metric("Leads", f"{r['Leads']:,}")
        cols[1].metric("Spend", f"${r['Spend']:,.2f}")
        cols[2].metric("Fronts", f"{r['Fronts']:,}")
        cols[3].metric("Sales", f"{r['Sales']:,}")
        st.markdown(f"**Cost / Front:** `${r['Cost/Front']:,.2f}`  •  **Cost / Sale:** `${r['Cost/Sale']:,.2f}`")
        st.write("---")

    # Combined table of vendor totals
    summary_df = pd.DataFrame([{
        "Vendor": r["Vendor"],
        "Leads": r["Leads"],
        "Spend": r["Spend"],
        "Fronts": r["Fronts"],
        "Sales": r["Sales"],
        "Cost/Front": r["Cost/Front"],
        "Cost/Sale": r["Cost/Sale"]
    } for r in results])
    st.subheader("Vendor Totals")
    st.dataframe(summary_df.set_index("Vendor").style.format({"Spend":"${:,.2f}", "Cost/Front":"${:,.2f}", "Cost/Sale":"${:,.2f}"}), use_container_width=True)

    # Chart: Spend by Vendor
    fig = px.bar(summary_df, x="Vendor", y="Spend", title=f"Spend by Vendor — {selected_date}", text="Spend")
    st.plotly_chart(fig, use_container_width=True)

# Auto-refresh note and a rerun button
with st.expander("Auto-refresh & Controls"):
    st.write("Data is read live from the Google Sheet. Use the button below to manually refresh.")
    if st.button("Refresh now"):
        st.experimental_rerun()

st.caption("Built for MarketingDashboard — reads Sheet1 and Vendors. Configure 'service_account' and 'spreadsheet_url' in Streamlit Secrets.")