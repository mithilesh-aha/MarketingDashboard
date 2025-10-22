import pandas as pd
import streamlit as st

# === 1️⃣ Read the full spreadsheet with multiple sheets ===
sheet_url = "YOUR_SPREADSHEET_URL"  # make sure to use CSV export link per sheet
sheet1_url = sheet_url + "&sheet=Sheet1&output=csv"
vendors_url = sheet_url + "&sheet=Vendors&output=csv"

df = pd.read_csv(sheet1_url)
vendors_df = pd.read_csv(vendors_url, header=None)  # Vendors tab has no header
vendors_list = vendors_df.iloc[:, 0].dropna().tolist()  # first column

# Extract vendor keywords from parentheses
vendor_keywords = {}
for v in vendors_list:
    if "(" in v and ")" in v:
        keyword = v.split("(")[1].split(")")[0].lower()
        vendor_keywords[v] = keyword
    else:
        vendor_keywords[v] = v.lower()

# === 2️⃣ Streamlit app ===
st.title("Vendor Matched Report Dashboard")

# Convert date column to datetime
df["Day(date)"] = pd.to_datetime(df["Day(date)"], errors="coerce")
dates = df["Day(date)"].dropna().sort_values().unique()

# Color map from your Apps Script
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

for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    date_df = df[df["Day(date)"] == date]

    all_matched_rows = []

    for vendor_name, keyword in vendor_keywords.items():
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword)]
        if matched_rows.empty:
            continue

        # Append for grand total
        all_matched_rows.append(matched_rows)

        # Show vendor total
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = matched_rows["Fronts"].sum()
        total_sales = matched_rows["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts else 0
        cost_per_sale = total_spent / total_sales if total_sales else 0

        st.markdown(f"**{vendor_name}**: Leads={num_leads}, Spent=${total_spent:.2f}, "
                    f"Fronts={total_fronts}, Sales={total_sales}, CPF=${cost_per_front:.2f}, CPS=${cost_per_sale:.2f}")

    # Grand total
    if all_matched_rows:
        grand_df = pd.concat(all_matched_rows)
        total_leads = grand_df["Number of Leads"].sum()
        total_spent = grand_df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = grand_df["Fronts"].sum()
        total_sales = grand_df["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts else 0
        cost_per_sale = total_spent / total_sales if total_sales else 0

        st.markdown(f"**GRAND TOTAL ({date.strftime('%m/%d/%Y')})**: Leads={total_leads}, "
                    f"Spent=${total_spent:.2f}, Fronts={total_fronts}, Sales={total_sales}, "
                    f"CPF=${cost_per_front:.2f}, CPS=${cost_per_sale:.2f}")
