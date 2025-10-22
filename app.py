import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marketing Dashboard", layout="wide")

# -----------------------------
# 1. Public Google Sheet CSV link
# -----------------------------
csv_url = "https://docs.google.com/spreadsheets/d/e/<SHEET_ID>/pub?output=csv"

# -----------------------------
# 2. Load data
# -----------------------------
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(csv_url)

# -----------------------------
# 3. Check required columns
# -----------------------------
required_columns = ["Date", "Vendor", "Amount"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"❌ Column '{col}' not found in Sheet1")
        st.stop()

# -----------------------------
# 4. Data preprocessing
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = df["Amount"].replace('[\$,]', '', regex=True).astype(float)

# -----------------------------
# 5. Date filter
# -----------------------------
min_date = df["Date"].min()
max_date = df["Date"].max()

selected_dates = st.date_input(
    "Filter by date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
else:
    df_filtered = df.copy()

# -----------------------------
# 6. Totals per vendor
# -----------------------------
vendor_totals = df_filtered.groupby("Vendor")["Amount"].sum().reset_index()
grand_total = df_filtered["Amount"].sum()

# -----------------------------
# 7. Color mapping for vendors
# -----------------------------
# Example: assign colors to each vendor
vendor_colors = {
    "Media Alpha": "#D9EAD3",
    "Vendor B": "#FCE5CD",
    "Vendor C": "#FFF2CC",
    # Add more vendors as needed
}

def color_vendor_row(row):
    return [f"background-color: {vendor_colors.get(row['Vendor'], '#FFFFFF')}" for _ in row]

# -----------------------------
# 8. Display dashboard
# -----------------------------
st.title("📊 Marketing Dashboard")

st.subheader("Per Vendor Totals")
st.dataframe(
    vendor_totals.style.format({"Amount": "${:,.2f}"}).apply(color_vendor_row, axis=1)
)

st.markdown(f"**Grand Total:** ${grand_total:,.2f}")

st.subheader("Filtered Data")
st.dataframe(
    df_filtered.style.format({"Amount": "${:,.2f}"}).apply(
        lambda x: ["background-color: #f9f9f9" if i % 2 == 0 else "" for i in range(len(x))], axis=1
    )
)

# -----------------------------
# 9. Download filtered data
# -----------------------------
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=df_filtered.to_csv(index=False),
    file_name="filtered_marketing_data.csv",
    mime="text/csv"
)
