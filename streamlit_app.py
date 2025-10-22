import streamlit as st
import pandas as pd
import re

st.title("Vendor Matched Report Dashboard")

# URLs
SHEET1_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"

# Read main sheet
df = pd.read_csv(SHEET1_URL)
st.write("**Sheet1 Preview:**")
st.dataframe(df.head())

# Make sure 'Day(date)' is datetime
df["Day(date)"] = pd.to_datetime(df["Day(date)"], errors="coerce")
df = df.dropna(subset=["Day(date)"])

# Extract unique dates
dates = df["Day(date)"].sort_values().unique()

# Vendors list (from Sheet1 or separate Vendors sheet)
vendors = [
    "Black (black)",
    "Darkblue (darkblue)",
    "Mauve (mauve)",
    "Lime (lime)",
    "Indigo (indigo)",
    "Tangerine (tangerine)",
    "Coral (coral)",
    "Grey (grey)",
    "Pink (pink)"
]

# Color map
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

# Loop through dates
for date in dates:
    st.subheader(f"📅 {date.strftime('%A (%m/%d/%Y)')}")
    date_df = df[df["Day(date)"] == date]
    
    for vendor_name in vendors:
        match = re.search(r"\(([^)]+)\)", vendor_name)
        if not match:
            continue
        keyword = match.group(1).lower()
        bg_color = color_map.get(keyword, "#e7e6e6")
        
        # Debug: show which rows are being matched
        matched_rows = date_df[date_df["Source"].str.lower().str.contains(keyword, na=False)]
        st.write(f"Vendor: {vendor_name} | Keyword: {keyword} | Matched Rows: {len(matched_rows)}")
        
        if not matched_rows.empty:
            st.dataframe(matched_rows.style.set_properties(**{"background-color": bg_color}))
        else:
            st.write(f"No matches found for vendor {vendor_name} on this date.")
