import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

# -----------------------------
# 1. Load data from CSV link
# -----------------------------
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # Clean currency/percent columns
    df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)
    df["Cost-Per-Front"] = df["Cost-Per-Front"].replace('[\$,]', '', regex=True).astype(float)
    df["Cost-Per-Sale"] = df["Cost-Per-Sale"].replace('[\$,]', '', regex=True).astype(float)
    df["Contact Rate"] = df["Contact Rate"].replace('[\%]', '', regex=True).astype(float)
    return df

df = load_data(csv_url)

# -----------------------------
# 2. Vendor list (from Source)
# -----------------------------
unique_vendors = df["Source"].unique()

# -----------------------------
# 3. Color mapping by keywords
# -----------------------------
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
# 4. Group by date
# -----------------------------
df["Day(date)"] = pd.to_datetime(df["Day(date)"].str.extract(r'\((.*?)\)')[0], format="%m/%d/%Y")
dates = df["Day(date)"].sort_values().unique()

# -----------------------------
# 5. Streamlit layout
# -----------------------------
st.set_page_config(layout="wide")
st.title("Vendor Matched Report Dashboard")

for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    date_df = df[df["Day(date)"] == date]
    
    all_matched_rows = []

    for vendor in unique_vendors:
        keyword_match = [k for k in color_map.keys() if k in vendor.lower()]
        bg_color = color_map[keyword_match[0]] if keyword_match else color_map["grey"]
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(vendor.lower())]
        if matched_rows.empty:
            continue
        all_matched_rows.append(matched_rows)
        
        # Vendor totals
        num_leads = matched_rows["Number of Leads"].sum()
        total_spent = matched_rows["Total Amount Spent"].sum()
        total_fronts = matched_rows["Fronts"].sum()
        total_sales = matched_rows["Sales"].sum()
        cost_per_front = total_spent / total_fronts if total_fronts > 0 else 0
        cost_per_sale = total_spent / total_sales if total_sales > 0 else 0
        
        st.markdown(f"**Vendor: {vendor}**")
        st.dataframe(matched_rows.style.set_properties(**{'background-color': bg_color}))
        st.markdown(f"**TOTAL ({vendor})**: Leads={num_leads}, Spent=${total_spent:.2f}, Fronts={total_fronts}, Sales={total_sales}, Cost/Front=${cost_per_front:.2f}, Cost/Sale=${cost_per_sale:.2f}")

    # Grand totals for date
    if all_matched_rows:
        all_df = pd.concat(all_matched_rows)
        grand_leads = all_df["Number of Leads"].sum()
        grand_spent = all_df["Total Amount Spent"].sum()
        grand_fronts = all_df["Fronts"].sum()
        grand_sales = all_df["Sales"].sum()
        cost_per_front_all = grand_spent / grand_fronts if grand_fronts > 0 else 0
        cost_per_sale_all = grand_spent / grand_sales if grand_sales > 0 else 0
        st.markdown(f"**GRAND TOTAL ({date.strftime('%A')})**: Leads={grand_leads}, Spent=${grand_spent:.2f}, Fronts={grand_fronts}, Sales={grand_sales}, Cost/Front=${cost_per_front_all:.2f}, Cost/Sale=${cost_per_sale_all:.2f}")
    
    # -----------------------------
    # 6. Graphs
    # -----------------------------
    fig1 = px.bar(date_df, x="Source", y="Number of Leads", color="Source", title="Leads per Vendor")
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.bar(date_df, x="Source", y="Total Amount Spent", color="Source", title="Total Spent per Vendor")
    st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = px.bar(date_df, x="Source", y="Fronts", color="Source", title="Fronts per Vendor")
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.bar(date_df, x="Source", y="Sales", color="Source", title="Sales per Vendor")
    st.plotly_chart(fig4, use_container_width=True)
