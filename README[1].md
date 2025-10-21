# Marketing Dashboard (Streamlit + Google Sheets)

This is a dynamic marketing performance dashboard that pulls read-only data from Google Sheets. Vendor colors are applied dynamically.

## How to deploy on Streamlit Cloud

1. Create a Streamlit Cloud account: https://streamlit.io/cloud
2. Connect your GitHub repository containing this folder.
3. Go to your repository on Streamlit Cloud → Secrets and add your Service Account JSON:
   - Copy all fields from your Service Account JSON into `st.secrets["gcp_service_account"]`
4. Deploy the app.
5. Share the link with your team or boss.
