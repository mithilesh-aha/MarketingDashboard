import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

try:
    creds = Credentials.from_service_account_info(
        st.secrets["service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet_url = st.secrets["spreadsheet_url"]
    spreadsheet = client.open_by_url(sheet_url)
    st.success("✅ Connected successfully to Google Sheet!")
    st.write("Sheets found:", [s.title for s in spreadsheet.worksheets()])
except Exception as e:
    st.error(f"❌ Could not open spreadsheet: {e}")
