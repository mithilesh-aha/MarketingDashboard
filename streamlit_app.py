import streamlit as st
import pandas as pd

# -----------------------------
# CSV link (published Google Sheet)
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"

# -----------------------------
# Load data
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # Remove $ and commas in numeric columns
    if "Total Amount Spent" in df.columns:
        df["Total Amount Spent"] = df["Total Amount Spent"].replace('[\$,]', '', regex=True).astype(float)
    return df

df = load_data(csv_url)

# -----------------------------
# Sidebar filters
st.sidebar.header("Filters")
vendors = st.sidebar.multiselect("Select Vendor(s)", options=df["Vendor"].unique(), default=df["Vendor"].unique())
dates = st.sidebar.date_input("Select Date Range", [])

# Filter data
df_filtered = df[df["Vendor"].isin(vendors)]
if len(dates) == 2:
    df_filtered = df_filtered[(pd.to_datetime(df_filtered["Date"]) >= pd.to_datetime(dates[0])) & 
                              (pd.to_datetime(df_filtered["Date"]) <= pd.to_datetime(dates[1]))]

# -----------------------------
# Display table with coloring
st.title("Marketing Dashboard")
st.subheader("Data Table")

def highlight_total(row):
    if row.name % 2 == 0:
        return ["background-color: #f0f0f0"]*len(row)
    else:
        return [""]*len(row)

st.dataframe(df_filtered.style.apply(highlight_total, axis=1))

# -----------------------------
# Totals per vendor
st.subheader("Total Amount Spent per Vendor")
totals = df_filtered.groupby("Vendor")["Total Amount Spent"].sum().reset_index()
st.dataframe(totals)

# -----------------------------
# Grand total
grand_total = df_filtered["Total Amount Spent"].sum()
st.subheader(f"Grand Total: ${grand_total:,.2f}")
