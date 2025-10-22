import pandas as pd
import streamlit as st
import plotly.express as px

# -----------------------------
# 1. Load Data
# -----------------------------
data_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"
vendors_url = data_url  # Assuming vendors are in same sheet; adjust if separate

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)
    df["Day(date_parsed)"] = pd.to_datetime(df["Day(date)"].str.extract(r'\((.*?)\)')[0], errors='coerce')
    return df

df = load_data(data_url)
df = df.dropna(subset=["Day(date_parsed)"])

# Vendors sheet assumed to be column 'Vendors' in same CSV or adjust link
vendors_df = pd.read_csv(vendors_url)
unique_vendors = vendors_df['Vendors'].dropna().unique()

# -----------------------------
# 2. Vendor colors
# -----------------------------
color_map = {
    "darkblue": "#b8cce4", "tangerine": "#ffe699", "mustard": "#fff2cc", "mauve": "#e4dfec",
    "lime": "#d8e4bc", "indigo": "#c5d9f1", "black": "#d9d9d9", "coral": "#f8cbad",
    "violet": "#e6b8b7", "crimson": "#f4b084", "sepia": "#e2c5a3", "lilac": "#d9d2e9",
    "purple": "#d9c3e8", "saffron": "#fce4d6", "grey": "#e7e6e6", "monarch media": "#f2dcdb",
    "pink": "#f4cccc"
}

# -----------------------------
# 3. Streamlit App
# -----------------------------
st.title("Vendor Matched Report Dashboard")

dates = df["Day(date_parsed)"].sort_values().unique()
selected_date = st.date_input("Select Date", value=dates[0])

date_df = df[df["Day(date_parsed)"] == pd.to_datetime(selected_date)]

vendor_filter = st.selectbox("Select Vendor", options=unique_vendors)

st.subheader(f"Vendor: {vendor_filter} ({selected_date.strftime('%A (%m/%d/%Y)')})")

# Extract keyword in parentheses from vendor name
import re
match = re.search(r'\(([^)]+)\)', vendor_filter)
keyword = match.group(1).lower() if match else vendor_filter.lower()
color_key = next((c for c in color_map.keys() if c in keyword), "grey")
bg_color = color_map[color_key]

# Filter campaigns that match this vendor
matched_df = date_df[date_df["Source"].str.lower().str.contains(keyword)]

if not matched_df.empty:
    # Show campaigns
    st.dataframe(matched_df.style.set_properties(**{'background-color': bg_color}))

    # Totals
    num_leads = matched_df["Number of Leads"].sum()
    total_spent = matched_df["Total Amount Spent"].sum()
    total_fronts = matched_df["Fronts"].sum()
    total_sales = matched_df["Sales"].sum()
    cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
    cost_per_sale = total_spent / total_sales if total_sales > 0 else 0

    st.write(f"**Totals for {vendor_filter}:**")
    st.write(f"Leads={num_leads}, Spend=${total_spent:.2f}, Fronts={total_fronts}, Sales={total_sales}, Cost/Front=${cost_per_front:.2f}, Cost/Sale=${cost_per_sale:.2f}")

    # Graphs
    fig = px.bar(
        matched_df,
        x="Source",
        y=["Number of Leads", "Total Amount Spent", "Fronts", "Sales"],
        title=f"Campaign Performance for {vendor_filter} on {selected_date.strftime('%A (%m/%d/%Y)')}"
    )
    st.plotly_chart(fig)
else:
    st.write("No campaigns matched this vendor for the selected date.")
