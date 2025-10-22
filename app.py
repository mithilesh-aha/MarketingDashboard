import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marketing Dashboard", layout="wide")

# -----------------------------
# 1. Public Google Sheet CSV link
# -----------------------------
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQk6J9kZy6k0FqZsX4CqJ6J6kz6kZ6kZ6kZ6kZ6/pub?output=csv"

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
required_columns = ["Source", "Number of Leads", "Total Amount Spent", "Fronts", "Sales", "Contact Rate", "Cost-Per-Front", "Cost-Per-Sale", "Day(date)"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"❌ Column '{col}' not found in Sheet1")
        st.stop()

# -----------------------------
# 4. Data preprocessing
# -----------------------------
df["Date"] = pd.to_datetime(df["Day(date)"], errors="coerce")
df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)

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
vendor_totals = df_filtered.groupby("Source")["Total Amount Spent"].sum().reset_index()
grand_total = df_filtered["Total Amount Spent"].sum()

# -----------------------------
# 7. Color mapping for vendors
# -----------------------------
vendor_colors = {
    "Black1_1": "#D9EAD3",
    "Darkblue1": "#FCE5CD",
    "Darkblue2": "#FFF2CC",
    "IndigoPremium": "#D9EAD3",
    "Lime1": "#FCE5CD",
    "Mauve1": "#FFF2CC",
    "Mustard3": "#D9EAD3",
    "Tangerine3": "#FCE5CD",
    "Black3_1": "#FFF2CC",
    "Coral3": "#D9EAD3",
    "Coral4": "#FCE5CD",
    "Darkblue3": "#FFF2CC",
    "Darkblue4": "#D9EAD3",
    "Grey3": "#FCE5CD",
    "Lime4": "#FFF2CC",
    "Pink3": "#D9EAD3",
    "Apple1": "#FCE5CD",
    "Apple2": "#FFF2CC",
    "Apple3": "#D9EAD3",
    "Apple4": "#FCE5CD",
    "Black2_1": "#FFF2CC",
    "Grey1": "#D9EAD3",
    "Lime3": "#FCE5CD",
    "Mustard3": "#FFF2CC",
    "Pink1": "#D9EAD3",
    "Pink2": "#FCE5CD",
    "Tangerine3": "#FFF2CC"
}

def color_vendor_row(row):
    return [f"background-color: {vendor_colors.get(row['Source'], '#FFFFFF')}" for _ in row]

# -----------------------------
# 8. Display dashboard
# -----------------------------
st.title("📊 Marketing Dashboard")

st.subheader("Per Vendor Totals")
st.dataframe(
    vendor_totals.style.format({"Total Amount Spent": "${:,.2f}"}).apply(color_vendor_row, axis=1)
)

st.markdown(f"**Grand Total:** ${grand_total:,.2f}")

st.subheader("Filtered Data")
st.dataframe(
    df_filtered.style.format({"Total Amount Spent": "${:,.2f}"}).apply(
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
