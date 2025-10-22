import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Marketing Dashboard", layout="wide")

# ----------------------------
# Load Google Sheets
# ----------------------------
def get_gsheet_data():
    service_account_info = st.secrets["service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    
    gc = gspread.authorize(creds)
    sh = gc.open_by_url(st.secrets["spreadsheet_url"])
    
    # Read Sheet1
    try:
        sheet1 = sh.worksheet("Sheet1")
        df_sheet1 = pd.DataFrame(sheet1.get_all_records())
    except:
        df_sheet1 = pd.DataFrame()
    
    # Read Vendors
    try:
        vendors = sh.worksheet("Vendors")
        df_vendors = pd.DataFrame(vendors.get_all_records())
        vendor_list = df_vendors.iloc[:,0].dropna().tolist()
    except:
        vendor_list = []
    
    return df_sheet1, vendor_list

df, vendors = get_gsheet_data()

# ----------------------------
# Date filter
# ----------------------------
if not df.empty and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    selected_dates = st.sidebar.date_input(
        "Filter by Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if isinstance(selected_dates, tuple):
        start_date, end_date = selected_dates
        df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))]

# ----------------------------
# Matched Report logic
# ----------------------------
def generate_matched_report(df, vendors):
    output_rows = []
    color_map = {
        "grey": "#e7e6e6",
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
        "monarch media": "#f2dcdb",
        "pink": "#f4cccc"
    }
    
    df_copy = df.copy()
    df_copy.columns = [c.strip() for c in df_copy.columns]

    vendor_totals = []
    
    for vendor in vendors:
        match = None
        if "(" in vendor and ")" in vendor:
            match = vendor.split("(")[1].split(")")[0].strip().lower()
        if not match:
            continue
        matched_rows = df_copy[df_copy.iloc[:,0].str.lower().str.contains(match)]
        if matched_rows.empty:
            continue
        
        bg_color = color_map.get(match, "#e7e6e6")
        for _, row in matched_rows.iterrows():
            row_data = {
                "Vendor": vendor,
                "Source": row.iloc[0],
                **row.iloc[1:].to_dict()
            }
            row_data["_bg"] = bg_color
            output_rows.append(row_data)
        
        # Totals per vendor
        num_leads = matched_rows.iloc[:,1].apply(pd.to_numeric, errors="coerce").sum()
        total_spent = matched_rows.iloc[:,2].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = matched_rows.iloc[:,3].apply(pd.to_numeric, errors="coerce").sum()
        total_sales = matched_rows.iloc[:,4].apply(pd.to_numeric, errors="coerce").sum()
        cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
        cost_per_sale = total_spent / total_sales if total_sales > 0 else 0

        vendor_totals.append({
            "Vendor": f"TOTAL ({vendor})",
            "Source": "",
            "Leads": num_leads,
            "Spent": total_spent,
            "Fronts": total_fronts,
            "Sales": total_sales,
            "Cost/Front": cost_per_front,
            "Cost/Sale": cost_per_sale,
            "_bg": "#d9ead3"  # light green for totals
        })
    
    report_df = pd.DataFrame(output_rows)
    totals_df = pd.DataFrame(vendor_totals)
    final_df = pd.concat([report_df, totals_df], ignore_index=True)
    
    # Grand totals
    if not report_df.empty:
        total_leads = report_df.iloc[:,2].apply(pd.to_numeric, errors="coerce").sum()
        total_spent = report_df.iloc[:,3].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = report_df.iloc[:,4].apply(pd.to_numeric, errors="coerce").sum()
        total_sales = report_df.iloc[:,5].apply(pd.to_numeric, errors="coerce").sum()
        cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
        cost_per_sale = total_spent / total_sales if total_sales > 0 else 0
        grand_total = pd.DataFrame([{
            "Vendor": "GRAND TOTAL",
            "Source": "",
            "Leads": total_leads,
            "Spent": total_spent,
            "Fronts": total_fronts,
            "Sales": total_sales,
            "Cost/Front": cost_per_front,
            "Cost/Sale": cost_per_sale,
            "_bg": "#bdd7ee"  # light blue for grand total
        }])
        final_df = pd.concat([final_df, grand_total], ignore_index=True)
    
    return final_df

report_df = generate_matched_report(df, vendors)

# ----------------------------
# Display in Streamlit
# ----------------------------
st.title("Marketing Matched Report")
st.write(f"Total rows: {len(report_df)}")

if not report_df.empty:
    # Display dataframe with background colors
    def color_row(row):
        return [f"background-color: {row['_bg']}" if "_bg" in row else "" for _ in row]

    st.dataframe(report_df.style.apply(color_row, axis=1).hide_columns(["_bg"]), use_container_width=True)
else:
    st.info("No matching data found for selected dates/vendors.")
