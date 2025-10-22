import pandas as pd
import streamlit as st

# -------------------------------
# CONFIG: URLs to Google Sheet tabs
# -------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?gid=0&single=true&output=csv"
VENDORS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?gid=1234567890&single=true&output=csv"  # replace gid with Vendors tab

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(SHEET_URL)
vendors_df = pd.read_csv(VENDORS_URL)

# Ensure 'Day(date)' column is datetime
df['Day(date)'] = pd.to_datetime(df['Day(date)'], errors='coerce')
df = df.dropna(subset=['Day(date)'])

# Get unique vendors from Vendors tab
vendors_list = vendors_df.iloc[:, 0].dropna().str.strip().tolist()

# -------------------------------
# VENDOR COLOR MAP (matches App Script)
# -------------------------------
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

# -------------------------------
# FUNCTION TO GENERATE MATCHED REPORT
# -------------------------------
def generate_matched_report(df, vendors_list):
    report_rows = []

    for date, date_df in df.groupby('Day(date)'):
        date_str = date.strftime("%A (%m/%d/%Y)")
        report_rows.append({"type": "header", "date": date_str})

        all_matched_rows = []

        for vendor in vendors_list:
            import re
            match = re.search(r'\(([^)]+)\)', vendor)
            if not match:
                continue
            keyword = match.group(1).lower()
            color_key = next((c for c in color_map if c in keyword), "grey")
            bg_color = color_map[color_key]

            matched_rows = date_df[date_df['Source Name'].str.lower().str.contains(keyword, na=False)]
            if matched_rows.empty:
                continue

            all_matched_rows.append(matched_rows)

            # Add individual rows
            for _, row in matched_rows.iterrows():
                report_rows.append({
                    "type": "row",
                    "vendor_name": vendor,
                    "matched_vendor": row['Source Name'],
                    "Number of Leads": row['Number of Leads'],
                    "Total Amount Spent": row['Total Amount Spent'],
                    "Fronts": row['Fronts'],
                    "Sales": row['Sales'],
                    "Contact Rate": row.get('Contact Rate', ''),
                    "Cost-Per-Front": 0,
                    "Cost-Per-Sale": 0,
                    "bg_color": bg_color
                })

            # Vendor totals
            total_leads = matched_rows['Number of Leads'].sum()
            total_spent = matched_rows['Total Amount Spent'].replace('[\$,]', '', regex=True).astype(float).sum()
            total_fronts = matched_rows['Fronts'].sum()
            total_sales = matched_rows['Sales'].sum()
            cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
            cost_per_sale = total_spent / total_sales if total_sales > 0 else 0

            report_rows.append({
                "type": "total",
                "vendor_name": vendor,
                "Number of Leads": total_leads,
                "Total Amount Spent": f"${total_spent:.2f}",
                "Fronts": total_fronts,
                "Sales": total_sales,
                "Cost-Per-Front": f"${cost_per_front:.2f}",
                "Cost-Per-Sale": f"${cost_per_sale:.2f}",
                "bg_color": "#e2efda"
            })

        # Grand total for the date
        if all_matched_rows:
            all_rows_df = pd.concat(all_matched_rows)
            grand_total_leads = all_rows_df['Number of Leads'].sum()
            grand_total_spent = all_rows_df['Total Amount Spent'].replace('[\$,]', '', regex=True).astype(float).sum()
            grand_total_fronts = all_rows_df['Fronts'].sum()
            grand_total_sales = all_rows_df['Sales'].sum()
            grand_cost_per_front = grand_total_spent / grand_total_fronts if grand_total_fronts > 0 else 0
            grand_cost_per_sale = grand_total_spent / grand_total_sales if grand_total_sales > 0 else 0

            report_rows.append({
                "type": "grand_total",
                "date": date_str,
                "Number of Leads": grand_total_leads,
                "Total Amount Spent": f"${grand_total_spent:.2f}",
                "Fronts": grand_total_fronts,
                "Sales": grand_total_sales,
                "Cost-Per-Front": f"${grand_cost_per_front:.2f}",
                "Cost-Per-Sale": f"${grand_cost_per_sale:.2f}",
                "bg_color": "#bdd7ee"
            })

    return report_rows

# -------------------------------
# STREAMLIT APP
# -------------------------------
st.title("Vendor Matched Report Dashboard")

report = generate_matched_report(df, vendors_list)

for row in report:
    if row["type"] == "header":
        st.subheader(f"📅 {row['date']}")
    elif row["type"] == "row":
        st.markdown(f"""
        <div style="background-color:{row['bg_color']};padding:5px;border-radius:5px;">
        {row['vendor_name']} | {row['matched_vendor']} | {row['Number of Leads']} | {row['Total Amount Spent']} | {row['Fronts']} | {row['Sales']} | {row['Contact Rate']} | {row['Cost-Per-Front']} | {row['Cost-Per-Sale']}
        </div>
        """, unsafe_allow_html=True)
    elif row["type"] == "total":
        st.markdown(f"""
        <div style="background-color:{row['bg_color']};padding:5px;border-radius:5px;font-weight:bold;">
        TOTAL ({row['vendor_name']}) | {row['Number of Leads']} | {row['Total Amount Spent']} | {row['Fronts']} | {row['Sales']} | {row['Cost-Per-Front']} | {row['Cost-Per-Sale']}
        </div>
        """, unsafe_allow_html=True)
    elif row["type"] == "grand_total":
        st.markdown(f"""
        <div style="background-color:{row['bg_color']};padding:5px;border-radius:5px;font-weight:bold;color:#1f4e78;">
        GRAND TOTAL ({row['date']}) | {row['Number of Leads']} | {row['Total Amount Spent']} | {row['Fronts']} | {row['Sales']} | {row['Cost-Per-Front']} | {row['Cost-Per-Sale']}
        </div>
        """, unsafe_allow_html=True)
