import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re

st.set_page_config(page_title="Vendor Matched Report", layout="wide")
st.title("📊 Vendor Matched Report Dashboard")

# =======================
# Configuration
# =======================
SHEET1_GID = "0"  # Replace with Sheet1 gid
VENDORS_GID = "1234567"  # Replace with Vendors tab gid
SHEET_URL_TEMPLATE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv&gid={gid}"

# =======================
# Load Data
# =======================
def load_sheet(gid):
    url = SHEET_URL_TEMPLATE.format(gid=gid)
    csv_text = requests.get(url).text
    df = pd.read_csv(StringIO(csv_text))
    return df

df_main = load_sheet(SHEET1_GID)
df_vendors = load_sheet(VENDORS_GID)

# Extract vendors from column A
vendors_list = df_vendors.iloc[:, 0].dropna().tolist()

# Convert date column
df_main["Day(date)"] = pd.to_datetime(df_main["Day(date)"], errors="coerce")
df_main = df_main.dropna(subset=["Day(date)"])

# =======================
# Color Map
# =======================
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

# =======================
# Display Data
# =======================
dates = df_main["Day(date)"].sort_values().unique()

for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    date_df = df_main[df_main["Day(date)"] == date]
    
    all_matched_rows = []

    for vendor in vendors_list:
        match = re.search(r"\(([^)]+)\)", vendor)
        if not match:
            continue
        keyword = match.group(1).lower()
        bg_color = color_map.get(keyword, "#e7e6e6")
        
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword, na=False)]
        if matched_rows.empty:
            continue
        
        all_matched_rows.append(matched_rows)
        
        st.markdown(f"**{vendor}**")
        st.dataframe(
            matched_rows.style.set_properties(
                **{"background-color": bg_color, "text-align": "center"}
            )
        )
        
        # Totals per vendor
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        fronts = matched_rows["Fronts"].sum()
        sales = matched_rows["Sales"].sum()
        contact_rate = (sales / num_leads * 100 if num_leads > 0 else 0)
        cpf = total_spent / fronts if fronts > 0 else 0
        cps = total_spent / sales if sales > 0 else 0
        
        st.markdown(
            f"**TOTAL ({keyword.title()}): Leads={num_leads}, Spend=${total_spent:.2f}, "
            f"Fronts={fronts}, Sales={sales}, Contact Rate={contact_rate:.2f}%, "
            f"Cost-Per-Front=${cpf:.2f}, Cost-Per-Sale=${cps:.2f}**"
        )
    
    # Grand totals per date
    if all_matched_rows:
        grand_df = pd.concat(all_matched_rows)
        total_leads = grand_df["Number of Leads"].sum()
        total_spent = grand_df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        fronts = grand_df["Fronts"].sum()
        sales = grand_df["Sales"].sum()
        contact_rate = (sales / total_leads * 100 if total_leads > 0 else 0)
        cpf = total_spent / fronts if fronts > 0 else 0
        cps = total_spent / sales if sales > 0 else 0
        
        st.markdown(
            f"**GRAND TOTAL ({date.strftime('%A (%m/%d/%Y)')}): Leads={total_leads}, Spend=${total_spent:.2f}, "
            f"Fronts={fronts}, Sales={sales}, Contact Rate={contact_rate:.2f}%, "
            f"Cost-Per-Front=${cpf:.2f}, Cost-Per-Sale=${cps:.2f}**"
        )
