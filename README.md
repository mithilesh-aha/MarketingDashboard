# Marketing Dashboard (Streamlit)

This project is a Streamlit dashboard that reads data from the **MarketingDashboard** Google Sheet and produces a matched vendor report similar to your Apps Script output.

## Files in this repo
- `app.py` - main Streamlit application
- `requirements.txt` - Python dependencies
- `README.md` - this file

## Before you run
1. Create a Google Cloud Service Account and download the JSON key.
2. Share your Google Sheet with the service account email (Editor or Viewer depending on needs).
3. Do **not** commit your service account JSON to GitHub. Instead, use Streamlit Secrets for deployment.

## Streamlit Secrets (recommended for Streamlit Cloud)
In your Streamlit app settings (Share → Settings → Secrets), add these two keys:

```
[service_account]
# paste the entire JSON contents of the service account file here as JSON (no extra formatting required)
```

and also add:

```
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1WVWnLZpD20DCGPpmTNQyowFXWE3eCRtMtgOAyOqRX9s
```

*(Alternatively, set `spreadsheet_url` to your sheet URL in the Streamlit secrets editor.)*

## Run locally (for testing)
- Place `service_account.json` (downloaded from Google Cloud) in the same folder as `app.py`.
- Install dependencies:
```
pip install -r requirements.txt
```
- Run:
```
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push this repository to GitHub.
2. On Streamlit Cloud, connect your GitHub repo and deploy the app.
3. In Streamlit Cloud → Settings → Secrets, add `service_account` (paste entire JSON) and `spreadsheet_url` (the Google Sheet URL).
4. Click deploy / rerun. The app will read the sheet and show the matched report page.

## Notes
- The app expects two sheets named exactly: `Sheet1` and `Vendors`.
- Column names in `Sheet1` should include a Date column named 'Date' (or common variants). The app attempts to auto-detect common column names for Source, Leads, Spend, Fronts, and Sales.
- If you need Excel export or additional features, open an issue in your repo and update the code accordingly.
