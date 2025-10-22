import streamlit as st
import pandas as pd

# --- CSV Links ---
DATA_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdB51W41oj4PvIGlPlA8O1BpOSfIIMr3U3oLkbKxfAC4LyuSu6xkcAz1_Ze3CzHDuNpkJh12tzLrQy/pub?output=csv"
VENDORS_CSV_URL = DATA_CSV_URL  # Replace with a separate vendors CSV if needed

# --- Load Data ---
df = pd.read_csv(DATA_CSV_URL)
vendors_df = pd.read_csv(VENDORS_CSV_URL)

# Clean Vendors list
vendors_list = vendors_df['Vendors'].dropna().unique()  # Column must be 'Vendors'

# Convert date column to datetime
df['Day(date)'] = pd.to_datetime(df['Day(date)'], errors='coerce')
dates = sorted(df['Day(date)'].dropna().unique())

# --- Color mapping (like your AppScript) ---
color_map = {
    'darkblue': '#b8cce4',
    'tangerine': '#ffe699',
    'mustard': '#fff2cc',
    'mauve': '#e4dfec',
    'lime': '#d8e4bc',
    'indigo': '#c5d9f1',
    'black': '#d9d9d9',
    'coral': '#f8cbad',
    'violet': '#e6b8b7',
    'crimson': '#f4b084',
    'sepia': '#e2c5a3',
    'lilac': '#d9d2e9',
    'purple': '#d9c3e8',
    'saffron': '#fce4d6',
    'grey': '#e7e6e6',
    'monarch media': '#f2dcdb',
    'pink': '#f4cccc'
}

st.title("Vendor Matched Report Dashboard")

for date in dates:
    date_str = pd.to_datetime(date).strftime('%A (%m/%d/%Y)')
    st.subheader(f"📅 {date_str}")
    
    date_df = df[df['Day(date)'] == date]
    all_matched_rows = []

    for vendor_name in vendors_list:
        # Extract keyword from vendor name (inside parentheses)
        if '(' in vendor_name and ')' in vendor_name:
            keyword = vendor_name.split('(')[-1].replace(')', '').lower()
        else:
            keyword = vendor_name.lower()
        
        # Match rows for this vendor
        matched_rows = date_df[date_df['Source Name (Vendors)'].str.lower().str.contains(keyword, na=False)]
        if matched_rows.empty:
            continue
        
        all_matched_rows.append(matched_rows)
        
        # Determine background color
        bg_color = '#e7e6e6'  # default grey
        for k, v in color_map.items():
            if k in keyword:
                bg_color = v
                break
        
        # Display each matched row
        for idx, row in matched_rows.iterrows():
            st.markdown(
                f"<div style='background-color:{bg_color}; padding:5px; border-radius:4px;'>"
                f"{row['Source Name (Vendors)']} | {row['Matched Vendor']} | {row['Number of Leads']} | "
                f"{row['Total Amount Spent']} | {row['Fronts']} | {row['Sales']} | {row['Contact Rate']} | "
                f"{row['Cost-Per-Front']} | {row['Cost-Per-Sale']}</div>", unsafe_allow_html=True
            )
        
        # Totals per vendor
        total_leads = matched_rows['Number of Leads'].sum()
        total_spent = matched_rows['Total Amount Spent'].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = matched_rows['Fronts'].sum()
        total_sales = matched_rows['Sales'].sum()
        cost_per_front = total_spent / total_fronts if total_fronts else 0
        cost_per_sale = total_spent / total_sales if total_sales else 0

        st.markdown(
            f"<b>TOTAL ({vendor_name.split('(')[-1].replace(')', '')})</b> | | {total_leads} | "
            f"${total_spent:.2f} | {total_fronts} | {total_sales} | | "
            f"${cost_per_front:.2f} | ${cost_per_sale:.2f}", unsafe_allow_html=True
        )
        st.write("")  # blank line
    
    # Grand totals for the date
    if all_matched_rows:
        grand_total_df = pd.concat(all_matched_rows)
        total_leads = grand_total_df['Number of Leads'].sum()
        total_spent = grand_total_df['Total Amount Spent'].replace('[\$,]', '', regex=True).astype(float).sum()
        total_fronts = grand_total_df['Fronts'].sum()
        total_sales = grand_total_df['Sales'].sum()
        cost_per_front = total_spent / total_fronts if total_fronts else 0
        cost_per_sale = total_spent / total_sales if total_sales else 0

        st.markdown(
            f"<b>GRAND TOTAL ({date_str})</b> | | {total_leads} | ${total_spent:.2f} | "
            f"{total_fronts} | {total_sales} | | ${cost_per_front:.2f} | ${cost_per_sale:.2f}", unsafe_allow_html=True
        )
    
    st.markdown("---")  # separator between dates
