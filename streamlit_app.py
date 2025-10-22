import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# CSV link (published Google Sheet)
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"

# -----------------------------
# Load data
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # Clean numeric columns
    if "Total Amount Spent" in df.columns:
        df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)
    if "Leads" in df.columns:
        df["Leads"] = pd.to_numeric(df["Leads"], errors='coerce').fillna(0)
    if "Fronts" in df.columns:
        df["Fronts"] = pd.to_numeric(df["Fronts"], errors='coerce').fillna(0)
    if "Sales" in df.columns:
        df["Sales"] = pd.to_numeric(df["Sales"], errors='coerce').fillna(0)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    return df

df = load_data(csv_url)

# -----------------------------
# Vendors list
# Extract unique vendors from Vendors column
unique_vendors = df["Vendors"].dropna().unique()

# -----------------------------
# Streamlit UI
st.title("Marketing Dashboard")
st.sidebar.header("Filters")
selected_vendors = st.sidebar.multiselect("Select Vendor(s)", options=unique_vendors, default=unique_vendors)
selected_dates = st.sidebar.date_input("Select Date Range", [])

# -----------------------------
# Filter data
df_filtered = df[df["Vendors"].isin(selected_vendors)]
if len(selected_dates) == 2:
    df_filtered = df_filtered[(df_filtered["Date"] >= pd.to_datetime(selected_dates[0])) & 
                              (df_filtered["Date"] <= pd.to_datetime(selected_dates[1]))]

# -----------------------------
# Color map (from your App Script)
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
# Function to determine row color
def get_color(vendor_name):
    match = pd.Series(vendor_name).str.extract(r'\(([^)]+)\)')[0]
    if pd.isna(match[0]):
        return color_map["grey"]
    keyword = match[0].lower()
    for key in color_map.keys():
        if key in keyword:
            return color_map[key]
    return color_map["grey"]

# -----------------------------
# Display table with colors
st.subheader("Matched Report")
def color_rows(row):
    return ["background-color: {}".format(get_color(row["Vendors"]))]*len(row)

st.dataframe(df_filtered.style.apply(color_rows, axis=1))

# -----------------------------
# Totals per vendor
st.subheader("Totals per Vendor")
totals_vendor = df_filtered.groupby("Vendors").agg(
    Leads=("Leads", "sum"),
    TotalSpent=("Total Amount Spent", "sum"),
    Fronts=("Fronts", "sum"),
    Sales=("Sales", "sum")
).reset_index()
totals_vendor["CostPerFront"] = totals_vendor["TotalSpent"] / totals_vendor["Fronts"].replace(0,np.nan)
totals_vendor["CostPerSale"] = totals_vendor["TotalSpent"] / totals_vendor["Sales"].replace(0,np.nan)
st.dataframe(totals_vendor.style.format({"TotalSpent":"${:,.2f}", "CostPerFront":"${:,.2f}", "CostPerSale":"${:,.2f}"}))

# -----------------------------
# Grand totals
st.subheader("Grand Total")
grand_totals = pd.DataFrame({
    "Leads": [totals_vendor["Leads"].sum()],
    "TotalSpent": [totals_vendor["TotalSpent"].sum()],
    "Fronts": [totals_vendor["Fronts"].sum()],
    "Sales": [totals_vendor["Sales"].sum()],
    "CostPerFront": [totals_vendor["TotalSpent"].sum()/totals_vendor["Fronts"].sum() if totals_vendor["Fronts"].sum()>0 else 0],
    "CostPerSale": [totals_vendor["TotalSpent"].sum()/totals_vendor["Sales"].sum() if totals_vendor["Sales"].sum()>0 else 0]
})
st.dataframe(grand_totals.style.format({"TotalSpent":"${:,.2f}", "CostPerFront":"${:,.2f}", "CostPerSale":"${:,.2f}"}))

# -----------------------------
# Graphs
st.subheader("Visualization: Total Spent per Vendor")
fig, ax = plt.subplots(figsize=(10,6))
ax.bar(totals_vendor["Vendors"], totals_vendor["TotalSpent"], color="skyblue")
ax.set_xlabel("Vendors")
ax.set_ylabel("Total Amount Spent")
ax.set_title("Total Spent per Vendor")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)
